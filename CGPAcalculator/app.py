from flask import Flask, render_template,request, flash, redirect, url_for, session
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from flaskext.mysql import MySQL

app = Flask(__name__)
app.secret_key = 'V.$GZg38ZR91atXLpTDb/oKKXZ'

mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Yuvi#1332626'
app.config['MYSQL_DATABASE_DB'] = 'cgpacalculator'
app.config['MYSQL_DATABASE_CURSORCLASS'] = 'DictCursor'

mysql.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

'''
class Registration(Form):
    username = StringField('Username', [validators.DataRequired(),validators.length(min=4,max=10)])
    email = StringField('Email Address', [validators.DataRequired(),validators.length(min=6, max=50)])
    password = PasswordField('New Password', [validators.DataRequired(),validators.EqualTo('confirm', message = 'Passwords must match')])
    confirm = PasswordField('Repeat Password')
'''

@app.route('/register', methods=['GET', 'POST'])
def register():
    #form = Registration(request.form)
    if request.method == 'POST':
        name_user = request.form['name']
        username_user = request.form['username']
        email_user = request.form['email']
        password_user = sha256_crypt.encrypt(str(request.form['password']))
        
        if sha256_crypt.verify((request.form['confirm_password']),password_user) and name_user and username_user and email_user:
            con = mysql.connect()
            curr = con.cursor()
            already_exist = curr.execute("SELECT * FROM user WHERE username = %s",[username_user])
            if already_exist>0:
                flash("Your were already register. Go to login.")
            else:
                curr.execute("INSERT INTO user(name,username,email,password) VALUES(%s, %s, %s, %s)",(name_user,username_user,email_user,password_user))
                con.commit()
                curr.close()
                return redirect(url_for('login'))
        else:
            flash("Password not matching. Try again",'error')
        #con = mysql.connect()
        #curr = con.cursor()
        
    return render_template('register.html')    

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_user = request.form['username']
        password_user = request.form['password']
        
        con = mysql.connect()
        curr = con.cursor()
        result = curr.execute("SELECT * FROM user WHERE username = %s", [username_user])
        if result>0:
            data = curr.fetchone()
            password = data[3]  # password is loacated in 3rd index in database table
            
            if sha256_crypt.verify(password_user,password):
                session['username'] = request.form['username']
                return redirect(url_for('dashboard'))
            else:
                flash("Password not matching. Try again")
        
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        if request.method == 'POST':
            #write a code
    return render_template('dashboard.html')
    else:
        return "<p>You didn't logged in. <a href = 'http://localhost:5000/login'>click here</a> to login</p>"

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('home'))


if __name__=='__main__':
    app.run(debug=True)