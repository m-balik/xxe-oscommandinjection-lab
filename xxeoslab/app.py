from flask import Flask, request, render_template, redirect, url_for, session
from lxml import etree
import subprocess
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Kimlik doğrulama için gerekli gizli anahtar
app.config['DEBUG'] = True

USERNAME = 'gtucyber'
PASSWORD = 'turkcell@34000'

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    try:
        # XML girişini lxml ile pars edip dosya okuma zafiyeti oluşturan kod
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
        DOMTree = etree.fromstring(request.data, parser)

        username = DOMTree.find("username").text
        password = DOMTree.find("password").text

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return f"{username} kullanıcısına giriş yapılamadı! Hatalı kullanıcı adı ya da parola", 401

    except Exception as e:
        result = "<result><code>%d</code><msg>%s</msg></result>" % (3, str(e))
        return result, {'Content-Type': 'text/xml;charset=UTF-8'}

@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/ping', methods=['POST'])
def ping():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    ip_address = request.form['ip']
    command = 'ping -c 4 {}'.format(ip_address)
    result = os.popen(command).read()
    return render_template('result.html', result=result, ip_address=ip_address)
    
@app.route('/filter', methods=['POST', 'GET'])
def filter():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        ip_address = request.form['ip']
        # IP adresinde boşluk olup olmadığı kontrolü
        if ' ' in ip_address:
            return render_template('error.html')

        command = 'ping -c 4 {}'.format(ip_address)
        result = os.popen(command).read()
        return render_template('result.html', result=result, ip_address=ip_address)

    return render_template('filter.html')
    
@app.route('/blind', methods=['POST', 'GET'])
def blind():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        ip_address = request.form['ip']
        command = 'ping -c 4 {}'.format(ip_address)
        result = os.popen(command)
        return render_template('result.html', result=result, ip_address=ip_address)

    return render_template('blind.html')
    
@app.route('/menu')
def menu():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('menu.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
