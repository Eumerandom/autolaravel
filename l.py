# aku membenakkan kode i.py di sini

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

def authenticate_user(email, password):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, hashed_password))
    user = cursor.fetchone()
    db.close()
    return user

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

def test_ssh_connection(host, user, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=password)
        ssh.close()
        return True, "Koneksi SSH berhasil."
    except Exception as e:
        return False, f"Gagal koneksi SSH: {e}"

def install_laravel_on_server(host, user, password, project_name, mysql_user, mysql_password, port=80):
    db_name = f"{project_name}_db"
    db_user = f"{project_name}_user"
    db_password = f"pass_{project_name}*"
    commands = [
        # "sudo apt update && sudo apt upgrade -y",
        
        # menginstall jika packet belum ada
        
        # "MISSING_PKGS=''",
        # "for pkg in apache2 php php-cli php-mbstring unzip curl php-xml composer mysql-server; do "
        # "  if ! dpkg -l | grep -wq \"$pkg\" && ! command -v \"$pkg\" >/dev/null 2>&1; then "
        # "    MISSING_PKGS=\"$MISSING_PKGS $pkg\"; "
        # "  fi; "
        # "done",
        # "if [ -n \"$MISSING_PKGS\" ]; then sudo apt install -y $MISSING_PKGS || echo 'Beberapa paket gagal diinstal'; fi",
                
        f"if ! grep -q 'Listen {port}' /etc/apache2/ports.conf; then echo 'Listen {port}' | sudo tee -a /etc/apache2/ports.conf; fi",
        f"if sudo lsof -i :{port} | grep LISTEN; then echo 'Port {port} sudah digunakan.'; else echo 'Port {port} tersedia.'; fi",
        
        f"cd /var/www && composer create-project --no-progress --quiet --prefer-dist laravel/laravel {project_name} &&"
        f"sudo chown -R www-data:www-data /var/www/{project_name} &&",
        f"sudo chmod -R 775 /var/www/{project_name}/storage /var/www/{project_name}/bootstrap/cache",
        "sudo systemctl restart apache2",

        f"if [ ! -f /etc/apache2/sites-available/{project_name}.conf ]; then "
        f"sudo bash -c 'cat > /etc/apache2/sites-available/{project_name}.conf <<EOF\n"
        f"<VirtualHost *:{port}>\n"
        f"    ServerName {project_name}.local\n"
        f"    DocumentRoot /var/www/{project_name}/public\n"
        f"    <Directory /var/www/{project_name}/public>\n"
        f"        AllowOverride All\n"
        f"        Require all granted\n"
        f"    </Directory>\n"
        f"    ErrorLog ${{APACHE_LOG_DIR}}/{project_name}_error.log\n"
        f"    CustomLog ${{APACHE_LOG_DIR}}/{project_name}_access.log combined\n"
        f"</VirtualHost>\n"
        f"EOF'",
        
        f"if ! grep -q '{project_name}.local' /etc/hosts; then echo '127.0.0.1 {project_name}.local' | sudo tee -a /etc/hosts; fi",
        f"sudo a2ensite {project_name}.conf",
        "sudo systemctl restart apache2",
        "sudo a2enmod rewrite",
        "sudo systemctl restart apache2",
        
        f"mysql -u {mysql_user} -p {mysql_password} -e \"CREATE DATABASE {db_name};\"",
        f"mysql -u {mysql_user} -p {mysql_password} -e \"CREATE USER `{db_user}`@'%' IDENTIFIED BY '{db_password}';\"",
        f"mysql -u {mysql_user} -p {mysql_password} -e \"GRANT ALL PRIVILEGES ON {db_name}.* TO `{db_user}`@'%';\"",
        f"mysql -u {mysql_user} -p {mysql_password} -e \"FLUSH PRIVILEGES;\"",
        
        f"sed -i 's/DB_DATABASE=.*/DB_DATABASE={db_name}/' /var/www/{project_name}/.env",
        f"sed -i 's/DB_USERNAME=.*/DB_USERNAME={db_user}/' /var/www/{project_name}/.env",
        f"sed -i 's/DB_PASSWORD=.*/DB_PASSWORD={db_password}/' /var/www/{project_name}/.env",
        f"sed -i 's/SESSION_DRIVER=.*/SESSION_DRIVER=file/' /var/www/{project_name}/.env",
    ]
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=password)
        output_placeholder = st.empty()
        log_output = ""
        for command in commands:
            # stdin, stdout, stderr = ssh.exec_command(f"{command}; echo $?", get_pty=True)
            # stdout_lines = stdout.readlines()
            # stderr_lines = stderr.readlines()
            # for line in iter(stdout.readline, ""):
            #     log_output += f"[OUTPUT] {line}"
            #     output_placeholder.text_area("Log Instalasi", log_output, height=500)

            # for err in iter(stderr.readline, ""):
            #     log_output += f"[ERROR] {err}"
            #     output_placeholder.text_area("Log Instalasi", log_output, height=500)
            # exit_code = int(stdout_lines[-1].strip()) if stdout_lines else 1
            
            # if exit_code != 0:
            #     log_output += f"\n[ERROR] {command} (Exit Code: {exit_code}):\n" + "".join(stderr_lines)
            #     log_output += "\nOutput:\n" + "".join(stdout_lines)
            #     output_placeholder.text_area("Log Instalasi", log_output, height=500)
            #     break
            # else:
            #     log_output += f"\n[SUCCESS] {command}:\n" + "".join(stdout_lines)
            #     output_placeholder.text_area("Log Instalasi", log_output, height=500)

            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            for line in iter(stdout.readline, ""):
                log_output += f"{line}"
                output_placeholder.text_area("Log Instalasi", log_output, height=300)

            for err in iter(stderr.readline, ""):
                log_output += f"[ERROR] {err}"
                output_placeholder.text_area("Log Instalasi", log_output, height=300)


        ssh.close()
        return log_output
    except Exception as e:
        return f"Error: {e}"

