"""Blogly application."""

from flask import Flask, request, render_template, redirect, url_for, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

# User Profile Routes

@app.route("/")
def home():
    return redirect("/posts")

@app.route("/users")
def list_users():
    users = User.query.all()
    return render_template("user-list.html", users=users)

@app.route("/users/new")
def add_user_form():
    return render_template("add-user.html")

@app.route("/users/new", methods=["POST"])
def add_user():
    
    first_name = request.form["firstname"]
    last_name = request.form["lastname"]
    img_url = request.form["image"]

    user = User(first_name=first_name, last_name=last_name, img_url=img_url)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/users/<int:id>")
def user_profile(id):
    user = User.query.get(id)
    posts = Post.query.filter_by(user_id=id).all()
    return render_template("profile.html", user=user, posts=posts)

@app.route("/users/<int:id>/edit")
def edit_user_form(id):
    user = User.query.get(id)
    return render_template("edit-user.html", id=id, firstname=user.first_name, lastname=user.last_name, img_url=user.img_url)

@app.route("/users/<int:id>/edit", methods=["POST"])
def edit_user(id):
    
    user = User.query.get(id)
    user.first_name = request.form["firstname"]
    user.last_name = request.form["lastname"]
    user.img_url = request.form["image"]
    db.session.commit()
    return redirect(f"/users/{id}")

@app.route("/users/<int:id>/delete")
def delete_user(id):
    Post.query.filter_by(user_id=id).delete()
    User.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect("/")

# Post Routes

@app.route("/posts")
def show_posts():
    posts = db.session.query(Post, User).join(User).all()
    return render_template("posts.html", posts=posts)

@app.route("/users/<int:user_id>/posts/new")
def add_post_form(user_id):
    tags = Tag.query.all()
    return render_template("add-post.html", uid=user_id, tags=tags)

@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def add_post(user_id):

    title = request.form["title"]
    content = request.form["content"]
    tags = request.form.getlist("tags")

    post = Post(title=title, content=content, user_id=user_id, tags=tags)
    
    db.session.add(post)
    db.session.commit()
    return redirect(f"/users/{user_id}")

@app.route("/posts/<int:id>")
def show_post(id):
    post = Post.query.get(id)
    return render_template("post.html", id=id, post=post)

@app.route("/posts/<int:id>/edit")
def post_form(id):
    post = Post.query.get(id)
    tags = Tag.query.all()
    return render_template("post-form.html", id=id, post=post, tags=tags)

@app.route("/posts/<int:id>/edit", methods=["POST"])
def edit_post(id):
    post = Post.query.get(id)
    post.title = request.form["title"]
    post.content = request.form["content"]
    post.tags.clear()
    for tag_name in request.form.getlist("tags"):
        tag = Tag.query.filter_by(name=tag_name).first()
        post.tags.append(tag)

    db.session.commit()

    return redirect(f"/posts/{id}")

@app.route("/posts/<int:id>/delete", methods=["POST"])
def delete_post(id):
    post = Post.query.get(id)
    uid = post.user_id

    Post.query.filter_by(id=id).delete()

    db.session.commit()

    return redirect(f"/users/{uid}")

# Tag Routes

@app.route("/tags")
def tags():
    tags = Tag.query.all()
    return render_template("tags.html", tags=tags)

@app.route("/tags/<int:id>")
def tag(id):
    tag = Tag.query.get(id)
    return render_template("tag.html", tag=tag, posts=tag.posts)

@app.route("/tags/new")
def tag_form():
    return render_template("add-tag.html")

@app.route("/tags/new", methods=["POST"])
def add_tag():
    tag = Tag(name=request.form["name"])
    try:
        db.session.add(tag)
        db.session.commit()
    except:
        db.session.rollback()
        flash("Tag name already exists!")
        return render_template("add-tag.html")
    
    return redirect("/tags")

@app.route("/tags/<int:id>/edit")
def edit_tag_form(id):
    tag = Tag.query.get(id)
    return render_template("edit-tag.html", tag=tag)

@app.route("/tags/<int:id>/edit", methods=["POST"])
def edit_tag(id):
    tag = Tag.query.get(id)
    try:
        tag.name = request.form["name"]
        db.session.commit()
    except:
        db.session.rollback()
        flash("Tag name already exists!")
        return render_template("edit-tag.html", tag=tag)
    
    return redirect("/tags")

@app.route("/tags/<int:id>/delete", methods=["POST"])
def delete_tag(id):
    PostTag.query.filter_by(tag_id = id).delete()
    Tag.query.filter_by(id = id).delete()
    db.session.commit()
    return redirect("/tags")