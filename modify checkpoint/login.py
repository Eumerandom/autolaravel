import mysql.connector
import hashlib
import re

# menghubungkan ke database untuk menyimpan data user
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="parastream_adm",
        password="paraSTREAM",
        database="auth_db"
    )

# autentikasi login user
def authenticate_user(email, password):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, hashed_password))
    user = cursor.fetchone()
    db.close()
    return user

# registrasi user
def register_user(full_name, email, password):
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$", email):
        return "Email tidak valid!"
    db = connect_db()
    cursor = db.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)", (full_name, email, hashed_password))
        db.commit()
        return True
    except mysql.connector.IntegrityError:
        return "Email sudah digunakan!"
    finally:
        db.close()