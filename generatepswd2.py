import bcrypt

password = b"PsT_36"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed)
print(hashed.decode())