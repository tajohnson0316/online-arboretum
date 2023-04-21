from flask import render_template, request, redirect, session
from flask_app import app
from flask_app.models.user_model import User
from flask_app.models import tree_model


# Login and registration form routes - GET
@app.route("/", methods=["GET"])
@app.route("/login", methods=["GET"])
@app.route("/register", methods=["GET"])
def display_login_and_registration():
    return render_template("login_registration.html")


# Register new user route - POST
@app.route("/users/new", methods=["POST"])
def register_user():
    if not User.validate_registration(request.form):
        return redirect("/")

    session["user_id"] = User.create_one(
        {**request.form, "password": User.encrypt_string(request.form["password"])}
    )

    return redirect("/home")


# Login route - POST
@app.route("/users/login", methods=["POST"])
def login():
    email = request.form["login_email"]
    if not User.validate_login_email(email):
        return redirect("/")

    user = User.get_one_by_email({"email": email})

    if not User.validate_password(user.password, request.form["login_password"]):
        return redirect("/")

    session["user_id"] = user.id

    return redirect("/home")


# Logout route - POST
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")


# Display homepage route - GET
@app.route("/home", methods=["GET"])
def display_homepage():
    # session validation
    if not "user_id" in session:
        return redirect("/")

    current_user = User.get_one({"id": session["user_id"]})
    list_of_trees = tree_model.Tree.get_all()

    # logic used to help find lengths for number of visitors at a single tree
    list_of_trees_with_visitors = []
    list_of_visitors_lengths = []
    for tree in list_of_trees:
        tree_with_visitors = tree_model.Tree.get_one_with_visitors({"id": tree.id})
        list_of_trees_with_visitors.append(tree_with_visitors)
        list_of_visitors_lengths.append(len(tree_with_visitors.list_of_visitors))

    total_trees = len(list_of_trees_with_visitors)

    return render_template(
        "arboretum_home.html",
        current_user=current_user,
        list_of_trees=list_of_trees_with_visitors,
        total_trees=total_trees,
        lengths=list_of_visitors_lengths,
    )


# VIEW user's planted trees - GET
@app.route("/user/my-trees/view", methods=["GET"])
def display_user_trees():
    # session validation
    if not "user_id" in session:
        return redirect("/")

    current_user = User.get_one_with_trees({"id": session["user_id"]})
    list_of_trees = current_user.list_of_trees

    # logic used to help find lengths for number of visitors at a single tree
    list_of_trees_with_visitors = []
    list_of_visitors_lengths = []
    for tree in list_of_trees:
        tree_with_visitors = tree_model.Tree.get_one_with_visitors({"id": tree.id})
        list_of_trees_with_visitors.append(tree_with_visitors)
        list_of_visitors_lengths.append(len(tree_with_visitors.list_of_visitors))

    total_trees = len(list_of_trees_with_visitors)

    return render_template(
        "display_user_trees.html",
        current_user=current_user,
        list_of_trees=list_of_trees_with_visitors,
        total_trees=total_trees,
        lengths=list_of_visitors_lengths,
    )


# ADD the tree_id and user_id to the visitors table - POST
@app.route("/users/<int:tree_id>/visited/add", methods=["POST"])
def add_to_visits(tree_id):
    User.add_tree_to_visits({"user_id": session["user_id"], "tree_id": tree_id})

    return redirect(f"/trees/{tree_id}/view")
