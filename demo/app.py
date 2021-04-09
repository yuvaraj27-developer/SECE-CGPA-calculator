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
app.config['MYSQL_DATABASE_DB'] = 'demo'

mysql.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    con = mysql.connect();
    curr = con.cursor();
    curr.execute("SELECT * FROM nameofdepartment")
    department =curr.fetchall()  #data are stored as a tuple inside a list
    dept = []
    for d in department:
        dept.append(d[0])  # that's why im taking it as a d[0] 
    con.commit()
    curr.close()
    if request.method == 'POST':
        name_user = request.form['name']
        username_user = request.form['username']
        email_user = request.form['email']
        department_user = request.form['department']
        password_user = sha256_crypt.encrypt(str(request.form['password']))
        
        if sha256_crypt.verify((request.form['confirm_password']),password_user) and name_user and username_user and email_user and department_user:
            con = mysql.connect()
            curr = con.cursor()
            already_exist = curr.execute("SELECT * FROM user WHERE username = %s",[username_user])
            if already_exist>0:
                flash("Your were already register. Go to login.")
            else:
                curr.execute("INSERT INTO user(name,username,department,email,password) VALUES(%s, %s, %s, %s, %s)",(name_user,username_user,department_user,email_user,password_user))
                con.commit()
                curr.close()
                return redirect(url_for('home'))
        else:
            flash("Password not matching. Try again",'error')
        #con = mysql.connect()
        #curr = con.cursor()
        
    return render_template('register.html', department=dept)    

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
            password = data[4]  # password is loacated in 3rd index in database table
            
            if sha256_crypt.verify(password_user,password):
                session['username'] = request.form['username']
                return redirect(url_for('dashboard'))
            else:
                flash("Password not matching. Try again")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        con = mysql.connect()
        curr = con.cursor()
        curr.execute("SELECT * FROM nameofdepartment")
        department = curr.fetchall()
        dept = []
        con.commit()
        curr.close()
        for i in department:
            dept.append(i[0])
        if request.method == 'POST':
            '''
            for i in dept:
                try:
                    if request.form[i]>0:
                        check = request.form[i]
                        return check
                except:
                    continue;
            '''
            new_department = request.form['departmentname']
            if new_department not in dept:
                con = mysql.connect()
                curr = con.cursor()
                curr.execute("INSERT INTO nameofdepartment(departmentname) VALUES(%s)", new_department)
                con.commit()
                curr.close()
                return redirect(url_for('subjectadmin',dept = new_department))
            else:
                flash("Department is already exist.")
            
        return render_template('dashboard.html', username = session['username'], department = dept)
    else:
        return "<p>You didn't logged in. <a href = 'http://localhost:5000/login'>click here</a> to login</p>"

