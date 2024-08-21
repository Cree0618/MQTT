import bcrypt

password = b"PsT_sidla"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed.decode())