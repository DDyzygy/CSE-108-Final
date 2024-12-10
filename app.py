from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///final.sqlite"
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

@app.route('/')
def default_page():
    return render_template('forum.html')
