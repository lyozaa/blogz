from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:verysecurepassword@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "119%F6vKTpcbsZ0"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    #TODO: delete "login" after / is set up
    route_whitelist = ["login","blog_index", "index", "signup"]
    if request.endpoint not in route_whitelist and "username" not in session:
        return redirect("/login")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("That username doesn't exist.", category="error")
            return render_template("login.html")
        if user.password != password:
            flash("That password is incorrect.", category="error")
            return render_template("login.html")
        else:
            session["username"] = username
            # session['logged_in']=True ----------- need flask-login module for this kind of thing, i think
            flash("Logged In!", category="success") 
            return redirect("/newpost")
    else:
        # if:
        #     session['logged_in']=True:
        #     flash("You're already logged in!", category=error) 
        #     return redirect("/blog")
        # else:
        return render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        #request information from the form
        username = request.form["username"]
        password = request.form["password"]
        verify = request.form["verify"]

        #validate the data
        #initialize the error messages
        username_error_msg = ""
        password_error_msg = ""

        #username qualify conditions
        if username == "":
            username_error_msg = flash("Please enter a username.", category="error")
        if len(username) < 3:
            username_error_msg = flash("Username must be 3-20 characters.", category="error")
        if len(username) > 20:
            username_error_msg = flash("Username must be 3-20 characters.", category="error")
        if " " in username:
            username_error_msg = flash("Username cannot contain a space.", category="error")
        else:
            username_error_msg == ""
       
        #password qualify conditions
        if password == "":
            password_error_msg = flash("Please enter a password.", category="error")
        if len(password) < 3:
            password_error_msg = flash("Password must be at least 3 characters.", category="error")
        if password != verify:
            password_error_msg = flash("Passwords do not match.", category="error")
        else:
            password_error_msg == ""
     
        #if all fields pass qualifying conditions, check the database to see if user is unique
        if username_error_msg == "" and password_error_msg == "":
            existing_username = user = User.query.filter_by(username=username).first()
            if not existing_username:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session["username"] = username
                #TODO: Flash "Welcome to Blogz, {{username}}!"
                return redirect("/newpost")
            else:
                username_error_msg = flash("That username is already taken.", category="error")
                return render_template("signup.html", 
                    username_error = username_error_msg)
        else:
            return render_template("signup.html", 
                username_error = username_error_msg,
                password_error = password_error_msg)

    return render_template("signup.html")


@app.route("/logout")
def logout():
    del session["username"]
    flash("Logged Out!", category="success")
    return redirect("/blog")


@app.route("/")
def index():
    users = User.query.all()
    return render_template("index.html", 
        users=users)


@app.route("/blog")
def blog_index():
    # Use Case 1: User clicks on post title to access a single post's page
    if request.args.get('id'):
        post_id = request.args.get('id')
        post = Blog.query.get(post_id)
        return render_template("single-post.html", post=post)
    # Use Case 2: User clicks on username link (from index or end of post) to go to user's blog
    elif request.args.get('user'):
        owner_id = request.args.get('user')
        blogger_name = User.query.get(owner_id)
        posts = Blog.query.filter_by(owner_id=owner_id).all()
        return render_template("singleUser.html", user=blogger_name, posts=posts)
    # Use Case 3: User Uses the <nav> bar to access the /blog page with all post from all users displayed
    else:
        posts = Blog.query.all()
        #TODO: Display written by line after blogs
        return render_template("blog.html", posts=posts)


@app.route("/newpost", methods = ["POST", "GET"])
def new_post_index():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        owner = User.query.filter_by(username=session["username"]).first()

        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()

        single_blog_page = "/blog?id=" + str(new_blog.id)
        return redirect(single_blog_page)
    else:
        return render_template("newpost.html", title="New Post")

if __name__ == "__main__":
    app.run()