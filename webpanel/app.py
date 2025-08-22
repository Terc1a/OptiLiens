from flask import Flask
from flask import Flask, render_template, request, json, redirect, url_for, jsonify
from flaskext.mysql import MySQL
from mysql.connector import connect, Error
import yaml
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
import requests
from flask import current_app as ca
from jinja2 import Environment, FileSystemLoader
from flask import send_from_directory, abort

# Загружаем Jinja‑среду один раз при старте приложения
env = Environment(loader=FileSystemLoader('templates'))

with open("../config.yaml", "r") as f:
    conf = yaml.safe_load(f)

app = Flask(__name__)
app.config['SECRET_KEY'] = conf['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = 'static/logos'
app.config['DOWNLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'downloads')
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    cnx = connect(user=conf['user'], password=conf['password'], host=conf['host_db'], database=conf['database'])
    cursor = cnx.cursor(buffered=True)
    select_user = f"""SELECT * FROM users WHERE user_id={user_id}"""
    cursor.execute(select_user)
    user_data = cursor.fetchall()
    return User(user_data[0][0], user_data[0][1], user_data[0][1])


@app.route("/")
def main():
    return render_template('index.html')


@app.route('/signin')
def signin():

    return render_template('signin.html')


@app.route("/dash", methods=["POST", "GET"])
def dash():
    if request.method == 'GET':
        cnx = connect(user=conf['user'], password=conf['password'], host=conf['host_db'], database=conf['database'])
        cursor = cnx.cursor(buffered=True)
        req_count = f"""select count(*) from hikariplus"""
        req_count2 = f"""select count(*)"""
        uniq_count = f"""select distinct addr from hikariplus"""
        mobile_req_count = f"""select distinct addr from hikariplus where is_mobile='True'"""
        test_q = f"""SELECT DISTINCT(addr), COUNT(*) AS req_count FROM hikariplus GROUP BY addr ORDER BY req_count DESC limit 10"""
        cursor.execute(req_count)
        rc = cursor.fetchall()
        cursor.execute(uniq_count)
        uc = cursor.fetchall()
        cursor.execute(mobile_req_count)
        mc = cursor.fetchall()
        cursor.execute(test_q)
        tq = cursor.fetchall()
        print(type(tq))
        items2 = [v[0] for v in tq]
        items3 = [v[1] for v in tq]
        test = dict((x,y) for x,y in tq)
        print(test)
        cnx.close()

        return render_template('dash.html', rc=rc, uc=uc, ucounter=uc[:9], mc=mc, mcounter=mc[:9], test=test)

@app.route('/api/signin',methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['inputName']
        password = request.form['inputPassword']
        cnx = connect(user=conf['user'], password=conf['password'], host=conf['host_db'], database=conf['database'])
        cursor = cnx.cursor(buffered=True)
        select_user = "SELECT user_id, user_name, user_password FROM users WHERE user_name = %s LIMIT 1"
        cursor.execute(select_user, (username,))
        row = cursor.fetchone()
        if row is None:
            # Пользователь не найден
            return render_template('signin.html', error="Неверные учетные данные")
        user_id, user_name, stored_hash = row

        # Verify the password
        if not check_password_hash(stored_hash, password):
            return render_template('signin.html', error="Неверные учетные данные")

        # Password is correct – log in the user
        user = User(user_id, user_name, stored_hash)
        login_user(user)
        return redirect(url_for('admin_panel'))


    return render_template('signin.html')

@app.route('/content-to-refresh')
def refresher():
        cnx = connect(user=conf['user'], password=conf['password'], host=conf['host_db'], database=conf['database'])
        cursor = cnx.cursor(buffered=True)
        req_count = f"""select count(*) from hikariplus"""
        uniq_count = f"""select distinct addr from hikariplus"""
        mobile_req_count = f"""select distinct addr from hikariplus where is_mobile='True'"""
        cursor.execute(req_count)
        rc = cursor.fetchall()
        cursor.execute(uniq_count)
        uc = cursor.fetchall()
        cursor.execute(mobile_req_count)
        mc = cursor.fetchall()
        cnx.close()

        return jsonify(success=True, rc=rc, uc=uc, ucounter=uc[:9], mc=mc, mcounter=mc[:9])


@app.route('/admin')
@login_required
def admin_panel():
    return render_template('admin.html')


@app.route('/admin/add_service', methods=['POST'])
def add_service():
    try:
        # 1. Сохраняем логотип локально
        logo_path = None
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo.filename != '':
                ext = logo.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4()}.{ext}"
                logo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                logo_path = f"/static/logos/{filename}"

        # 2. Отправляем данные в FastAPI-аналитику
        api_url = "https://analyze.hikariplus.ru/register_service"
        payload = {
            "service_name": request.form['name'],
            "service_domain": request.form['domain'],
        }
        try:
            api_response = requests.post(api_url, params=payload, timeout=5)
        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 502

        if api_response.status_code != 200:
            return jsonify({"error": "API error", "status": api_response.status_code, "text": api_response.text}), 502

        # 3. Генерируем nginx‑конфиг
        tmpl = env.get_template('nginx.conf.j2')
        conf_content = tmpl.render(
            domain=request.form['domain'],
            service=request.form['name'] 
        )

        # 4. Сохраняем файл во временную папку
        filename = f"{request.form['name']}.conf"
        file_path = os.path.join(ca.config['DOWNLOAD_FOLDER'], filename)
        with open(file_path, 'w') as f:
            f.write(conf_content)

        # 5. Отправляем клиенту ссылку на скачивание
        download_url = url_for('download_conf', filename=filename, _external=True)

        return jsonify({"status": "success", "download_url": download_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download/<path:filename>')
def download_conf(filename):
    try:
        return send_from_directory(
            ca.config['DOWNLOAD_FOLDER'],
            filename,
            as_attachment=True   # заголовок Content-Disposition: attachment
        )
    except FileNotFoundError:
        abort(404)


if __name__ == "__main__":
    app.run(debug=True, host='192.168.0.5', port='5000')
