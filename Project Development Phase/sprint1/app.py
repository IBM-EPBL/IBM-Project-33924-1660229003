from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
import ibm_db
app = Flask(__name__, template_folder = 'templates')
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'jbhavanin2002@gmail.com'
app.config['MAIL_PASSWORD'] = '12345'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32733;Security=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=vzq93202;PWD=OIRHO37DPLeUSbSh;","","")

@app.route('/', methods=['GET', 'POST'])
def registration():
    if request.method=='GET':
        return render_template('registration.html')
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        wallet=request.form['wallet']
        sql="INSERT INTO NEW_USER(EMAIL,PASSWORD,WALLET) VALUES(?,?,?)"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.bind_param(stmt,3,wallet)
        ibm_db.execute(stmt)
        msg = Message('Registration Verfication',recipients=[email])
        msg.body = ('Congratulations! Welcome user!')
        msg.html = ('<h1>Registration Verfication</h1>'
                    '<p>Congratulations! Welcome user!</p>')
        mail.send(msg)
    return redirect(url_for('dashboard'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        sql="SELECT * FROM NEW_USER WHERE email=abc@gmail.com AND password=abc"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))
    elif request.method=='GET':
        return render_template('login.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

