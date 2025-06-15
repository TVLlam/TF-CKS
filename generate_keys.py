# generate_keys.py
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_key_pair():
    # Tạo khóa riêng tư RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048, # Kích thước khóa 2048-bit là đủ an toàn
    )

    # Lấy khóa công khai từ khóa riêng tư
    public_key = private_key.public_key()

    # Chuyển đổi khóa riêng tư sang định dạng PEM
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption() # Không mã hóa khóa riêng tư trong ví dụ này (cho đơn giản)
                                                          # Trong thực tế, bạn nên mã hóa nó với một mật khẩu.
    )

    # Chuyển đổi khóa công khai sang định dạng PEM
    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return pem_private_key.decode('utf-8'), pem_public_key.decode('utf-8')

if __name__ == '__main__':
    # Ví dụ cách sử dụng
    private_key_str, public_key_str = generate_key_pair()
    print("--- Private Key ---")
    print(private_key_str)
    print("\n--- Public Key ---")
    print(public_key_str)

    # Lưu ý: Trong ứng dụng thực tế, bạn sẽ lưu các khóa này vào cơ sở dữ liệu cho người dùng cụ thể
    # hoặc quản lý chúng một cách an toàn hơn.