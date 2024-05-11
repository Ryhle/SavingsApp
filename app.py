from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == 'user' and password == 'password':
        return redirect(url_for('main_index'))  # Redirect to main.py route
    else:
        return render_template('login.html', message='Invalid username or password')

@app.route('/success')
def success():
    return redirect(url_for('main.index'))  # Redirect to main.py route

if __name__ == '__main__':
    app.run(debug=True)