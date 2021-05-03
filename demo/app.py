from flask import Flask, render_template,request, flash, redirect, url_for, session
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

@app.route('/',methods=['GET'])
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
        con.commit()
        curr.close()
        if result>0:
            data = curr.fetchone()
            password = data[4]  # password is loacated in 3rd index in database table
            
            if sha256_crypt.verify(password_user,password):
                session['username'] = request.form['username']
                if session['username'] == 'admin':
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('semester1'))
            else:
                flash("Password not matching. Try again")
    return render_template('login.html')

@app.route('/semester1', methods=['GET', 'POST'])
def semester1():
    if 'username' in session:
        con = mysql.connect()
        curr = con.cursor()
        curr.execute("SELECT * FROM user WHERE username = %s", session['username'])
        current_user =  curr.fetchone()
        current_department = current_user[2]
        curr.execute("SELECT * FROM semester1 WHERE department = %s", current_department)
        sem1 = curr.fetchall()
        try:
            curr.execute("SELECT * FROM studentgrade WHERE username = %s", session['username'])
            current_grade = curr.fetchall()
        except:
            current_grade = []
        sgpa1 = current_user[6]
        cgpa = '-'
        if current_user[6]!='-':
            cgpa = sgpa1
            cgpa = str(cgpa)
        con.commit()
        curr.close()
        if request.method == 'POST':
            con = mysql.connect()
            curr = con.cursor()
            credit = 0
            product_c_gp = 0
            for sem in sem1: 
                grade = request.form[sem[2]]
                if grade == '-':
                    pass
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                curr.execute("SELECT courseid FROM studentgrade WHERE username = %s AND semester = %s ",( session['username'], 'semester1'))
                eeee = curr.fetchall()
                if sem[2] in (x[0] for x in eeee):
                    curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                    con.commit()
                else:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade, 'semester1'))
                    con.commit()
            if credit==0:
                curr.execute("UPDATE user SET sgpa1 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa1 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            con.commit()
            curr.close()
            return redirect(url_for('semester1'))
        return render_template('semester1.html',cgpa = cgpa[:5],sgpa1 = sgpa1[:5],sem1 = sem1,grade = current_grade,username = session['username'],dept = current_department)
    else:
        return "<p>You didn't logged in. <a href = 'http://localhost:5000/login'>click here</a> to login</p>"

@app.route('/semester2', methods=['GET', 'POST'])
def semester2():
    if 'username' in session:
        con = mysql.connect()
        curr = con.cursor()
        curr.execute("SELECT * FROM user WHERE username = %s", session['username'])
        current_user =  curr.fetchone()
        current_department = current_user[2]
        curr.execute("SELECT * FROM semester2 WHERE department = %s", current_department)
        sem2 = curr.fetchall()
        try:
            curr.execute("SELECT * FROM studentgrade WHERE username = %s", session['username'])
            current_grade = curr.fetchall()
        except:
            current_grade = []
        sgpa2 = current_user[7]
        cgpa = '-'
        if current_user[7]!='-':
            cgpa = float(sgpa2) + float(current_user[6])
            cgpa = cgpa/2
            cgpa = str(cgpa)
        con.commit()
        curr.close()
        if request.method == 'POST':
            
            con = mysql.connect()
            curr = con.cursor()
            
            credit = 0
            product_c_gp = 0
            for sem in sem2: 
                grade = request.form[sem[2]]
                if grade == '-':
                    pass
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                curr.execute("SELECT courseid FROM studentgrade WHERE username = %s AND semester = %s ",( session['username'], 'semester2'))
                eeee = curr.fetchall()
                if sem[2] in (x[0] for x in eeee):
                    curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                    con.commit()
                else:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade, 'semester2'))
                    con.commit()
            if credit==0:
                curr.execute("UPDATE user SET sgpa2 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa2 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            con.commit()
            curr.close()
            return redirect(url_for('semester2'))
        return render_template('semester2.html',cgpa = cgpa[:5],sgpa2 = sgpa2[:5],sem2 = sem2,grade = current_grade,username = session['username'],dept = current_department)
    else:
        return "<p>You didn't logged in. <a href = 'http://localhost:5000/login'>click here</a> to login</p>"

@app.route('/semester3', methods=['GET', 'POST'])
def semester3():
    if 'username' in session:
        con = mysql.connect()
        curr = con.cursor()
        curr.execute("SELECT * FROM user WHERE username = %s", session['username'])
        current_user =  curr.fetchone()
        current_department = current_user[2]
        curr.execute("SELECT * FROM semester3 WHERE department = %s", current_department)
        sem3 = curr.fetchall()
        try:
            curr.execute("SELECT * FROM studentgrade WHERE username = %s", session['username'])
            current_grade = curr.fetchall()
        except:
            current_grade = []
        sgpa3 = current_user[8]
        cgpa = '-'
        if current_user[8]!='-':
            cgpa = float(sgpa3) + float(current_user[6])+ float(current_user[7])
            cgpa = cgpa/3
            cgpa = str(cgpa)
        con.commit()
        curr.close()
        if request.method == 'POST':
            con = mysql.connect()
            curr = con.cursor()
            credit = 0
            product_c_gp = 0
            for sem in sem3: 
                grade = request.form[sem[2]]
                if grade == '-':
                    pass
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                curr.execute("SELECT courseid FROM studentgrade WHERE username = %s AND semester = %s ",( session['username'], 'semester3'))
                eeee = curr.fetchall()
                if sem[2] in (x[0] for x in eeee):
                    curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                    con.commit()
                else:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade, 'semester3'))
                    con.commit()
            if credit==0:
                curr.execute("UPDATE user SET sgpa3 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa3 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            con.commit()
            curr.close()
            return redirect(url_for('semester3'))
        return render_template('semester3.html',cgpa = cgpa[:5],sgpa3 = sgpa3[:5],sem3 = sem3,grade = current_grade,username = session['username'],dept = current_department)
    else:
        return "<p>You didn't logged in. <a href = 'http://localhost:5000/login'>click here</a> to login</p>"

@app.route('/semester4', methods=['GET', 'POST'])
def semester4():
    if 'username' in session:
        con = mysql.connect()
        curr = con.cursor()
        curr.execute("SELECT * FROM user WHERE username = %s", session['username'])
        current_user =  curr.fetchone()
        current_department = current_user[2]
        curr.execute("SELECT * FROM semester4 WHERE department = %s", current_department)
        sem4 = curr.fetchall()
        try:
            curr.execute("SELECT * FROM studentgrade WHERE username = %s", session['username'])
            current_grade = curr.fetchall()
        except:
            current_grade = []
        sgpa4 = current_user[9]
        cgpa = '-'
        if current_user[9]!='-':
            cgpa = float(sgpa4) + float(current_user[6])+ float(current_user[7]) +float(current_user[8])
            cgpa = cgpa/4
            cgpa = str(cgpa)
        con.commit()
        curr.close()
        if request.method == 'POST':
            con = mysql.connect()
            curr = con.cursor()
            credit = 0
            product_c_gp = 0
            for sem in sem4: 
                grade = request.form[sem[2]]
                if grade == '-':
                    pass
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                curr.execute("SELECT courseid FROM studentgrade WHERE username = %s AND semester = %s ",( session['username'], 'semester4'))
                eeee = curr.fetchall()
                if sem[2] in (x[0] for x in eeee):
                    curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                    con.commit()
                else:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade, 'semester4'))
                    con.commit()
            if credit==0:
                curr.execute("UPDATE user SET sgpa4 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa4 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            con.commit()
            curr.close()
            return redirect(url_for('semester4'))
        return render_template('semester4.html',cgpa = cgpa[:5],sgpa4 = sgpa4[:5],sem4 = sem4,grade = current_grade,username = session['username'],dept = current_department)
    else:
        return "<p>You didn't logged in. <a href = 'http://localhost:5000/login'>click here</a> to login</p>"

@app.route('/semester5', methods=['GET', 'POST'])
def semester5():
    if 'username' in session:
        con = mysql.connect()
        curr = con.cursor()
        curr.execute("SELECT * FROM user WHERE username = %s", session['username'])
        current_user =  curr.fetchone()
        current_department = current_user[2]
        curr.execute("SELECT * FROM semester5 WHERE department = %s", current_department)
        sem5 = curr.fetchall()
        try:
            curr.execute("SELECT * FROM studentgrade WHERE username = %s", session['username'])
            current_grade = curr.fetchall()
        except:
            current_grade = []
        sgpa5 = current_user[10]
        cgpa = '-'
        if current_user[10]!='-':
            cgpa = float(sgpa5) + float(current_user[6])+ float(current_user[7])+ float(current_user[8])+ float(current_user[9])
            cgpa = cgpa/5
            cgpa = str(cgpa)
        con.commit()
        curr.close()
        if request.method == 'POST':
            con = mysql.connect()
            curr = con.cursor()
            credit = 0
            product_c_gp = 0
            for sem in sem5: 
                grade = request.form[sem[2]]
                if grade == '-':
                    pass
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                curr.execute("SELECT courseid FROM studentgrade WHERE username = %s AND semester = %s ",( session['username'], 'semester5'))
                eeee = curr.fetchall()
                if sem[2] in (x[0] for x in eeee):
                    curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                    con.commit()
                else:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade, 'semester5'))
                    con.commit()
            if credit==0:
                curr.execute("UPDATE user SET sgpa5 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa5 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            con.commit()
            curr.close()
            return redirect(url_for('semester5'))
        return render_template('semester5.html',cgpa = cgpa[:5],sgpa5 = sgpa5[:5],sem5 = sem5,grade = current_grade,username = session['username'],dept = current_department)
    else:
        return "<p>You didn't logged in. <a href = 'http://localhost:5000/login'>click here</a> to login</p>"

@app.route('/semester6', methods=['GET', 'POST'])
def semester6():
    if 'username' in session:
        con = mysql.connect()
        curr = con.cursor()
        curr.execute("SELECT * FROM user WHERE username = %s", session['username'])
        current_user =  curr.fetchone()
        current_department = current_user[2]
        curr.execute("SELECT * FROM semester6 WHERE department = %s", current_department)
        sem6 = curr.fetchall()
        try:
            curr.execute("SELECT * FROM studentgrade WHERE username = %s", session['username'])
            current_grade = curr.fetchall()
        except:
            current_grade = []
        sgpa6 = current_user[11]
        cgpa = '-'
        if current_user[11]!='-':
            cgpa = float(sgpa6) + float(current_user[6])+ float(current_user[7])+ float(current_user[8])+ float(current_user[9])+ float(current_user[10])
            cgpa = cgpa/6
            cgpa = str(cgpa)
        con.commit()
        curr.close()
        if request.method == 'POST':
            con = mysql.connect()
            curr = con.cursor()
            credit = 0
            product_c_gp = 0
            for sem in sem6: 
                grade = request.form[sem[2]]
                if grade == '-':
                    pass
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                curr.execute("SELECT courseid FROM studentgrade WHERE username = %s AND semester = %s ",( session['username'], 'semester6'))
                eeee = curr.fetchall()
                if sem[2] in (x[0] for x in eeee):
                    curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                    con.commit()
                else:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade, 'semester6'))
                    con.commit()
            if credit==0:
                curr.execute("UPDATE user SET sgpa6 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa6 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            con.commit()
            curr.close()
            return redirect(url_for('semester6'))
        return render_template('semester6.html',cgpa = cgpa[:5],sgpa6 = sgpa6[:5],sem6 = sem6,grade = current_grade,username = session['username'],dept = current_department)
    else:
        return "<p>You didn't logged in. <a href = 'http://localhost:5000/login'>click here</a> to login</p>"
        
@app.route('/semester7', methods=['GET', 'POST'])
def semester7():
    if 'username' in session:
        con = mysql.connect()
        curr = con.cursor()
        curr.execute("SELECT * FROM user WHERE username = %s", session['username'])
        current_user =  curr.fetchone()
        current_department = current_user[2]
        curr.execute("SELECT * FROM semester7 WHERE department = %s", current_department)
        sem7 = curr.fetchall()
        try:
            curr.execute("SELECT * FROM studentgrade WHERE username = %s", session['username'])
            current_grade = curr.fetchall()
        except:
            current_grade = []
        sgpa7 = current_user[12]
        cgpa = '-'
        if current_user[12]!='-':
            cgpa = float(sgpa7) + float(current_user[6])+float(current_user[7])+float(current_user[8])+float(current_user[9])+float(current_user[10])+float(current_user[11])
            cgpa = cgpa/7
            cgpa = str(cgpa)
        con.commit()
        curr.close()
        if request.method == 'POST':
            con = mysql.connect()
            curr = con.cursor()
            credit = 0
            product_c_gp = 0
            for sem in sem7: 
                grade = request.form[sem[2]]
                if grade == '-':
                    pass
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                curr.execute("SELECT courseid FROM studentgrade WHERE username = %s AND semester = %s ",( session['username'], 'semester7'))
                eeee = curr.fetchall()
                if sem[2] in (x[0] for x in eeee):
                    curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                    con.commit()
                else:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade, 'semester7'))
                    con.commit()
            if credit==0:
                curr.execute("UPDATE user SET sgpa7 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa7 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            con.commit()
            curr.close()
            return redirect(url_for('semester7'))
        return render_template('semester7.html',cgpa = cgpa[:5],sgpa7 = sgpa7[:5],sem7 = sem7,grade = current_grade,username = session['username'],dept = current_department)
    else:
        return "<p>You didn't logged in. <a href = 'http://localhost:5000/login'>click here</a> to login</p>"

@app.route('/semester8', methods=['GET', 'POST'])
def semester8():
    if 'username' in session:
        con = mysql.connect()
        curr = con.cursor()
        curr.execute("SELECT * FROM user WHERE username = %s", session['username'])
        current_user =  curr.fetchone()
        current_department = current_user[2]
        curr.execute("SELECT * FROM semester8 WHERE department = %s", current_department)
        sem8 = curr.fetchall()
        try:
            curr.execute("SELECT * FROM studentgrade WHERE username = %s", session['username'])
            current_grade = curr.fetchall()
        except:
            current_grade = []
        sgpa8 = current_user[13]
        cgpa = '-'
        if current_user[13]!='-':
            cgpa = float(sgpa8) + float(current_user[6])+float(current_user[7])+float(current_user[8])+float(current_user[9])+float(current_user[10])+float(current_user[11])+float(current_user[12])
            cgpa = cgpa/8
            cgpa = str(cgpa)
        con.commit()
        curr.close()
        if request.method == 'POST':
            con = mysql.connect()
            curr = con.cursor()
            credit = 0
            product_c_gp = 0
            for sem in sem8: 
                grade = request.form[sem[2]]
                if grade == '-':
                    pass
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                curr.execute("SELECT courseid FROM studentgrade WHERE username = %s AND semester = %s ",( session['username'], 'semester8'))
                eeee = curr.fetchall()
                if sem[2] in (x[0] for x in eeee):
                    curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                    con.commit()
                else:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade, 'semester8'))
                    con.commit()
            if credit==0:
                curr.execute("UPDATE user SET sgpa8 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa8 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            con.commit()
            curr.close()
            return redirect(url_for('semester8'))
        return render_template('semester8.html',cgpa = cgpa[:5],sgpa8 = sgpa8[:5],sem8 = sem8,grade = current_grade,username = session['username'],dept = current_department)
    else:
        return "<p>You didn't logged in. <a href = 'http://localhost:5000/login'>click here</a> to login</p>"

'''
@app.route('/student-dashboard', methods=['GET','POST'])
def student_dashboard():
    if 'username' in session:
        con = mysql.connect()
        curr = con.cursor()
        curr.execute("SELECT * FROM user WHERE username = %s", session['username'])
        current_user =  curr.fetchone()
        current_department = current_user[2]
        curr.execute("SELECT * FROM semester1 WHERE department = %s", current_department)
        sem1 = curr.fetchall()
        curr.execute("SELECT * FROM semester2 WHERE department = %s", current_department)
        sem2 = curr.fetchall()
        curr.execute("SELECT * FROM semester3 WHERE department = %s", current_department)
        sem3 = curr.fetchall()
        curr.execute("SELECT * FROM semester4 WHERE department = %s", current_department)
        sem4 = curr.fetchall()
        curr.execute("SELECT * FROM semester5 WHERE department = %s", current_department)
        sem5 = curr.fetchall()
        curr.execute("SELECT * FROM semester6 WHERE department = %s", current_department)
        sem6 = curr.fetchall()
        curr.execute("SELECT * FROM semester7 WHERE department = %s", current_department)
        sem7 = curr.fetchall()
        curr.execute("SELECT * FROM semester8 WHERE department = %s", current_department)
        sem8 = curr.fetchall()
        try:
            curr.execute("SELECT * FROM studentgrade WHERE username = %s", session['username'])
            current_grade = curr.fetchall()
        except:
            current_grade = []

        con.commit()
        curr.close()
        sgpa1,sgpa2,sgpa3,sgpa4,sgpa5,sgpa6,sgpa7,sgpa8 = current_user[6],current_user[7],current_user[8],current_user[9],current_user[10],current_user[11],current_user[12],current_user[13]
        cgpalist = [sgpa1,sgpa2,sgpa3,sgpa4,sgpa5,sgpa6,sgpa7,sgpa8]
        cgpa,deno = 0,0
        for i in cgpalist:
            if i != '-':
                cgpa += float(i)
                deno+=1
        if deno!=0:
            cgpa = cgpa/deno
            
        if request.method == 'POST':
            
            con = mysql.connect()
            curr = con.cursor()
            
            credit = 0
            product_c_gp = 0
            for sem in sem1: 
                grade = request.form[sem[2]]
                if grade == '-':
                    break
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                
                
                flag=0
                curr.execute("SELECT * FROM studentgrade WHERE username = %s AND semester = %s",( session['username'], 'semester1'))
                check_courseid_exist= curr.fetchall()
                for i in check_courseid_exist:
                    if i[2] == sem[2]:
                        curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                        con.commit()
                        flag=1
                        break
                if flag==0:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade, 'semester1'))
                    con.commit()
                
                #try:
                    #return 'asda'
                curr.execute("SELECT courseid FROM studentgrade WHERE username = %s AND semester = %s ",( session['username'], 'semester1'))
                eeee = curr.fetchall()
                if sem[2] in (x[0] for x in eeee):
                    curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                    con.commit()
                else:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade, 'semester1'))
                    con.commit()
            if credit==0:
                curr.execute("UPDATE user SET sgpa1 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa1 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            #return str(product_c_gp/credit) + " " + str(product_c_gp) + " " + str(credit)
            
            credit = 0
            product_c_gp = 0
            for sem in sem2: 
                grade = request.form[sem[2]]
                if grade == '-':
                    break;
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                flag=0
                curr.execute("SELECT * FROM studentgrade WHERE username = %s AND semester = %s",( session['username'], 'semester2'))
                check_courseid_exist= curr.fetchall()
                for i in check_courseid_exist:
                    if i[2] == sem[2]:
                        curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                        con.commit()
                        flag=1
                        break
                if flag==0:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade,'semester2'))
                    con.commit()                   
                    
            if credit==0:
                curr.execute("UPDATE user SET sgpa2 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa2 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            #return str(product_c_gp/credit) + " " + str(product_c_gp) + " " + str(credit)
            
            credit = 0
            product_c_gp = 0           
            for sem in sem3: 
                grade = request.form[sem[2]]
                if grade == '-':
                    break
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                flag=0
                curr.execute("SELECT * FROM studentgrade WHERE username = %s AND semester = %s", (session['username'], 'semester3'))
                check_courseid_exist= curr.fetchall()
                for i in check_courseid_exist:
                    if i[2] == sem[2]:
                        curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                        con.commit()
                        flag=1
                        break
                if flag==0:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade,'semester3'))
                    con.commit()                   

            if credit==0:
                curr.execute("UPDATE user SET sgpa3 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa3 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            
            credit = 0
            product_c_gp = 0            
            for sem in sem4:
                grade = request.form[sem[2]]
                if grade == '-':
                    break
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                flag=0
                curr.execute("SELECT * FROM studentgrade WHERE username = %s AND semester = %s",( session['username'], 'semester4'))
                check_courseid_exist= curr.fetchall()
                for i in check_courseid_exist:
                    if i[2] == sem[2]:
                        curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                        con.commit()
                        flag=1
                        break
                if flag==0:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade,'semester4'))
                    con.commit()                   
            if credit==0:
                curr.execute("UPDATE user SET sgpa5 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa5 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            
            credit = 0
            product_c_gp = 0           
            for sem in sem5:
                grade = request.form[sem[2]]
                if grade == '-':
                    break
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                flag=0
                curr.execute("SELECT * FROM studentgrade WHERE username = %s AND semester = %s",( session['username'], 'semester5'))
                check_courseid_exist= curr.fetchall()
                for i in check_courseid_exist:
                    if i[2] == sem[2]:
                        curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                        con.commit()
                        flag=1
                        break
                if flag==0:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade,'semester5'))
                    con.commit()                   
            if credit==0:
                curr.execute("UPDATE user SET sgpa5 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa5 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            
                        
            credit = 0
            product_c_gp = 0
            for sem in sem6:
                grade = request.form[sem[2]]
                if grade == '-':
                    break
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                flag=0
                curr.execute("SELECT * FROM studentgrade WHERE username = %s AND semester = %s",( session['username'], 'semester6'))
                check_courseid_exist= curr.fetchall()
                for i in check_courseid_exist:
                    if i[2] == sem[2]:
                        curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                        con.commit()
                        flag=1
                        break
                if flag==0:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade,'semester6'))
                    con.commit()                   

            if credit==0:
                curr.execute("UPDATE user SET sgpa6 = %s WHERE username = %s", ('-', session['username']))
            else:
                curr.execute("UPDATE user SET sgpa6 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
            
                        
            credit = 0
            product_c_gp = 0
            for sem in sem7:
                grade = request.form[sem[2]]
                if grade == '-':
                    break
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                flag=0
                curr.execute("SELECT * FROM studentgrade WHERE username = %s AND semester = %s", (session['username'], 'semester7'))
                check_courseid_exist= curr.fetchall()
                for i in check_courseid_exist:
                    if i[2] == sem[2]:
                        curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                        con.commit()
                        flag=1
                        break
                if flag==0:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade,'semester7'))
                    con.commit()                   
            if credit==0:
                curr.execute("UPDATE user SET sgpa7 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa7 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            
                        
            credit = 0
            product_c_gp = 0
            for sem in sem8:
                grade = request.form[sem[2]]
                if grade == '-':
                    break
                elif grade == 'O':
                    product_c_gp = product_c_gp + int(sem[3]) * 10
                    credit += int(sem[3])
                elif grade == 'A+':
                    product_c_gp = product_c_gp + int(sem[3]) * 9
                    credit += int(sem[3])
                elif grade == 'A':
                    product_c_gp = product_c_gp + int(sem[3]) * 8
                    credit += int(sem[3])
                elif grade == 'B+':
                    product_c_gp =  product_c_gp + int(sem[3]) * 7
                    credit += int(sem[3])
                elif grade == 'B':
                    product_c_gp = product_c_gp + int(sem[3]) * 6
                    credit += int(sem[3])
                else:
                    product_c_gp = product_c_gp + int(sem[3]) * 0
                    credit += 0
                flag=0
                curr.execute("SELECT * FROM studentgrade WHERE username = %s AND semester = %s", (session['username'], 'semester8'))
                check_courseid_exist= curr.fetchall()
                for i in check_courseid_exist:
                    if i[2] == sem[2]:
                        curr.execute("UPDATE studentgrade SET grade = %s WHERE username = %s AND courseid = %s",(grade, session['username'] , sem[2]))
                        con.commit()
                        flag=1
                        break
                if flag==0:
                    curr.execute("INSERT INTO studentgrade(username,department,courseid, grade,semester) VALUES(%s, %s, %s, %s,%s)",(session['username'],current_department,sem[2],grade,'semester8'))
                    con.commit()                   
            if credit==0:
                curr.execute("UPDATE user SET sgpa8 = %s WHERE username = %s", ('-', session['username']))
                con.commit()
            else:
                curr.execute("UPDATE user SET sgpa8 = %s WHERE username = %s", (str(product_c_gp/credit), session['username']))
                con.commit()
            
            curr.execute("SELECT * FROM studentgrade WHERE username = %s", session['username'])
            post_current_grade = curr.fetchall()
            curr.execute("SELECT * FROM user WHERE username = %s", session['username'])
            post_current_user =  curr.fetchone()
            p_sgpa1,p_sgpa2,p_sgpa3,p_sgpa4,p_sgpa5,p_sgpa6,p_sgpa7,p_sgpa8 = post_current_user[6],post_current_user[7],post_current_user[8],post_current_user[9],post_current_user[10],post_current_user[11],post_current_user[12],post_current_user[13]
            p_cgpalist = [p_sgpa1,p_sgpa2,p_sgpa3,p_sgpa4,p_sgpa5,p_sgpa6,p_sgpa7,p_sgpa8]
            p_cgpa,p_deno = 0,0
            for i in p_cgpalist:
                if i != '-':
                    p_cgpa += float(i)
                    p_deno+=1
            if p_deno!=0:
                p_cgpa = p_cgpa/p_deno
            con.commit()
            curr.close()
            return render_template('student_dashboard.html',dept=current_department,grade = post_current_grade,username = session['username'],cgpa=p_cgpa,sgpa1=p_sgpa1,sgpa2=p_sgpa2,sgpa3=p_sgpa3,sgpa4=p_sgpa4,sgpa5=p_sgpa5,sgpa6=p_sgpa6,sgpa7=p_sgpa7,sgpa8=p_sgpa8,sem1 = sem1,sem2 = sem2,sem3 = sem3,sem4 = sem4,sem5 = sem5,sem6 = sem6,sem7 = sem7,sem8 = sem8)
            
            return redirect(url_for('student_dashboard'))

        return render_template('student_dashboard.html',dept=current_department,grade = current_grade,username = session['username'],cgpa=cgpa,sgpa1=sgpa1,sgpa2=sgpa2,sgpa3=sgpa3,sgpa4=sgpa4,sgpa5=sgpa5,sgpa6=sgpa6,sgpa7=sgpa7,sgpa8=sgpa8,sem1 = sem1,sem2 = sem2,sem3 = sem3,sem4 = sem4,sem5 = sem5,sem6 = sem6,sem7 = sem7,sem8 = sem8)
    else:
        return "<p>You didn't logged in. <a href = 'http://localhost:5000/login'>click here</a> to login</p>"

'''

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        con = mysql.connect()
        curr = con.cursor()
        curr.execute("SELECT * FROM nameofdepartment")
        department = curr.fetchall()  #(("name"),("asd") )
        dept = []
        con.commit()
        curr.close()
        for i in department:
            dept.append(i[0])
        if request.method == 'POST':
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
                    con.commit()
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
                    con.commit()
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
                    con.commit()
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
                    con.commit()
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
                    con.commit()
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
                    con.commit()
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
                    con.commit()
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
                    con.commit()
                else:
                    flash("Course is already exists.")
            
            con.commit()
            curr.close()
            return redirect(url_for('subjectadmin'))
            
        return render_template('subject.html',dept=dept,sem1 = sem1,sem2 = sem2,sem3 = sem3,sem4 = sem4,sem5 = sem5,sem6 = sem6,sem7 = sem7,sem8 = sem8)
    else:
        return "<p>You didn't logged in. <a href = 'http://localhost:5000/login'>click here</a> to login</p>"

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('home'))


if __name__=='__main__':
    app.run(debug=True)