st.set_page_config(page_title="Automasi Instalasi Laravel", layout="wide")

st.markdown(
    """
    <style>
        * {
            font-family:'Poppins' !important;
        }
        [data-testid="stHeader"] {
            height: 70px !important;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 0px 0px 40px;
            border-top: none;
        }
        [data-testid="stHeader"]::before {
            content: "";
            background: url('https://laravel.com/img/logomark.min.svg') no-repeat center;
            background-size: contain;
            width: 50px;
            height: 50px;
            padding: 20px !important;
            display: block;
        }
        .stMainBlockContainer {
            width: 60vw !important;
            margin: auto !important;
            margin-top: 0 !important;
            padding-top: 40px !important;
            padding-bottom: 0 !important;
            text-align: center !important;
        }
        .stButton>button {
            background-color: #ff2d20 !important;
            color: white !important;
            font-size: 16px !important;
            width: 150px !important;
            padding: 10px !important;
            border-radius: 8px !important;
            margin: auto !important;
        }
        .stButton>button:hover {
            background-color: #171717 !important;
            color: #ff2d20 !important;
            border: 1px solid #ff2d20 !important;
        }
        .stTextInput>div>div>input {
            text-align: left !important;
            font-size: 14px !important;
            padding: 10px !important;
        }
        .stTextInput .stColumns {
            width: 30vw !important;
            justify-content: center !important;
            margin: auto !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            justify-content: center !important;
            margin: auto !important;
        }
        .stTabs [data-baseweb="tab"] {
            flex-grow: 0.5 !important;
            text-align: center !important;
            font-size: 20px !important;
            font-weight: bold !important;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            border-bottom: 1px solid #ff2d20 !important;
        }
        .stTabs [data-baseweb="tab-panel"] {
            width: 40vw !important;
            justify-content: center !important;
            margin: auto !important;
        }
        .stHeader {
            margin-bottom: 40px !important;
        }
        /*
        .stText .stMarkdown {
            justify-content: center !important;
            margin: auto !important;
        }
        */
    </style>
    """,
    unsafe_allow_html=True
)

