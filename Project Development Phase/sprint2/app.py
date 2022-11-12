from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
from datetime import datetime
from flask_cors import CORS, cross_origin
import ibm_db

app = Flask(__name__, template_folder = 'templates')
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'jbhavanin2002@gmail.com'
app.config['MAIL_PASSWORD'] = '12345'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# GLobal variables
EMAIL=''
USERID=''

conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32733;Security=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=vzq93202;PWD=OIRHO37DPLeUSbSh;","","")

def fetch_walletamount():
    sql = 'SELECT WALLET FROM NEW_USER WHERE EMAIL=?'
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, EMAIL)
    ibm_db.execute(stmt)
    user =ibm_db.fetch_assoc(stmt)
    print(user['WALLET'])
    return user['WALLET'] #returns int
 
def fetch_categories():

    sql = 'SELECT * FROM NEW_CATEGORY WHERE USERID = ?'
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,USERID)
    ibm_db.execute(stmt)

    categories = []
    while ibm_db.fetch_row(stmt) != False:
        categories.append([ibm_db.result(stmt, "CATEGORYID"), ibm_db.result(stmt, "CATEGORY_NAME")])

    sql = 'SELECT * FROM CATEGORY_CATEGORY WHERE USERID IS NULL'
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.execute(stmt)

    while ibm_db.fetch_row(stmt) != False:
        categories.append([ibm_db.result(stmt, "CATEGORYID"), ibm_db.result(stmt, "CATEGORY_NAME")])

    print(categories)
    return categories # returns list 

def fetch_userID():
    sql = 'SELECT USERID FROM NEW_USER WHERE EMAIL=?'
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, EMAIL)
    ibm_db.execute(stmt)
    user=ibm_db.fetch_assoc(stmt)
    print(user['USERID'])
    return user['USERID'] # returns int  

def fetch_expenses() : 
    sql = 'SELECT * FROM NEW_EXPENSE where USERID = ' + str(USERID)
    print(sql)
    stmt = ibm_db.exec_immediate(conn, sql)
    expenses = []
    while ibm_db.fetch_row(stmt) != False:
        category_id = ibm_db.result(stmt, "CATEGORYID")
        category_id = str(category_id)
        sql2 = "SELECT * FROM NEW_CATEGORY WHERE CATEGORYID = " + category_id
        stmt2 = ibm_db.exec_immediate(conn, sql2)
        category_name = ""
        while ibm_db.fetch_row(stmt2) != False :
            category_name = ibm_db.result(stmt2, "CATEGORY_NAME")
        expenses.append([ibm_db.result(stmt, "EXPENSE_AMOUNT"), ibm_db.result(stmt, "DATE"), ibm_db.result(stmt, "DESCRIPTION"), category_name])
    print(expenses)
    return expenses

@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def registration():
    if request.method=='GET':
        return render_template('registration.html')
    if request.method=='POST':
        email=request.form['email']
        EMAIL=email
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
        EMAIL = email
    return redirect(url_for('dashboard'))

@app.route('/login',methods=['GET','POST'])
def login():
    global EMAIL
    if request.method=='POST':
        email=request.form['email']
        EMAIL=email
        password=request.form['password']
        sql="SELECT * FROM NEW_USER WHERE email=? AND password=?"
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
    global USERID
    global EMAIL
    if USERID=='' and EMAIL=='':
        return render_template('login.html')
    elif USERID=='':
        USERID=fetch_userID()
    
    expenses = fetch_expenses()
    wallet = fetch_walletamount()
    return render_template('dashboard.html', expenses = expenses, wallet = wallet, email = EMAIL)
      
@app.route('/updatebalance', methods=['GET','POST'])
def update_balance():
    if request.method == 'GET':
        wallet = fetch_walletamount()
        return render_template('updatebalance.html', wallet = wallet)
    elif request.method == 'POST':
        global EMAIL
        global USERID
        if EMAIL == '':
            return render_template('login.html', msg='Login before proceeding')
        if(USERID==''):
            # get user using email
            USERID = fetch_userID()
        
        new_balance = request.form['balanceupdated']
        sql = 'UPDATE NEW_USER SET WALLET = ? WHERE USERID = ?'
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,new_balance)
        ibm_db.bind_param(stmt,2,USERID)
        ibm_db.execute(stmt)

        return redirect(url_for('dashboard'))


@app.route('/addcategory', methods=['GET','POST'])
def add_category():
    if request.method=='GET':        
        # categories = fetch_categories()
        return render_template('addcategory.html')
    
    elif request.method=='POST':
        return render_template('dashboard.html', msg='Added category!')
@app.route('/addexpense', methods=['GET', 'POST'])
def add_expense():
    if request.method=='GET':
        categories = fetch_categories()
        if len(categories) == 0:
            return redirect(url_for('add_category'))
        return render_template('addexpense.html', categories=categories)

    elif request.method=='POST':
        global EMAIL
        global USERID
        if EMAIL == '':
            return render_template('login.html', msg='Login before proceeding')
        if(USERID==''):
            # get user using email
            USERID = fetch_userID()
        
        amount_spent = request.form['amountspent']
        category_id = request.form.get('category')
        description = request.form['description']
        date = request.form['date']
        print(amount_spent, category_id, description, date, USERID)

        sql="INSERT INTO NEW_EXPENSE(USERID, EXPENSE_AMOUNT, CATEGORYID, DESCRIPTION, DATE) VALUES(?,?,?,?,?)"
        stmt=ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,USERID)
        ibm_db.bind_param(stmt,2,amount_spent)
        ibm_db.bind_param(stmt,3,category_id)
        ibm_db.bind_param(stmt,5,description)
        ibm_db.bind_param(stmt,6,date)
        ibm_db.execute(stmt)

        sql = "UPDATE NEW_USER SET WALLET = WALLET - ? WHERE USERID = ?";
        statement = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(statement, 1, amount_spent)
        ibm_db.bind_param(statement, 2, USERID)
        ibm_db.execute(statement)
    
        return redirect(url_for('dashboard'))
        # return render_template('dashboard.html', msg='Expense added!')

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)