import streamlit as st
import mysql.connector
import hashlib
import paramiko
import re

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="parastream_adm",
        password="paraSTREAM",
        database="auth_db"
    )

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$", email)

def authenticate_user(email, password):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, hashed_password))
    user = cursor.fetchone()
    db.close()
    return user

def register_user(full_name, email, password):
    if not is_valid_email(email):
        return "Invalid email format"
    
    db = connect_db()
    cursor = db.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)", (full_name, email, hashed_password))
        db.commit()
        return True
    except mysql.connector.IntegrityError:
        return False
    finally:
        db.close()

def install_laravel_on_server(host, user, password, project_name):
    db_name = f"{project_name}_db"
    db_user = f"{project_name}_user"
    db_password = f"pass_{project_name}*$#"
    commands = [
        "sudo apt update && sudo apt upgrade -y",
        "sudo apt install -y apache2 php php-cli php-mbstring unzip curl php-xml composer mysql-server",
        f"cd /var/www && composer create-project --prefer-dist laravel/laravel {project_name}",
        f"sudo chown -R www-data:www-data /var/www/{project_name}",
        f"sudo chmod -R 775 /var/www/{project_name}/storage /var/www/{project_name}/bootstrap/cache",
        "sudo systemctl restart apache2",
        f"echo '<VirtualHost *:80>\n    ServerName {project_name}.local\n    DocumentRoot /var/www/{project_name}/public\n    <Directory /var/www/{project_name}/public>\n        AllowOverride All\n        Require all granted\n    </Directory>\n    ErrorLog ${APACHE_LOG_DIR}/{project_name}_error.log\n    CustomLog ${APACHE_LOG_DIR}/{project_name}_access.log combined\n</VirtualHost>' | sudo tee /etc/apache2/sites-available/{project_name}.conf",
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
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            user = authenticate_user(email, password)
            if user:
                st.success(f"Selamat datang, {user['full_name']}!")
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Email atau password salah!")
    with tab2:
        full_name = st.text_input("Nama Lengkap", key="reg_full_name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            result = register_user(full_name, email, password)
            if result == True:
                st.success("Registrasi berhasil! Silakan login.")
            elif result == "Invalid email format":
                st.error("Format email tidak valid!")
            else:
                st.error("Email sudah digunakan!")

if st.session_state["authenticated"]:
    st.subheader("Tentukan lokasi server")
    server_ip = st.text_input("IP Server", placeholder="192.168.1.100")
    server_user = st.text_input("Username SSH", value="root")
    server_password = st.text_input("Password SSH", type="password")
    project_name = st.text_input("Nama Project Laravel", "my-laravel-project")
    if st.button("Install Laravel"):
        if all([server_ip.strip(), server_user.strip(), server_password.strip(), project_name.strip()]):
            st.success(f"Memulai instalasi Laravel di {server_ip}...")
            log = install_laravel_on_server(server_ip, server_user, server_password, project_name)
            st.text_area("Log Instalasi", log, height=300)
            st.success(f"Laravel berhasil diinstal! Anda dapat mengaksesnya di http://{project_name}.local")
        else:
            st.error("Semua field harus diisi!")
