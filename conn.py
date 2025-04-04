from flask import Flask
from flask import Flask, render_template, request, json, redirect, url_for, jsonify
from flaskext.mysql import MySQL
from mysql.connector import connect, Error
import yaml


with open("config.yaml", "r") as f:
    conf = yaml.safe_load(f)


cnx = connect(user=conf['user'], password=conf['password'], host=conf['host_db'], database=conf['database'])
cursor = cnx.cursor(buffered=True)

print(cnx)