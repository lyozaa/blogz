from flask import Flask, request, redirect, render_template
#will i need jinja 2 for blog template to work?  render_template enough?
@app.route("/")
def index():
    return redirect("/blog")

@app.route("/newpost", methods = ["POST", "GET"])

@app.route("/blog") #isn't this the same as index? just render_template of this page in index, right?don't need a seperate handler?
def index():
    return render_template("/blog", 
    #template variable = python variable,
    #template variable = python variable,
    #template variable = python variable,
    #template variable = python variable, error messages
    )
    

def error_protocols():
    title_error_msg = ""
    blog_entry_error_msg = ""

    if title == "":
        title_error_msg = "Please fill in the title."
    elif body == "":
        blog_entry_error_msg = "Please fill in the body."






app.run()