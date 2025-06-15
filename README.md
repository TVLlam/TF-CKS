# 🔐 SecureFileShare: Web Truyền File Dữ Liệu Có Ký Số

<p>Dự án xây dựng một hệ thống web toàn diện, cho phép người dùng <strong>tải lên, chia sẻ và tải xuống file</strong> một cách an toàn, kèm theo tính năng <strong>kiểm tra tính toàn vẹn dữ liệu và xác thực nguồn gốc</strong> sử dụng <strong>chữ ký số RSA</strong>. Hệ thống đảm bảo rằng file không bị thay đổi hoặc hỏng hóc trong suốt quá trình truyền tải và lưu trữ, đồng thời xác nhận rằng file thực sự đến từ người gửi đã ký.</p>

<h2> Mục tiêu chính</h2>
<ul>
    <li>Cung cấp một nền tảng an toàn để người dùng <strong>đăng ký, đăng nhập và quản lý phiên</strong> truy cập.</li>
    <li>Cho phép người dùng <strong>tải lên file</strong> và lưu trữ trên máy chủ.</li>
    <li>Triển khai chức năng <strong>chia sẻ file giữa các người dùng</strong> đã đăng ký.</li>
    <li>Đảm bảo <strong>tính toàn vẹn và xác thực nguồn gốc của file</strong> bằng cách sử dụng <strong>chữ ký số RSA</strong>:
        <ul>
            <li>Mỗi người dùng được tạo một cặp khóa riêng tư/công khai khi đăng ký.</li>
            <li>File được ký số bằng khóa riêng tư của người gửi khi upload lên hệ thống.</li>
            <li>Khi download, hệ thống sẽ xác minh chữ ký số bằng khóa công khai của người gửi để đảm bảo file không bị thay đổi.</li>
        </ul>
    </li>
    <li>Phát triển giao diện Web <strong>chuyên nghiệp, thân thiện và trực quan</strong>, bao gồm một trang đăng nhập/đăng ký riêng biệt và giao diện ứng dụng chính với các hiệu ứng mượt mà.</li>
</ul>

<h2>📁 Cấu trúc dự án</h2>
<ul>
    <li><code>app.py</code>: Backend Python sử dụng Flask, xử lý các logic chính (xác thực người dùng, quản lý file, chia sẻ file, tạo/xác minh chữ ký số), tương tác với cơ sở dữ liệu (SQLAlchemy).</li>
    <li><code>generate_keys.py</code>: Script Python để tạo cặp khóa riêng tư/công khai RSA cho người dùng.</li>
    <li><code>requirements.txt</code>: Danh sách các thư viện Python cần thiết cho backend (Flask, SQLAlchemy, Flask-Login, Cryptography, v.v.).</li>
    <li><code>.env</code>: File cấu hình môi trường (SECRET_KEY, DATABASE_URL).</li>
    <li><code>site.db</code>: Cơ sở dữ liệu SQLite (tự động tạo khi chạy server lần đầu) để lưu trữ thông tin người dùng và metadata của file.</li>
    <li><code>static/</code>: Thư mục chứa các tài nguyên tĩnh (CSS, JS, hình ảnh, file đã tải lên).
        <ul>
            <li><code>static/assets/</code>: Thư mục chứa logo và các hình ảnh giao diện.</li>
            <li><code>static/uploads/</code>: Thư mục để lưu trữ các file đã được người dùng tải lên.</li>
            <li><code>static/style.css</code>: Tệp CSS tùy chỉnh để làm đẹp giao diện.</li>
            <li><code>static/script.js</code>: Logic JavaScript cho các hiệu ứng giao diện và tương tác.</li>
        </ul>
    </li>
    <li><code>templates/</code>: Thư mục chứa các file HTML templates (Flask Jinja2).
        <ul>
            <li><code>base.html</code>: Layout cơ sở chung cho toàn bộ trang web.</li>
            <li><code>index.html</code>: Trang chào mừng/giới thiệu.</li>
            <li><code>login.html</code>: Trang đăng nhập.</li>
            <li><code>register.html</code>: Trang đăng ký.</li>
            <li><code>dashboard.html</code>: Giao diện chính của ứng dụng sau khi đăng nhập.</li>
            <li><code>my_files_uploaded.html</code>: Trang chi tiết các file đã tải lên.</li>
            <li><code>my_files_sent.html</code>: Trang chi tiết các file đã gửi.</li>
            <li><code>my_files_received.html</code>: Trang chi tiết các file đã nhận.</li>
        </ul>
    </li>
</ul>

<h2>🖼️ Giao diện người dùng</h2>
<p>Dự án được thiết kế với giao diện hiện đại, tối giản và thân thiện, đảm bảo trải nghiệm người dùng mượt mà qua từng thao tác.</p>

### Trang Đăng nhập / Đăng ký
<img src="Screenshot 2025-06-15 184855.png" alt="Login Interface" width="600">
<br>
*Giao diện đăng nhập và đăng ký chuyên nghiệp, với khả năng chuyển đổi giữa hai form.*
*(Bạn cần thay thế "login_interface.png" bằng ảnh chụp màn hình thực tế của bạn, ví dụ: "Screenshot 2025-06-04 155648.png" nếu đó là ảnh của bạn)*

### Trang ứng dụng chính (Dashboard)
<img src="static/assets/main_app_dashboard.png" alt="Main App Interface" width="800">
<br>
*Giao diện chính của ứng dụng (Dashboard), hiển thị các phần quản lý file, chia sẻ và tải xuống.*
*(Bạn cần thay thế "main_app_dashboard.png" bằng ảnh chụp màn hình thực tế của bạn, ví dụ: "Screenshot 2025-06-04 155711.png")*

