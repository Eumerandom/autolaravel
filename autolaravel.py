import streamlit as st
import mysql.connector
import hashlib
import paramiko

def connect_db():
    # Fungsi untuk menghubungkan ke database MySQL
    return mysql.connector.connect(
        host="localhost",
        user="parastream_adm",
        password="paraSTREAM",
        database="auth_db"
    )

def authenticate_user(username, password):
    # Fungsi untuk memverifikasi kredensial pengguna
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, hashed_password))
    user = cursor.fetchone()
    db.close()
    return user

def register_user(full_name, username, password):
    # Fungsi untuk mendaftarkan pengguna baru
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

def install_laravel_on_server(host, user, password, project_name):
    # Fungsi untuk menginstal Laravel, mengatur VirtualHost, dan membuat database
    db_name = f"{project_name}_db"
    db_user = f"{project_name}_user"
    db_password = f"pass_{project_name}*"
    commands = [
        "sudo apt update && sudo apt upgrade -y",
        "sudo apt install -y apache2 php php-cli php-mbstring unzip curl php-xml composer mysql-server",
        f"cd /var/www && composer create-project --prefer-dist laravel/laravel {project_name}",
        f"sudo chown -R www-data:www-data /var/www/{project_name}",
        f"sudo chmod -R 775 /var/www/{project_name}/storage /var/www/{project_name}/bootstrap/cache",
        "sudo systemctl restart apache2",
        f"echo '<VirtualHost *:80>\n    ServerName {project_name}.local\n    DocumentRoot /var/www/{project_name}/public\n    <Directory /var/www/{project_name}/public>\n        AllowOverride All\n        Require all granted\n    </Directory>\n    ErrorLog ${{APACHE_LOG_DIR}}/{project_name}_error.log\n    CustomLog ${{APACHE_LOG_DIR}}/{project_name}_access.log combined\n</VirtualHost>' | sudo tee /etc/apache2/sites-available/{project_name}.conf",
        f"sudo a2ensite {project_name}.conf",
        "sudo systemctl reload apache2",
        f"mysql -u root -e \"CREATE DATABASE {db_name};\"",
        f"mysql -u root -e \"CREATE USER '{db_user}'@'localhost' IDENTIFIED BY '{db_password}';\"",
        f"mysql -u root -e \"GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_user}'@'localhost';\"",
        f"mysql -u root -e \"FLUSH PRIVILEGES;\"",
        f"sed -i 's/DB_DATABASE=.*/DB_DATABASE={db_name}/' /var/www/{project_name}/.env",
        f"sed -i 's/DB_USERNAME=.*/DB_USERNAME={db_user}/' /var/www/{project_name}/.env",
        f"sed -i 's/DB_PASSWORD=.*/DB_PASSWORD={db_password}/' /var/www/{project_name}/.env",
        f"sed -i 's/SESSION_DRIVER=.*/SESSION_DRIVER=file/' /var/www/{project_name}/.env"
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

# UI utama
st.title("Automasi Instalasi Laravel")
st.divider()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    # Menampilkan tab untuk memilih Login atau Register
    tab1, tab2 = st.tabs(["Login", "Register"])
    # Tab Login
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            user = authenticate_user(username, password)
            if user:
                st.success(f"Selamat datang, {user['full_name']}!")
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Username atau password salah!")
    # Tab Register
    with tab2:
        full_name = st.text_input("Nama Lengkap", key="reg_full_name")
        username = st.text_input("Username", key="reg_user")
        password = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            if register_user(full_name, username, password):
                st.success("Registrasi berhasil! Silakan login.")
            else:
                st.error("Username sudah digunakan!")

if st.session_state["authenticated"]:
    # Form instalasi Laravel
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
