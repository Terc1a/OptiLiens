from flask import Flask
from flask import Flask, render_template, request, json, redirect, url_for, jsonify
from flaskext.mysql import MySQL
from mysql.connector import connect, Error
import yaml


with open("../config.yaml", "r") as f:
    conf = yaml.safe_load(f)


app = Flask(__name__)


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
    






if __name__ == "__main__":
    app.run(debug=True, host='192.168.0.11', port='5000')