### Tính năng tải lên và chia sẻ file
<img src="static/assets/upload_share_feature.png" alt="Upload and Share Feature" width="800">
<br>
*Khu vực tải file lên và tùy chọn chia sẻ file đã tải lên với người dùng khác trong hệ thống, bao gồm modal gửi file.*
*(Bạn cần thay thế "upload_share_feature.png" bằng ảnh chụp màn hình thực tế của bạn, ví dụ: "Screenshot 2025-06-04 160020.png")*

### Kiểm tra tính toàn vẹn và xác thực bằng chữ ký số khi tải xuống
<img src="static/assets/download_verify_signature.png" alt="Download and Signature Verification" width="800">
<br>
*Quá trình tải xuống file kèm theo kiểm tra chữ ký số để xác minh tính nguyên vẹn của dữ liệu và nguồn gốc file.*
*(Bạn cần chụp ảnh màn hình hiển thị thông báo xác minh chữ ký sau khi tải xuống và thay thế "download_verify_signature.png")*

<h2>🚀 Hướng dẫn chạy ứng dụng</h2>

<p>Để cài đặt và chạy ứng dụng trên máy cục bộ, bạn cần đảm bảo đã cài đặt Python 3.8+ và pip.</p>

<pre>
# 1. Clone repository
git clone https://github.com/TVLlam/SHA_TRUYEN_FILE.git
# Hoặc tải file zip từ GitHub/nguồn khác nếu bạn không dùng Git

# 2. Di chuyển vào thư mục dự án (nơi có app.py, requirements.txt)
cd SecureFileShare # Thay đổi nếu tên thư mục của bạn khác

# 3. Tạo và kích hoạt môi trường ảo
python -m venv venv
# Trên Windows:
.\venv\Scripts\activate
# Trên macOS/Linux:
source venv/bin/activate

# 4. Cài đặt các thư viện Python
pip install -r requirements.txt

# 5. Tạo file '.env'
# Trong thư mục gốc của dự án, tạo file .env và dán nội dung sau.
# THAY ĐỔI 'your_super_secret_key...' bằng một chuỗi ngẫu nhiên dài và phức tạp!
# SECRET_KEY được dùng cho bảo mật Flask (sessions, v.v.)
# DATABASE_URL chỉ định sử dụng SQLite với file site.db
# Ví dụ nội dung file .env:
# SECRET_KEY=your_super_secret_key_that_is_very_long_and_random_and_unique_for_production
# DATABASE_URL=sqlite:///site.db

# 6. Đảm bảo các thư mục cần thiết tồn tại (server sẽ tạo nếu chưa có)
# mkdir static\uploads  # Tự động tạo bởi app.py nếu chưa có

# 7. Chạy server Flask
python app.py
</pre>

<p>Sau khi server khởi động thành công, mở trình duyệt và truy cập:</p>
<pre>
http://127.0.0.1:5000/
</pre>
*Ứng dụng sẽ tự động chuyển hướng đến trang Đăng nhập/Đăng ký.*

<h2>🔧 Cách sử dụng</h2>
<ol>
    <li><strong>Truy cập ứng dụng:</strong> Mở trình duyệt và truy cập <code>http://127.0.0.1:5000/</code>. Bạn sẽ được đưa đến trang Đăng nhập/Đăng ký.</li>
    <li><strong>Đăng ký tài khoản mới:</strong> Nếu chưa có tài khoản, nhấp vào "Đăng ký" và điền thông tin. Hệ thống sẽ tự động tạo một cặp khóa riêng tư/công khai cho bạn.</li>
    <li><strong>Đăng nhập:</strong> Sau khi đăng ký hoặc nếu đã có tài khoản, sử dụng tên người dùng và mật khẩu để đăng nhập. Bạn sẽ được chuyển hướng đến Dashboard.</li>
    <li><strong>Tải lên file:</strong> Trên Dashboard, trong phần "Tải lên File mới", chọn tệp từ máy tính của bạn và nhấn "Tải lên & Ký số". File sẽ được ký số bằng khóa riêng tư của bạn và lưu trữ.</li>
    <li><strong>Chia sẻ file:</strong> Trong phần "File đã tải lên của tôi", nhấp vào nút "Gửi" bên cạnh file bạn muốn chia sẻ. Một modal sẽ hiện ra cho phép bạn chọn người nhận từ danh sách người dùng đã đăng ký. Nhấn "Gửi file".</li>
    <li><strong>Tải xuống & Kiểm tra tính toàn vẹn/xác thực:</strong>
        <ul>
            <li>Trên Dashboard, trong phần "File đã nhận", bạn sẽ thấy các file được chia sẻ với bạn.</li>
            <li>Nhấp vào "Tải xuống & Xác minh" bên cạnh file.</li>
            <li>Hệ thống sẽ tải file và tự động xác minh chữ ký số bằng khóa công khai của người gửi. Một thông báo sẽ hiện ra cho biết chữ ký là HỢP LỆ (file nguyên vẹn) hay KHÔNG HỢP LỆ (file đã bị thay đổi).</li>
        </ul>
    </li>
</ol>

<h2>🧑‍💻 Tác giả</h2>

* **[Tên của bạn]**: [Liên kết đến GitHub/LinkedIn/Portfolio của bạn]

<h2>📧 Liên hệ</h2>

Nếu có bất kỳ câu hỏi hoặc góp ý nào về dự án, vui lòng liên hệ:

* **Email:** your.email@example.com
* **GitHub:** [https://github.com/your-github-profile](https://github.com/your-github-profile)

<h2>📄 Bản quyền / Giấy phép (License)</h2>

Dự án này được cấp phép theo Giấy phép MIT. Vui lòng xem file [LICENSE](LICENSE) để biết thêm chi tiết.
