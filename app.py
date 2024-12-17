from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
 
from werkzeug.security import generate_password_hash, check_password_hash 
 
from datetime import datetime
 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'our_key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///final.sqlite"
db = SQLAlchemy(app)
 
 
 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
 
class Topics(db.Model):    
    topic_id = db.Column(db.Integer, primary_key=True)
    topic_title = db.Column(db.String(700), nullable = False)
    topic_desc = db.Column(db.String(10000), nullable = True)
    posts = db.relationship('Posts', backref='topic', lazy=True)
 
class Posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    post_comment = db.Column(db.String(10000), nullable = False)
    post_time_date = db.Column(db.DateTime, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    post_upvotes = db.Column(db.Integer, default = 0)
    post_downvotes = db.Column(db.Integer, default = 0)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id'), nullable = False)
    comments = db.relationship('Comments', backref='post', lazy=True)
 
class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(10000), nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable = False)
    comment_time_date = db.Column(db.DateTime, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    comment_upvotes = db.Column(db.Integer, default = 0)
    comment_downvotes = db.Column(db.Integer, default = 0)
 
 
# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///final.sqlite"
# db = SQLAlchemy(app)
 
with app.app_context():
    db.create_all()
 
@app.route('/', methods=['GET', 'POST'])
def default_page():
    session.pop('user_id', None)
    session.pop('username', None)
 
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('homepage'))
        else:
            error = "Username/Password does not match"
 
    return render_template('forum.html', error=error)
 
 
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
            return redirect(url_for('default_page'))
        else:
            return "Please fill out all fields."
 
    return render_template('signup.html')
 
@app.route('/homepage')
def homepage():
    username = session.get('username')
    topics = Topics.query.all()
    if 'username' not in session:
        return redirect(url_for('default_page'))
    else:
        user = User.query.filter_by(username = username).first()
        return render_template('homepage.html', user = user, topics = topics)
 
@app.route('/topic/<int:topic_id>')
def topic_posts(topic_id):
    topic = Topics.query.get(topic_id)
    posts = Posts.query.filter_by(topic_id=topic_id).order_by(Posts.post_time_date.desc()).all()
    for post in posts:
        post.username = User.query.get(post.user_id).username
    return render_template('topic_posts.html', topic=topic, posts=posts)

 
@app.route('/post/<int:post_id>')
def post_comments(post_id):
    post = Posts.query.get(post_id)
    if not post:
        return "Post not found", 404
    post_user = User.query.get(post.user_id)
    comments = db.session.query(Comments, User).join(User, Comments.user_id == User.id).filter(Comments.post_id == post_id).all()
 
    return render_template('post_comments.html', post=post, post_user=post_user, comments=comments)
 
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('default_page'))
 
@app.route('/add_post/<int:topic_id>', methods=['GET', 'POST'])
def add_post(topic_id):
    if 'user_id' not in session:
        return redirect(url_for('default_page'))
 
    if request.method == 'POST':
        post_comment = request.form.get('post_comment')
        if post_comment:
            new_post = Posts(
                post_comment=post_comment,
                post_time_date=datetime.now(),
                user_id=session['user_id'],
                topic_id=topic_id
            )
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('topic_posts', topic_id=topic_id))
 
    return render_template('add_post.html', topic_id=topic_id)
 
@app.route('/add_comment/<int:post_id>', methods=['GET', 'POST'])
def add_comment(post_id):
    if 'user_id' not in session:
        return redirect(url_for('default_page'))
 
    if request.method == 'POST':
        comment = request.form.get('comment')
        if comment:
            new_comment = Comments(
                comment=comment,
                comment_time_date=datetime.now(),
                user_id=session['user_id'],
                post_id=post_id
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('post_comments', post_id=post_id))
 
    return render_template('add_comment.html', post_id=post_id)
 
 
if __name__ == "__main__":
    app.run(debug=True)