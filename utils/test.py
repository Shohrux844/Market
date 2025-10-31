import bcrypt

print(bcrypt.hashpw("1234".encode(), salt=bcrypt.gensalt()))
#
#
# # Parol va hash
# plain_password = b"12345"  # yoki real parolingiz
# hashed_password = b'$2b$12$0rTLdsSlAjcjvyRRoSKKQOAVRPro92XFO4VrePUZpAGLBPBC8QQPe'
#
# # Tekshirish
# is_valid = bcrypt.checkpw(plain_password, hashed_password)
#
# print(is_valid)

# import secrets
# secret_key = secrets.token_urlsafe(32)
# print(secret_key)