st.header("Automasi Instalasi Laravel")
st.text(" ")
# st.divider()

with st.container():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            message_login = st.empty()
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                user = authenticate_user(email, password)
                if user:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    message_login.error("Email atau password salah!")
        with tab2:
            message_regis = st.empty()
            full_name = st.text_input("Nama Lengkap", key="reg_full_name")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_pass")
            if st.button("Register"):
                result = register_user(full_name, email, password)
                if result == True:
                    message_regis.success("Registrasi berhasil! Silakan login.")
                else:
                    message_regis.error(result)

    if "tab1_complete" not in st.session_state:
        st.session_state["tab1_complete"] = False
    if "tab2_complete" not in st.session_state:
        st.session_state["tab2_complete"] = False

    if st.session_state["authenticated"]:
            tab1, tab2, tab3 = st.tabs(["Informasi Project", "Informasi MySQL", "Halaman Instalasi"])
            
            with tab1:
                message_placeholder = st.empty()
                project_name = st.text_input("Nama Project Laravel", "my-laravel-project")
                col1, col2 = st.columns([3, 1])
                with col1:
                    server_ip = st.text_input("IP Server", placeholder="192.168.1.100")
                with col2:
                    port = st.text_input("Project Port", value=80)
                server_user = st.text_input("Username SSH", value="root")
                server_password = st.text_input("Password SSH", type="password")
                
                if st.button("Simpan", key="key_tab1"):
                    if all([project_name.strip(), port.strip(), server_ip.strip(), server_user.strip(), server_password.strip()]):
                        success, message = test_ssh_connection(server_ip, server_user, server_password)
                        if success:
                            st.session_state["tab1_complete"] = True
                            message_placeholder.success("Tersimpan!")
                            # st.rerun()
                        else:
                            message_placeholder.error(message)
                    else:
                        message_placeholder.error("Semua field harus diisi!")
                
            if st.session_state["tab1_complete"]:
                with tab2:
                    message_placeholder2 = st.empty()
                    mysql_user = st.text_input("Username MySQL", value="root")
                    mysql_password = st.text_input("Password MySQL", type="password")

                    if st.button("Simpan", key="key_tab2"):    
                        if all([mysql_user.strip(), mysql_password.strip()]):
                            st.session_state["mysql_user"] = mysql_user
                            st.session_state["mysql_password"] = mysql_password
                            st.session_state["tab2_complete"] = True
                            message_placeholder2.success("Tersimpan!")
                        else:
                            message_placeholder2.error("Semua field harus diisi!")
                            
                if st.session_state["tab2_complete"]:
                    with tab3:
                        st.markdown("<h3>Informasi Project</h3>", unsafe_allow_html=True)
                        st.text(f"Nama Project: {project_name}")
                        st.text(f"Server Tujuan: {server_ip}:{port}")
                        st.text("")
                        if st.button("Install Laravel"):
                            st.success(f"Memulai instalasi Laravel di {server_ip} dengan port {port}...")
                            mysql_user = st.session_state.get("mysql_user", "root")
                            mysql_password = st.session_state.get("mysql_password", "")
                            log = install_laravel_on_server(server_ip, server_user, server_password, project_name, mysql_user, mysql_password, port)
                            if "Error: Authentication failed." in log:
                                st.error("Gagal masuk ke server. Periksa kembali IP, username, atau password.")
                            elif "Permission denied" in log:
                                st.error("Gagal mengakses file atau folder. Coba jalankan dengan akses root.")
                            elif "Could not resolve host" in log:
                                st.error("Nama domain tidak ditemukan. Pastikan server dapat mengakses internet.")
                            elif "No such file or directory" in log:
                                st.error("File atau direktori tidak ditemukan. Pastikan path sudah benar.")
                            elif "E: Unable to locate package" in log:
                                st.error("Gagal menginstal paket. Periksa apakah repository sudah diperbarui.")
                            else:
                                st.text_area("Log Instalasi", log, height=300)
                                st.success(f"Laravel berhasil diinstal! Anda dapat mengaksesnya di http://{project_name}.local:{port}")

