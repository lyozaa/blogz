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
    #TODO: line 17 user to username?
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blog = db.relationship("Blog", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    #TODO: delete "login" after / is set up
    route_whitelist = ["signup", "index", "blog_index", "login"]
    if request.endpoint not in route_whitelist and "username" not in session:
        return redirect("/login")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session["username"] = username
            flash("Logged In!", category="success")
            return redirect("/newpost")
        else:
            flash("User password incorrect, or user does not exist", category="error")
            return render_template("login.html")

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
        verify_password_error_msg = ""

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
        if password != verify:
            password_error_msg = flash("Passwords do not match.", category="error")
            verify_password_error_msg = flash("Passwords do not match.", category="error")
        else:
            password_error_msg == ""
            verify_password_error_msg == ""

        #if all fields pass qualifying conditions, check the database to see if user is unique
        if not username_error_msg and not password_error_msg and not verify_password_error_msg:
            existing_username = user = User.query.filter_by(username=username).first()
            if not existing_username:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session["username"] = username
                return redirect("/newpost")
            else:
                return render_template("signup.html", 
                    username_error = username_error_msg,
                    password_error = password_error_msg,
                    verify_error = verify_password_error_msg)

    return render_template("signup.html")

@app.route("/logout")
def logout():
    del session["username"]
    flash("Logged Out!", category="success")
    return redirect("/blog")


@app.route("/")
def index():
    return redirect("/blog")


@app.route("/blog")
def blog_index():
    #To see the index page that displays all the blog posts
    if not request.args.get("id"):
        all_posts = Blog.query.all()
        return render_template("blog.html", title="Blog", posts=all_posts)
    #To access a specific blog post's page
    else: 
        blog_id_query = request.args.get("id") #this needs to get the k/v of the post and the id # of the post
        blog_id = Blog.query.get(blog_id_query)
        return render_template("single-blog.html", post=blog_id)


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