import streamlit as st
import paramiko
# import mysql.connector
# import hashlib
# import re

from style import style as style
from login import login as login

st.markdown(style, unsafe_allow_html=True)

# menghubungkan ke database untuk form login
login.connect_db()

# menghubungkan ke ssh
def test_ssh_connection(host, user, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=password)
        ssh.close()
        return True, "Koneksi SSH berhasil."
    except Exception as e:
        return False, f"Gagal koneksi SSH: {e}"

# instalasi laravel
def install_laravel_on_server(host, user, password, project_name, port):
    commands = [
        # memeriksa port 
        f"if ! grep -q 'Listen {port}' /etc/apache2/ports.conf; then echo 'Listen {port}' | sudo tee -a /etc/apache2/ports.conf; fi",
        f"if sudo lsof -i :{port} | grep LISTEN; then echo 'Port {port} sudah digunakan.'; else echo 'Port {port} tersedia.'; fi",
        
        # create project dan mengatur permission
        f"cd /var/www && composer create-project --no-progress --quiet --prefer-dist laravel/laravel {project_name} &&"
        f"sudo chown -R www-data:www-data /var/www/{project_name} &&",
        f"sudo chmod -R 775 /var/www/{project_name}/storage /var/www/{project_name}/bootstrap/cache",
        "sudo systemctl restart apache2",

        # create file project
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
        
        # menyimpan informasi host
        f"if ! grep -q '{project_name}.local' /etc/hosts; then echo '127.0.0.1 {project_name}.local' | sudo tee -a /etc/hosts; fi",
        f"sudo a2ensite {project_name}.conf",
        "sudo systemctl restart apache2",
        "sudo a2enmod rewrite",
        "sudo systemctl restart apache2",   
    ]
        
    # log instalasi 
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=password)
        output_placeholder = st.empty()
        log_output = ""
        for command in commands:

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
    
           

# tampilan aplikasi
st.set_page_config(page_title="Automasi Instalasi Laravel", layout="wide")

st.markdown(style, unsafe_allow_html=True)

st.header("Automasi Instalasi Laravel")
st.text(" ")
# st.divider()

with st.container():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # halaman login dan registrasi
    if not st.session_state["authenticated"]:
        tab1, tab2 = st.tabs(["Login", "Register"])
        # halaman login
        with tab1:
            message_login = st.empty()
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                user = login.authenticate_user(email, password)
                if user:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    message_login.error("Email atau password salah!")
        # halaman registrasi
        with tab2:
            message_regis = st.empty()
            full_name = st.text_input("Nama Lengkap", key="reg_full_name")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_pass")
            if st.button("Register"):
                result = login.register_user(full_name, email, password)
                if result == True:
                    message_regis.success("Registrasi berhasil! Silakan login.")
                else:
                    message_regis.error(result)

    if "tab1_complete" not in st.session_state:
        st.session_state["tab1_complete"] = False
    if "tab2_complete" not in st.session_state:
        st.session_state["tab2_complete"] = False

    if st.session_state["authenticated"]:
            tab1, tab2, tab3 = st.tabs(["Informasi Project", "Informasi Database", "Halaman Instalasi"])
            # halaman informasi project
            with tab1:
                message_placeholder = st.empty()
                project_name = st.text_input("Nama Project Laravel", "project")
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
            # halaman informasi database
            if st.session_state["tab1_complete"]:
                with tab2:
                    message_placeholder2 = st.empty()
                    db_name = f"{project_name}_db"

                    database = st.selectbox("Database", ["MySQL", "SQLite"])
                    if database == "MySQL":
                        db_user = st.text_input("Username MySQL", value="root")
                        db_password = st.text_input("Password MySQL", type="password")
                        if database == "MySQL":
                            # mengedit file .env
                            f"sed -i 's/DB_DATABASE=.*/DB_CONNECTION=mysql/' /var/www/{project_name}/.env",
                            f"sed -i 's/DB_DATABASE=.*/DB_DATABASE={db_name}/' /var/www/{project_name}/.env",
                            f"sed -i 's/DB_USERNAME=.*/DB_USERNAME={db_user}/' /var/www/{project_name}/.env",
                            f"sed -i 's/DB_PASSWORD=.*/DB_PASSWORD={db_password}/' /var/www/{project_name}/.env",
                            f"sed -i 's/SESSION_DRIVER=.*/SESSION_DRIVER=file/' /var/www/{project_name}/.env",
                            
                            # create database
                            f"mysql -u {db_user} -p {db_password} -e \"CREATE DATABASE {db_name};\"",
                            f"mysql -u {db_user} -p {db_password} -e \"GRANT ALL PRIVILEGES ON {db_name}.* TO `{db_user}`@'%';\"",

                        # SQLite
                        else:
                                f"sed -i 's/DB_DATABASE=.*/DB_CONNECTION=sqlite/' /var/www/{project_name}/.env",
                                f"sed -i 's/DB_DATABASE=.*/DB_DATABASE={db_name}/database/database.sqlite' /var/www/{project_name}/.env", 
                                                                
                    if st.button("Simpan", key="key_tab2"):    
                        if all([db_user.strip(), db_password.strip()]):
                            st.session_state["db_user"] = db_user
                            st.session_state["db_password"] = db_password
                            st.session_state["tab2_complete"] = True
                            message_placeholder2.success("Tersimpan!")
                        else:
                            message_placeholder2.error("Semua field harus diisi!")
                # halaman summarize
                if st.session_state["tab2_complete"]:
                    with tab3:
                        st.markdown("<h3>Informasi Project</h3>", unsafe_allow_html=True)
                        st.text(f"Nama Project: {project_name}")
                        st.text(f"Server Tujuan: {server_ip}:{port}")
                        st.text("")

                        # tombol instalasi
                        if st.button("Install Laravel"):
                            st.success(f"Memulai instalasi Laravel di {server_ip} dengan port {port}...")
                            mysql_user = st.session_state.get("mysql_user", "root")
                            mysql_password = st.session_state.get("mysql_password", "")

                            # menampilkan log dan error
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

