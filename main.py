from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog"
app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))

    def __init__(self, title, body):
        self.title = title
        self.body = body


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

        new_blog = Blog(title, body)
        db.session.add(new_blog)
        db.session.commit()

        single_blog_page = "/blog?id=" + str(new_blog.id)
        return redirect(single_blog_page)
    else:
        return render_template("newpost.html", title="New Post")




if __name__ == "__main__":
    app.run()