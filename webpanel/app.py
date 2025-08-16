from flask import Flask
from flask import Flask, render_template, request, json, redirect, url_for, jsonify
from flaskext.mysql import MySQL
from mysql.connector import connect, Error
import yaml
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

with open("../config.yaml", "r") as f:
    conf = yaml.safe_load(f)

app = Flask(__name__)
app.config['SECRET_KEY'] = conf['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = 'static/logos'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Redirect unauthenticated users to 'login' route

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


#Вот тут надо отдавать топ-10 активных адресов и количество запросов у них
#SELECT DISTINCT(addr), COUNT(*) AS req_count FROM hikariplus GROUP BY addr ORDER BY req_count DESC limit 10;


        return render_template('dash.html', rc=rc, uc=uc, ucounter=uc[:9], mc=mc, mcounter=mc[:9], test=test)

@app.route('/api/signin',methods=['POST'])
# def signIn():
#     name = request.form['inputName']
#     password = request.form['inputPassword']
#     cnx = connect(user=conf['user'], password=conf['password'], host=conf['host_db'], database=conf['database'])
#     cursor = cnx.cursor(buffered=True)
#     check_user = f"""select * from users where user_name='{name}' and user_password='{password}'"""
#     cursor.execute(check_user)

#     result = cursor.fetchall()
#     if result:
#         return redirect(url_for('dash'))
#     else:
#         return json.dumps({'html':'<span>Username or Password is incorrect</span>'})
#     cnx.close()
def login():
    if request.method == 'POST':
        username = request.form['inputName']
        password = request.form['inputPassword']
        cnx = connect(user=conf['user'], password=conf['password'], host=conf['host_db'], database=conf['database'])
        cursor = cnx.cursor(buffered=True)
        select_user = f"""SELECT * FROM users WHERE user_name='{username}' and user_password='{password}'"""
        cursor.execute(select_user)
        user_data = cursor.fetchall()
        user = User(user_data[0][0], user_data[0][1], user_data[0][1])
        print(type(user))
        login_user(user)
        return redirect(url_for('dash'))

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
def dashboard():
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
        api_url = "https://analytics.hikariplus.ru/register_service"
        payload = {
            "name": request.form['name'],
            "domain": request.form['domain'],
        }
        
        # Добавьте авторизационный токен, если нужно
        #headers = {'Authorization': 'Bearer your-secret-token'}
        #api_response = requests.post(api_url, json=payload, headers=headers)
        api_response = requests.post(api_url, json=payload)
        if api_response.status_code != 200:
            return jsonify({"error": "API error"}), 500

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='192.168.0.5', port='5000')
