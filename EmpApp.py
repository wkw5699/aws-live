from flask import Flask, render_template, request, redirect
from pymysql import connections
import os
import boto3
from config import *
import random
from datetime import datetime

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def employee():
    cur = db_conn.cursor()
    cur.execute("SELECT * FROM employee")
    data = cur.fetchall()
    # return render_template('AddEmp.html')
    cur.close()
    return render_template('employee.html', data=data)

@app.route("/attendance", methods=['GET', 'POST'])
def attendance():
    query_string = "SELECT * FROM Attendance"
    cursor = db_conn.cursor()
    cursor.execute(query_string)
    attendance = cursor.fetchall()
    cursor.close()
    print(attendance)

    return render_template('attendance.html', attendance=attendance)

@app.route("/leave", methods=['GET', 'POST'])
def leave():
    cur = db_conn.cursor() 
    cur.execute("SELECT * FROM Leaves")
    leave = cur.fetchall()
    cur.close()
    print(leave)
    return render_template('leave.html', leave = leave)

@app.route("/payroll", methods=['GET', 'POST'])
def payroll():
    cur = db_conn.cursor() 
    cur.execute("SELECT * FROM Payroll")
    payroll = cur.fetchall()
    cur.close()
    print(payroll)
    return render_template('payroll.html', payroll = payroll)


@app.route("/index", methods=['GET', 'POST'])
def aboutUs():
    return render_template('index.html')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    position = request.form['position']
    salary = request.form['salary']
    ot_pay = request.form['ot_pay']
    email = request.form['email']
    phone = request.form['phone']
    emp_image_file = request.files['emp_image_file']
    emp_resume = request.files['emp_resume']
    emp_certificate = request.files['emp_certificate']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    if emp_resume == "":
        return "Please select a file"
    
    if emp_certificate == "":
        return "Please select a file"
    
    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, position, salary, ot_pay, email, phone))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        emp_resume_name_in_s3 = "emp-id-" + str(emp_id) + "_resume"
        emp_certificate_name_in_s3 = "emp-id-" + str(emp_id) + "_certificate"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            s3.Bucket(custombucket).put_object(Key=emp_resume_name_in_s3, Body=emp_resume)
            s3.Bucket(custombucket).put_object(Key=emp_certificate_name_in_s3, Body=emp_certificate)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)
            
            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_resume_name_in_s3)

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_certificate_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return redirect('/')
    #return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/editemp/<id>", methods=['POST'])
def EditeEmp(id):
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    position = request.form['position']
    salary = request.form['salary']
    ot_pay = request.form['ot_pay']
    email = request.form['email']
    phone = request.form['phone']
    print(emp_id, first_name, last_name, position, salary, ot_pay )

    insert_sql = "UPDATE employee SET emp_id=%s, first_name=%s, last_name=%s, position=%s, salary=%s, ot_pay=%s, email=%s, phone=%s WHERE emp_id=%s"
    cursor = db_conn.cursor()


    
    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, position, salary, ot_pay, email, phone, id))
        db_conn.commit()
        

    finally:
        cursor.close()

    print("all modification done...")
    return redirect("/", code=302)  

@app.route("/",methods=['GET'])
def ViewEmp():
    emp_id = request.form.get['emp_id']
    first_name = request.form.get['first_name']
    last_name = request.form.get['last_name']
    position = request.form.get['position']
    salary = request.form.get['salary']
    ot_pay = request.form.get['ot_pay']
    email = request.form.get['email']
    phone = request.form.get['phone']
    emp_image_file = request.files.get['emp_image_file']
    emp_resume = request.files.get['emp_resume']
    emp_certificate = request.files.get['emp_certificate']

    select_sql = "select * from employee"
    cursor = db_conn.cursor()
    try:

        cursor.execute(select_sql, (emp_id, first_name, last_name, position, salary, ot_pay, email, phone))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        emp_resume_name_in_s3 = "emp-id-" + str(emp_id) + "_resume"
        emp_certificate_name_in_s3 = "emp-id-" + str(emp_id) + "_certificate"
        s3 = boto3.resource('s3')

        try:
            print("Data retrieved from MySQL RDS... retrieving images from S3...")
            s3.Bucket(custombucket).get_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            s3.Bucket(custombucket).get_object(Key=emp_resume_name_in_s3, Body=emp_resume)
            s3.Bucket(custombucket).get_object(Key=emp_certificate_name_in_s3, Body=emp_certificate)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)
            
            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_resume_name_in_s3)

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_certificate_name_in_s3)
        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    name=emp_name      

@app.route("/addAttend", methods=['POST'])
def AddAttendance():
    emp_id = request.form['emp_id']
    check_in = request.form['check_in']
    check_out = request.form['check_out']

    ran_id = random.randint(1000, 9999)
    attd_id = "AT" + str(ran_id)

    #calculate total work time and check valid
    check_in_data = check_in.split(":")
    check_out_data = check_out.split(":")
    a_hours = int(check_in_data[0])
    b_hours = int(check_out_data[0])
    a_mins = int(check_in_data[1])
    b_mins = int(check_out_data[1])

    if b_hours < a_hours:
        return "please enter correct check out hours!"
    ttl_a = a_hours + (a_mins/60)
    ttl_b = b_hours + (b_mins/60)
    ttl = ttl_b - ttl_a

    print(ttl)
    total_hours = float(f'{ttl:.2f}')
    print(total_hours)
    overtime = 0
    status = "invalid"
    if (total_hours >= 8):
        overtime = total_hours - 8.00
        status = "valid"


    insert_sql = "INSERT INTO Attendance VALUES (%s, %s, %s, %s, %s, %s, %s)"

    cursor = db_conn.cursor()

    cursor.execute(insert_sql, (attd_id, emp_id, check_in, check_out,total_hours,status,overtime))
    db_conn.commit()

    cursor.close()

    print("all modification done...")
    return redirect('/attendance')

