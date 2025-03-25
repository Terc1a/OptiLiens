from flask import Flask
from flask import Flask, render_template, request, json, redirect, url_for
from flaskext.mysql import MySQL
from mysql.connector import connect, Error
import yaml
import flask_login
from flask_wtf.csrf import CSRFProtect
from flask_login import current_user, login_user, login_required, UserMixin ,logout_user

with open("../config.yaml", "r") as f:
    conf = yaml.safe_load(f)

csrf = CSRFProtect()

login_manager = flask_login.LoginManager()

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

app = Flask(__name__)
app.secret_key = 'a1dcbe59291f58c089qwerqazwf8ee8e2f44f05cdd4465e0d9c726938b2eeaab'
csrf.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    cursor = cnx.cursor(buffered=True)
    check_user = f"""select * from users where user_name='{name}' and user_password='{password}'"""
    cursor.execute(check_user)
    
    user = cursor.fetchall()
    return user


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('signin.html')

@app.route("/")
def main():
    return render_template('index.html')


@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route("/dash", methods=["POST", "GET"])
@login_required
def dash():
    return render_template('dash.html')


@app.route('/api/signin',methods=['POST'])
def signIn():
    name = request.form['inputName']
    password = request.form['inputPassword']
    cnx = connect(user=conf['user'], password=conf['password'], host=conf['host_db'], database=conf['database'])
    cursor = cnx.cursor(buffered=True)
    check_user = f"""select * from users where user_name='{name}' and user_password='{password}'"""
    cursor.execute(check_user)
    
    result = cursor.fetchall()
    if result:
        return redirect(url_for('dash'))
    else:
        return json.dumps({'html':'<span>Username or Password is incorrect</span>'})
    cnx.close()



if __name__ == "__main__":
    app.run(debug=True, host='192.168.0.11', port='5000')
