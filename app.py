from flask import Flask, render_template, request
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

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///final.sqlite"
# db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

@app.route('/')
def default_page():
    return render_template('forum.html')

@app.route('/signup', methods=['POST'])
def signup_page():
    username = request.form.get('username')
    password = request.form.get('password')

    hashed_password = generate_password_hash(password)

    new_user = User(username=username, password_hash = hashed_password)
    db.session.add(new_user)
    db.session.commit()



if __name__ == "__main__":
    app.run(debug=True)