#update Attendance
@app.route("/attendance/<string:attd_id>", methods=['POST'])
def EditAttendance(attd_id):
    check_in = request.form['edit_check_in']
    check_out = request.form['edit_check_out']
  

    #calculate total work time and check valid
    check_in_data = check_in.split(":")
    check_out_data = check_out.split(":")
    a_hours = int(check_in_data[0])
    b_hours = int(check_out_data[0])
    a_mins = int(check_in_data[1])
    b_mins = int(check_out_data[1])

    if b_hours < a_hours:
        return "please enter correct check out hours!"
    ttl_a = a_hours + (a_mins/60)
    ttl_b = b_hours + (b_mins/60)
    ttl = ttl_b - ttl_a

    print(ttl)
    total_hours = float(f'{ttl:.2f}')
    print(total_hours)
    overtime = 0
    status = "invalid"
    if (total_hours >= 8):
        overtime = total_hours - 8.00
        status = "valid"


    update_sql = "UPDATE Attendance SET check_in=%s, check_out=%s, total_hours=%s,status=%s,overtime=%s WHERE attd_id=%s"
    cursor = db_conn.cursor()

    cursor.execute(update_sql, (check_in, check_out,total_hours, status,overtime, attd_id))
    db_conn.commit()

    cursor.close()

    print("all modification done...")
    return redirect('/attendance')

#Add payroll    
@app.route("/addPayroll", methods=['POST'])
def AddPayroll():
    emp_id = request.form['emp_id']
    py_amt = request.form['py_amt']

    if float(py_amt) < 0:
        return "please enter correct payroll amount"

    ran_id = random.randint(1000, 9999)
    py_id = "PR" + str(ran_id)

    insert_sql = "INSERT INTO Payroll VALUES (%s, %s, %s, %s, %s)"

    cursor = db_conn.cursor()

    cursor.execute(insert_sql, (py_id, emp_id, py_amt, "Unpaid", ""))
    db_conn.commit()

    cursor.close()

    print("add payroll successfully...")
    return redirect('/payroll')

#update Payroll
@app.route("/editPayroll/<string:pr_id>", methods=['POST'])
def EditPayroll(pr_id):
    py_amt = request.form['edit_pyamt']
  
    if float(py_amt) < 0:
        return "please enter correct payroll amount"

    update_sql = "UPDATE Payroll SET py_amt=%s WHERE pr_id=%s"
    cursor = db_conn.cursor()

    cursor.execute(update_sql, (py_amt, pr_id))
    db_conn.commit()

    cursor.close()

    print("edit payroll successfully...")
    return redirect('/payroll')    

#pay payroll
@app.route('/payPayroll/<string:pr_id>', methods=['POST'])
def payPayroll(pr_id): 
    today = datetime.now()  
    dt_string = today.strftime("%Y-%m-%d %H:%M:%S")
    update_sql = "UPDATE Payroll SET py_status=%s, payout_date=%s WHERE pr_id=%s"
    cursor = db_conn.cursor()
    print(dt_string)
    cursor.execute(update_sql, ("Paid", dt_string, pr_id))
    db_conn.commit()

    cursor.close()

    print("payroll is paid...")
    return redirect('/payroll')  

#Add leave    
@app.route("/addLeave", methods=['POST'])
def AddLeave():
    emp_id = request.form['emp_id']
    lv_date = request.form['lv_date']
    lv_duration = request.form['lv_duration']
    lv_reason = request.form['lv_reason']


    ran_id = random.randint(1000, 9999)
    lv_id = "LV" + str(ran_id)

    insert_sql = "INSERT INTO Leaves VALUES (%s, %s, %s, %s, %s, %s)"

    cursor = db_conn.cursor()
    cursor.execute(insert_sql, (lv_id, emp_id, lv_date, lv_duration, lv_reason, "Pending"))
    db_conn.commit()

    cursor.close()

    print("add leave successfully...")
    return redirect('/leave')

#update Payroll
@app.route("/editLeave/<string:lv_id>", methods=['POST'])
def EditLeave(lv_id):
    lv_date = request.form['lv_date']
    lv_duration = request.form['lv_duration']
    lv_reason = request.form['lv_reason']
    lv_status = request.form['lv_status']

    update_sql = "UPDATE Leaves SET lv_date=%s, lv_duration=%s, lv_reason=%s, lv_status=%s WHERE lv_id=%s"
    cursor = db_conn.cursor()

    cursor.execute(update_sql, (lv_date, lv_duration, lv_reason, lv_status, lv_id))
    db_conn.commit()

    cursor.close()

    print("edit leave successfully...")
    return redirect('/leave')  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
