from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash, check_password_hash 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our_key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///final.sqlite"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(10000), nullable = False)
    post_id = db.Column(db.Integer, nullable = False)
    comment_time = db.Column(db.Time, nullable = False)
    comment_date = db.Column(db.Date, nullable = False)
    user_id = db.Column(db.Integer, nullable = False)
    comment_upvotes = db.Column(db.Integer, nullable = True)
    comment_downvotes = db.Column(db.Integer, nullable = True)
    
class Posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    post_comment = db.Column(db.String(10000), nullable = False)
    post_time = db.Column(db.Time, nullable = False)
    post_date = db.Column(db.Date, nullable = False)
    user_id = db.Column(db.Integer, nullable = False)
    post_upvotes = db.Column(db.Integer, nullable = True)
    post_downvotes = db.Column(db.Integer, nullable = True)
    

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///final.sqlite"
# db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

@app.route('/', methods = ['GET', 'POST'])
def default_page():
    if 'user_id' in session:
        return redirect(url_for('homepage'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username = username).first()
        if user:
            if check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['username'] = user.username
                return redirect(url_for('homepage'))
                
    else:
        return render_template('forum.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            hashed_password = generate_password_hash(password)

            new_user = User(username=username, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            #return "Signup successful!"
            return render_template('forum.html')
        else:
            return "Please fill out all fields."
        
    return render_template('signup.html')

@app.route('/homepage')
def homepage():
    if 'user_id' not in session:
        return redirect(url_for('default_page'))
    else:
        return render_template('homepage.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('default_page'))


if __name__ == "__main__":
    app.run(debug=True)