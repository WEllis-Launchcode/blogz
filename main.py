from flask import Flask, request, redirect, session, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://blogz:Rogue#!W@rr!or#s@localhost:5000/blogz"
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "garrosh"
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(15))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password
    
@app.before_request
def require_login():
    allowed_routes = ['logup', 'blog', 'index', 'signin']
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect('/login')

@app.route('/')
def index():
    all_users = User.query.distinct()
    return render_template("index.html", list_all_users=all_users)

@app.route("/blog")
def blog():
    blog_id = request.args.get("id")
    blog_user = request.args.get("owner_id")
    posts = Blog.query.order_by()

    if (blog_id):
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template("singleUser.html", title=post.title, body=post.body, user=post.owner.username, blog_user=post.owner_id)

    if (blog_user):
        entries = Blog.query.filter_by(owner_id=blog_user).all()
        return render_template('entry.html', entries=entries)
    return render_template("todos.html", posts=posts)

@app.route("/signup", methods=["POST", "GET"])
def signin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verpassword = request.form["verpassword"]
        existing_user = User.query.filter_by(username=username).first()

        username_error = ""
        password_error = ""
        verpassword_error = ""

        if username == "":
            return render_template("signup.html", username_error = "Enter a username.")
        elif len(username) <= 3:
            return render_template("signup.html", username_error = "Must be more than 3 characters.")
        elif " " in username:
            return render_template("signup.html", username_error = "Please don't add a space.")

        if password != verpassword:
            return render_template("signup.html", verpassword_error = "Password doesn't match.")

        if password == "":
            return render_template("signup.html", password_error = "Enter a password.")
        elif len(password) <= 3:
            return render_template("signup.html", password_error = "Must be more than 3 characters.")
        elif " " in password:
            return render_template("signup.html", password_error = "No spaces for the password.")

        
        if not username_error and not password_error and not verpassword_error:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session["username"] = username
                return redirect("/newpost")
            else:
                return render_template("signup.html", title= "Signup", username_error=username_error, 
                password_error=password_error, verpassword_error=verpassword_error) 
    return render_template("signup.html")
    

         

@app.route("/login", methods=["POST", "GET"])
def logup():
    username_error = ""
    password_error = ""

    if request.method == "POST":
        print("form")
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session["username"] = username
            print("login")
            return redirect("/newpost")
        elif not user:    
            print("no user")
            return render_template("login.html", username_error="Username doesn't exist.")
        elif user.password != password:
            print("no password")
            return render_template("login.html", password_error="Password doesn't match.")
        
    return render_template("login.html")
            

@app.route('/newpost')
def post():
    return render_template('newpost.html', title="New Post")

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        print("title")
        blog_title = request.form["blog-title"]
        blog_body = request.form["blog-entry"]
        owner = User.query.filter_by(username=session["username"]).first()
        title_error = ""
        body_error = ""

        if not blog_title:
            title_error = "Please enter a blog tilte."
        
        if not blog_body:
            body_error = "Please enter a blog entry."
        
        if not body_error and not title_error:
            new_entry = Blog(blog_title, blog_body, owner)
            db.session.add(new_entry)
            db.session.commit()
            entry_id = new_entry.id
            return redirect("/blog?id={0}".format(entry_id))
        else:
            return render_template("newpost.html", title="New Entry", 
            title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)
    return render_template("newpost.html", title="New Entry")

@app.route("/logout")
def loggingout():
    del session["username"]
    flash("You're logged out.")
    return redirect('/blog')



if __name__ == '__main__':
    app.run()