from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

plain = "010-2061-3849"
encrypted = cipher.encrypt(plain.encode())
decrypted = cipher.decrypt(encrypted)
print(encrypted)
print(encrypted.decode())
print(decrypted)
print(decrypted.decode())
print("암호문 길이:", len(encrypted.decode())) 