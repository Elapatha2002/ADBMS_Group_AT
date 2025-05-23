from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# SQL Server DB config
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=DESKTOP-LAM4S7C\\SQLEXPRESS;'
    'DATABASE=ChamodMotorsDB;'
    'Trusted_Connection=yes;'
)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
            admin = cursor.fetchone()
            conn.close()

            if admin:
                return redirect('https://cmdashboardat.streamlit.app/')
            else:
                flash('Invalid username or password', 'error')

        except Exception as e:
            flash(str(e), 'error')

    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
