from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:verysecurepassword@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))

    def __init__(self, title, body):
        self.title = title
        self.body = body

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route("/")
def index():
    return redirect("/blog")

@app.route("/blog")
def blog_index():
    #if you want to see the index page that displays all the blog posts
    if not request.args.get("id"):
        all_posts = Blog.query.all()
        return render_template("blog.html", title="Blog", posts=all_posts)
    #if you want to access a specific blog's page
    else: 
        blog_id_query = request.args.get("id") #this needs to get the k/v of the post and the id # of the post
        blog_id = Blog.query.get(blog_id_query)
        return render_template("single-blog.html", post=blog_id)

@app.route("/newpost", methods = ["POST", "GET"])
def new_post_index():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        owner_id = request.form["owner_id"]

        new_blog = Blog(title, body)
        db.session.add(new_blog)
        db.session.commit()

        single_blog_page = "/blog?id=" + str(new_blog.id)
        return redirect(single_blog_page)
    else:
        return render_template("newpost.html", title="New Post")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            # "remember that the user has logged in"
            return redirect("/newpost")
        else:
            #tell them why the login failed
            return "<h1>Error!</h1>"

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

        #initialize the error messages
        username_error_msg = ""
        password_error_msg = ""
        verify_password_error_msg = ""

        #validate the data
        #username qualify conditions
        if username == "":
            username_error_msg = "Please enter a username."
        if len(username) < 3:
            username_error_msg = "Username must be 3-20 characters."
        if len(username) > 20:
            username_error_msg = "Username must be 3-20 characters."
        if " " in username:
            username_error_msg = "Username cannot contain a space."

        #password qualify conditions
        if password == "":
            password_error_msg = "Please enter a password."
        if password != verify:
            password_error_msg = "Passwords do not match."
            verify_password_error_msg = "Passwords do not match."

        #if all fields pass qualifying conditions, check the database to see if user is unique
        if not username_error_msg and not password_error_msg and not verify_password_error_msg:
            existing_username = user = User.query.filter_by(username=username).first()
            if not existing_username:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                # to do - remember the user
                return redirect("/newpost")
            else:
                return "<h1>duplicate user</h1>"

    return render_template("signup.html")



if __name__ == "__main__":
    app.run()