@app.route('/subjectadmin/<dept>', methods=['GET', 'POST'])
def subjectadmin(dept):
    if 'username' in session:
        con = mysql.connect()
        curr = con.cursor()
        curr.execute("SELECT * FROM semester1 WHERE department = %s", dept)
        sem1 = curr.fetchall();
        curr.execute("SELECT * FROM semester2 WHERE department = %s", dept)
        sem2 = curr.fetchall();
        curr.execute("SELECT * FROM semester3 WHERE department = %s", dept)
        sem3 = curr.fetchall();
        curr.execute("SELECT * FROM semester4 WHERE department = %s", dept)
        sem4 = curr.fetchall();
        curr.execute("SELECT * FROM semester5 WHERE department = %s", dept)
        sem5 = curr.fetchall();
        curr.execute("SELECT * FROM semester6 WHERE department = %s", dept)
        sem6 = curr.fetchall();
        curr.execute("SELECT * FROM semester7 WHERE department = %s", dept)
        sem7 = curr.fetchall();
        curr.execute("SELECT * FROM semester8 WHERE department = %s", dept)
        sem8 = curr.fetchall();
        con.commit()
        curr.close()
        check = 0
        
        if request.method == 'POST':
            semester = request.form['semester']
            coursename = request.form['coursename']
            courseid = request.form['courseid']
            creditpoint1 = request.form.get('creditpoint',type=int)
            
            con = mysql.connect()
            curr = con.cursor()
            if semester == 'semester1':
                d=""
                try:
                    curr.execute("SELECT * FROM semester1 WHERE courseid = %s", courseid)
                    data = curr.fetchone()
                    d = data[0]
                    c = data[2]
                except:
                    pass
                if d!=dept or c!=courseid: # checking whether the department and related course detail exist or not....i did this because i'm facing repeative insertion of same data in database while refreshing the page
                    curr.execute("INSERT INTO semester1(department, coursename, courseid, creditpoint) VALUES(%s,%s,%s,%s)",(dept,coursename,courseid,creditpoint1))
                else:
                    flash("Course is already exists.")
            
            elif semester == 'semester2':
                d=""
                try:
                    curr.execute("SELECT * FROM semester2 WHERE courseid = %s", courseid) 
                    data = curr.fetchone()
                    d = data[0]
                except:
                    pass
                if d!=dept:
                    curr.execute("INSERT INTO semester2(department, coursename, courseid, creditpoint) VALUES(%s,%s,%s,%s)",(dept,coursename,courseid,creditpoint1))
                else:
                    flash("Course is already exists.")
            
            elif semester == 'semester3':
                d=""
                try:
                    curr.execute("SELECT * FROM semester3 WHERE courseid = %s", courseid)
                    data = curr.fetchone()
                    d = data[0]
                except:
                    pass
                if d!=dept:
                    curr.execute("INSERT INTO semester3(department, coursename, courseid, creditpoint) VALUES(%s,%s,%s,%s)",(dept,coursename,courseid,creditpoint1))
                else:
                    flash("Course is already exists.")
            
            elif semester == 'semester4':
                d=""
                try:
                    curr.execute("SELECT * FROM semester4 WHERE courseid = %s", courseid)
                    data = curr.fetchone()
                    d = data[0]
                except:
                    pass
                if d!=dept:
                    curr.execute("INSERT INTO semester4(department, coursename, courseid, creditpoint) VALUES(%s,%s,%s,%s)",(dept,coursename,courseid,creditpoint1))
                else:
                    flash("Course is already exists.")
            
            elif semester == 'semester5':
                d=""
                try:
                    curr.execute("SELECT * FROM semester5 WHERE courseid = %s", courseid)
                    data = curr.fetchone()
                    d = data[0]
                except:
                    pass
                if d!=dept:
                    curr.execute("INSERT INTO semester5(department, coursename, courseid, creditpoint) VALUES(%s,%s,%s,%s)",(dept,coursename,courseid,creditpoint1))
                else:
                    flash("Course is already exists.")
            elif semester == 'semester6':
                d=""
                try:
                    curr.execute("SELECT * FROM semester6 WHERE courseid = %s", courseid)
                    data = curr.fetchone()
                    d = data[0]
                except:
                    pass
                if d!=dept:
                    curr.execute("INSERT INTO semester6(department, coursename, courseid, creditpoint) VALUES(%s,%s,%s,%s)",(dept,coursename,courseid,creditpoint1))
                else:
                    flash("Course is already exists.")
            elif semester == 'semester7':
                d=""
                try:
                    curr.execute("SELECT * FROM semester7 WHERE courseid = %s", courseid)
                    data = curr.fetchone()
                    d = data[0]
                except:
                    pass
                if d!=dept:
                    curr.execute("INSERT INTO semester7(department, coursename, courseid, creditpoint) VALUES(%s,%s,%s,%s)",(dept,coursename,courseid,creditpoint1))
                else:
                    flash("Course is already exists.")
            elif semester == 'semester8':
                d=""
                try:
                    curr.execute("SELECT * FROM semester8 WHERE courseid = %s", courseid)
                    data = curr.fetchone()
                    d = data[0]
                except:
                    pass
                if d!=dept:
                    curr.execute("INSERT INTO semester8(department, coursename, courseid, creditpoint) VALUES(%s,%s,%s,%s)",(dept,coursename,courseid,creditpoint1))
                else:
                    flash("Course is already exists.")
            
            con.commit()
            curr.close()
            
        return render_template('subject.html',dept=dept,sem1 = sem1,sem2 = sem2,sem3 = sem3,sem4 = sem4,sem5 = sem5,sem6 = sem6,sem7 = sem7,sem8 = sem8)

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('home'))


if __name__=='__main__':
    app.run(debug=True)