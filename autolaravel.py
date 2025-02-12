import streamlit as st
import mysql.connector
import hashlib
import paramiko

# Fungsi untuk menghubungkan ke database MySQL
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="parastream_adm",
        password="paraSTREAM",
        database="auth_db"
    )

# Fungsi untuk mengautentikasi pengguna saat login
def authenticate_user(username, password):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, hashed_password))
    user = cursor.fetchone()
    db.close()
    return user

# Fungsi untuk mendaftarkan pengguna baru
def register_user(full_name, username, password):
    db = connect_db()
    cursor = db.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO users (full_name, username, password) VALUES (%s, %s, %s)", (full_name, username, hashed_password))
        db.commit()
        db.close()
        return True
    except mysql.connector.IntegrityError:
        db.close()
        return False

# Fungsi untuk menginstal Laravel di server menggunakan SSH
def install_laravel_on_server(host, user, password, project_name):
    commands = [
        "sudo apt update && sudo apt upgrade -y",
        "sudo apt install -y apache2 php php-cli php-mbstring unzip curl php-xml composer",
        f"cd /var/www && composer create-project --prefer-dist laravel/laravel {project_name}",
        f"sudo chown -R www-data:www-data /var/www/{project_name}",
        f"sudo chmod -R 775 /var/www/{project_name}/storage /var/www/{project_name}/bootstrap/cache",
        "sudo systemctl restart apache2"
    ]
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=password)
        output_log = []
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            output_log.append(stdout.read().decode())
            output_log.append(stderr.read().decode())
        ssh.close()
        return "\n".join(output_log)
    except Exception as e:
        return f"Error: {e}"

# Tampilan utama aplikasi Streamlit
st.title("Automasi Instalasi Laravel")
st.divider()

# Mengatur status autentikasi pengguna
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Jika belum login, tampilkan form login dan register
if not st.session_state["authenticated"]:
    full_name = st.text_input("Nama Lengkap")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Login"):
            user = authenticate_user(username, password)
            if user:
                st.success(f"Selamat datang, {user['full_name']}!")
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Username atau password salah!")
    
    with col2:
        if st.button("Register"):
            if register_user(full_name, username, password):
                st.success("Registrasi berhasil! Silakan login.")
            else:
                st.error("Username sudah digunakan!")

# Jika sudah login, tampilkan form untuk instalasi Laravel
if st.session_state["authenticated"]:
    st.subheader("Tentukan lokasi server")
    server_ip = st.text_input("IP Server", placeholder="192.168.1.100")
    server_user = st.text_input("Username SSH", value="root")
    server_password = st.text_input("Password SSH", type="password")
    project_name = st.text_input("Nama Project Laravel", "my-laravel-project")
    
    if st.button("Install Laravel"):
        if server_ip.strip() and server_user.strip() and server_password.strip() and project_name.strip():
            st.success(f"Memulai instalasi Laravel di {server_ip}...")
            log = install_laravel_on_server(server_ip, server_user, server_password, project_name)
            st.text_area("Log Instalasi", log, height=300)
        else:
            st.error("Semua field harus diisi!")
