from flask import Flask ,request,render_template,redirect
from flask import session

app = Flask(__name__)
app.config["SECRET_KEY"] = "thisisthesecretkey"


@app.route('/login', methods = ['GET' , 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        session["username"] = username
        session["password"] = password
        return redirect('/dashboard')
    return render_template('login_form.html')

@app.route('/dashboard')
def dashboard():
    username = session.get("username")
    if username:
        return f"{username} has loggen in successfully"
    else:
        return "Your are not logged-in pls first log in"

@app.route('/logout')
def user_logout():
    session.pop("username",None)
    session.pop("password",None)
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug = True)