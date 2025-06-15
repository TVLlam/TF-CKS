import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- Cấu hình ứng dụng ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key_here') # Thay đổi secret key mạnh hơn trong production
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads' # Thư mục để lưu trữ file tải lên

# Đảm bảo thư mục upload tồn tại
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Khởi tạo Extensions ---
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Định nghĩa view cho việc đăng nhập khi chưa đăng nhập

# --- Database Models ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Khóa công khai và khóa riêng tư được lưu dưới dạng chuỗi PEM
    # LƯU Ý QUAN TRỌNG: Lưu khóa riêng tư trên server là rủi ro bảo mật.
    # Trong môi trường production, khóa riêng tư nên được người dùng tự quản lý (client-side)
    # hoặc được bảo vệ nghiêm ngặt bằng các giải pháp HSM/mã hóa mạnh mẽ.
    public_key = db.Column(db.Text, nullable=False) 
    private_key = db.Column(db.Text, nullable=True) 

    files_uploaded = db.relationship('File', backref='uploader', lazy=True)
    files_sent = db.relationship('FileTransaction', foreign_keys='FileTransaction.sender_id', backref='sender', lazy=True)
    files_received = db.relationship('FileTransaction', foreign_keys='FileTransaction.receiver_id', backref='receiver', lazy=True)

    def set_password(self, password):
        """Hash mật khẩu và lưu vào database."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Kiểm tra mật khẩu nhập vào với mật khẩu đã hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False) # Tên file được lưu trên server (đã được làm an toàn)
    original_filename = db.Column(db.String(255), nullable=False) # Tên file gốc do người dùng tải lên
    filepath = db.Column(db.String(255), nullable=False) # Đường dẫn tương đối đến file trên server
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp_uploaded = db.Column(db.DateTime, default=datetime.utcnow)
    digital_signature = db.Column(db.LargeBinary, nullable=False) # Chữ ký số của file

    transactions = db.relationship('FileTransaction', backref='file_info', lazy=True)

    def __repr__(self):
        return f'<File {self.filename}>'

class FileTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp_sent = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='sent') # Ví dụ: 'sent', 'received', 'viewed'

    def __repr__(self):
        return f'<FileTransaction {self.sender_id} -> {self.receiver_id} File:{self.file_id}>'

# --- Flask-Login User Loader ---
@login_manager.user_loader
def load_user(user_id):
    """Callback được sử dụng bởi Flask-Login để tải người dùng."""
    return User.query.get(int(user_id))

# --- Helper Functions for Cryptography ---
# Import hàm tạo khóa từ script generate_keys.py
# Đảm bảo file generate_keys.py nằm cùng cấp với app.py
from generate_keys import generate_key_pair 

def sign_file(file_content, private_key_pem):
    """
    Ký số nội dung file bằng khóa riêng tư của người gửi.
    file_content: Nội dung byte của file cần ký.
    private_key_pem: Chuỗi PEM của khóa riêng tư dùng để ký.
    """
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None # Sử dụng password nếu khóa riêng tư được mã hóa
    )
    
    # Thực hiện ký số bằng phương thức sign()
    signature = private_key.sign(
        file_content, # Dữ liệu cần ký (dạng bytes)
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH # PSS.MAX_LENGTH sử dụng độ dài salt tối đa
        ),
        hashes.SHA256() # Thuật toán băm được sử dụng trước khi ký
    )
    return signature

def verify_signature(file_content, signature, public_key_pem):
    """
    Xác minh chữ ký số của nội dung file bằng khóa công khai của người gửi.
    file_content: Nội dung byte của file cần xác minh.
    signature: Chữ ký số cần xác minh (dạng bytes).
    public_key_pem: Chuỗi PEM của khóa công khai dùng để xác minh.
    """
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode('utf-8')
    )
    
    # Thực hiện xác minh chữ ký bằng phương thức verify()
    try:
        public_key.verify(
            signature,
            file_content, # Dữ liệu gốc đã được ký
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256() # Thuật toán băm được sử dụng trong quá trình ký
        )
        return True # Chữ ký hợp lệ
    except InvalidSignature:
        return False # Chữ ký không hợp lệ (file có thể đã bị thay đổi)
    except Exception as e:
        # Xử lý các lỗi khác có thể xảy ra trong quá trình xác minh (ví dụ: khóa không hợp lệ)
        print(f"Lỗi khi xác minh chữ ký: {e}")
        return False

# --- Routes (Đường dẫn URL) ---

@app.route('/')
def index():
    """Trang chủ, chuyển hướng đến dashboard nếu đã đăng nhập."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Xử lý đăng ký tài khoản người dùng mới."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Tên người dùng đã tồn tại. Vui lòng chọn tên khác.', 'danger')
            return redirect(url_for('register'))

        # Tạo cặp khóa RSA mới cho người dùng
        try:
            private_key_pem, public_key_pem = generate_key_pair()
        except Exception as e:
            flash(f'Lỗi khi tạo cặp khóa: {e}. Vui lòng thử lại.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, public_key=public_key_pem, private_key=private_key_pem)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Xử lý đăng nhập người dùng."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Xử lý đăng xuất người dùng."""
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Trang dashboard hiển thị các file, giao dịch, và tùy chọn gửi/nhận."""
    # Lấy các file đã tải lên bởi người dùng hiện tại
    my_uploaded_files = File.query.filter_by(uploader_id=current_user.id).order_by(File.timestamp_uploaded.desc()).all()

    # Lấy các giao dịch gửi đi của người dùng hiện tại
    sent_transactions = FileTransaction.query.filter_by(sender_id=current_user.id).order_by(FileTransaction.timestamp_sent.desc()).all()

    # Lấy các giao dịch nhận được của người dùng hiện tại
    received_transactions = FileTransaction.query.filter_by(receiver_id=current_user.id).order_by(FileTransaction.timestamp_sent.desc()).all()

    # Lấy danh sách tất cả người dùng để gửi file (trừ người dùng hiện tại)
    all_users = User.query.filter(User.id != current_user.id).all() 

    return render_template(
        'dashboard.html',
        uploaded_files=my_uploaded_files,
        sent_transactions=sent_transactions,
        received_transactions=received_transactions,
        all_users=all_users
    )

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Xử lý việc tải lên file, ký số và lưu vào database."""
    if 'file' not in request.files:
        flash('Không có phần file trong request', 'danger')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('Không có file được chọn', 'danger')
        return redirect(request.url)

    if file:
        original_filename = secure_filename(file.filename)
        # Tạo tên file duy nhất để tránh trùng lặp khi lưu trên server
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{original_filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Đọc nội dung file để ký số.
        # file.read() sẽ di chuyển con trỏ. Cần file.seek(0) để đưa con trỏ về đầu trước khi lưu file.
        file_content = file.read()
        file.seek(0) 

        # Lấy khóa riêng tư của người dùng hiện tại để ký số
        private_key_pem = current_user.private_key
        if not private_key_pem:
            flash('Không tìm thấy khóa riêng tư của bạn. Vui lòng liên hệ quản trị viên.', 'danger')
            return redirect(url_for('dashboard'))

        try:
            digital_signature = sign_file(file_content, private_key_pem)
        except Exception as e:
            flash(f'Lỗi khi ký số file: {e}', 'danger')
            # In lỗi chi tiết ra console để debug
            print(f"Error during signing: {e}") 
            return redirect(url_for('dashboard'))

        # Lưu file vào thư mục UPLOAD_FOLDER
        file.save(filepath)

        # Lưu thông tin file vào CSDL
        new_file = File(
            filename=filename,
            original_filename=original_filename,
            filepath=filepath,
            uploader_id=current_user.id,
            digital_signature=digital_signature
        )
        db.session.add(new_file)
        db.session.commit()
        flash('File đã được tải lên và ký số thành công!', 'success')
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

@app.route('/send/<int:file_id>', methods=['POST'])
@login_required
def send_file(file_id):
    """Xử lý việc gửi file từ người gửi đến người nhận."""
    receiver_id = request.form['receiver_id']
    file_to_send = File.query.get_or_404(file_id)
    receiver = User.query.get_or_404(receiver_id)

    # Đảm bảo người dùng hiện tại là chủ sở hữu của file này
    if file_to_send.uploader_id != current_user.id:
        flash('Bạn không có quyền gửi file này.', 'danger')
        return redirect(url_for('dashboard'))

    # Không cho phép gửi file cho chính mình
    if int(receiver_id) == current_user.id:
        flash('Bạn không thể gửi file cho chính mình.', 'warning')
        return redirect(url_for('dashboard'))

    # Kiểm tra xem giao dịch đã tồn tại chưa để tránh trùng lặp
    existing_transaction = FileTransaction.query.filter_by(
        file_id=file_id,
        sender_id=current_user.id,
        receiver_id=receiver_id
    ).first()

    if existing_transaction:
        flash(f'File "{file_to_send.original_filename}" đã được gửi cho {receiver.username} trước đó.', 'info')
        return redirect(url_for('dashboard'))

    # Tạo bản ghi giao dịch mới
    new_transaction = FileTransaction(
        file_id=file_id,
        sender_id=current_user.id,
        receiver_id=receiver_id
    )
    db.session.add(new_transaction)
    db.session.commit()
    flash(f'File "{file_to_send.original_filename}" đã được gửi thành công cho {receiver.username}.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/download/<int:transaction_id>')
@login_required
def download_file(transaction_id):
    """Xử lý việc tải xuống file và xác minh chữ ký số."""
    transaction = FileTransaction.query.get_or_404(transaction_id)

    # Đảm bảo người dùng hiện tại là người nhận của giao dịch này
    if transaction.receiver_id != current_user.id:
        flash('Bạn không có quyền tải xuống file này.', 'danger')
        return redirect(url_for('dashboard'))

    file_to_download = File.query.get_or_404(transaction.file_id)
    uploader = User.query.get_or_404(file_to_download.uploader_id) # Người đã tải lên file gốc

    # Đường dẫn tuyệt đối đến file trên hệ thống
    full_filepath = os.path.join(current_app.root_path, file_to_download.filepath)

    if not os.path.exists(full_filepath):
        flash('File không tồn tại trên server.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        # Đọc nội dung file để xác minh
        with open(full_filepath, 'rb') as f:
            file_content = f.read()

        # Lấy khóa công khai của người tải lên (người đã ký file) để xác minh chữ ký
        uploader_public_key = uploader.public_key

        # Xác minh chữ ký số
        is_valid = verify_signature(file_content, file_to_download.digital_signature, uploader_public_key)

        if is_valid:
            flash(f'Tải xuống thành công! Chữ ký số của file "{file_to_download.original_filename}" là HỢP LỆ.', 'success')
        else:
            flash(f'Tải xuống thành công! Chữ ký số của file "{file_to_download.original_filename}" KHÔNG HỢP LỆ. File có thể đã bị thay đổi.', 'warning')

        # Gửi file cho người dùng để tải về
        return send_from_directory(
            directory=os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER']),
            path=file_to_download.filename,
            as_attachment=True,
            download_name=file_to_download.original_filename # Tên file khi tải về máy người dùng
        )
    except Exception as e:
        flash(f'Lỗi khi tải xuống hoặc xác minh file: {e}', 'danger')
        # In lỗi chi tiết ra console để debug
        print(f"Error during download or verification: {e}")
        return redirect(url_for('dashboard'))

@app.route('/my_files_uploaded')
@login_required
def my_files_uploaded():
    """Trang hiển thị tất cả các file người dùng hiện tại đã tải lên."""
    my_uploaded_files = File.query.filter_by(uploader_id=current_user.id).order_by(File.timestamp_uploaded.desc()).all()
    # Cần lấy tất cả người dùng để hiển thị tùy chọn gửi file trong modal trên trang này
    all_users = User.query.filter(User.id != current_user.id).all() 
    return render_template('my_files_uploaded.html', uploaded_files=my_uploaded_files, all_users=all_users)

@app.route('/my_files_sent')
@login_required
def my_files_sent():
    """Trang hiển thị tất cả các file người dùng hiện tại đã gửi."""
    sent_transactions = FileTransaction.query.filter_by(sender_id=current_user.id).order_by(FileTransaction.timestamp_sent.desc()).all()
    return render_template('my_files_sent.html', sent_transactions=sent_transactions)

@app.route('/my_files_received')
@login_required
def my_files_received():
    """Trang hiển thị tất cả các file người dùng hiện tại đã nhận."""
    received_transactions = FileTransaction.query.filter_by(receiver_id=current_user.id).order_by(FileTransaction.timestamp_sent.desc()).all()
    return render_template('my_files_received.html', received_transactions=received_transactions)

# --- Khởi động ứng dụng ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Tạo bảng trong database nếu chưa tồn tại. Chỉ chạy lần đầu.
                        # Nếu bạn đã có dữ liệu, KHÔNG NÊN chạy lại lệnh này trực tiếp
                        # vì nó có thể ghi đè/làm mất dữ liệu nếu bạn không cẩn thận
                        # (Tuy nhiên với SQLite, nó thường chỉ tạo nếu file db chưa tồn tại)
    app.run(debug=True) # debug=True sẽ tự động reload server khi có thay đổi code và hiển thị lỗi chi tiết