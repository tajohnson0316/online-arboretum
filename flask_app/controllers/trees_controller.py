from flask import render_template, request, redirect, session
from flask_app import app
from flask_app.models import tree_model
from flask_app.controllers import users_controller
from flask_app.models import user_model


# Display NEW TREE form - GET
@app.route("/trees/new/form", methods=["GET"])
def display_new_tree_form():
    # session validation
    if not "user_id" in session:
        return redirect("/")

    current_user = user_model.User.get_one({"id": session["user_id"]})

    return render_template("new_tree_form.html", current_user=current_user)


# Submit NEW TREE info - POST
@app.route("/trees/new/add", methods=["POST"])
def add_new_tree():
    # session validation
    if not "user_id" in session:
        return redirect("/")

    # tree form validation
    if not tree_model.Tree.validate_tree(request.form):
        return redirect("/trees/new/form")

    new_tree_id = tree_model.Tree.create_one(
        {**request.form, "user_id": session["user_id"]}
    )

    return redirect(f"/trees/{new_tree_id}/view")


# DELETE a user's tree - POST
@app.route("/trees/<int:id>/delete", methods=["POST"])
def delete_tree(id):
    # session validation
    if not "user_id" in session:
        return redirect("/")

    tree_model.Tree.delete_one({"id": id})

    return redirect("/user/my-trees/view")


# VIEW a tree - GET
@app.route("/trees/<int:id>/view", methods=["GET"])
def display_tree(id):
    # session validation
    if not "user_id" in session:
        return redirect("/")

    current_user = user_model.User.get_one_with_visits({"id": session["user_id"]})

    current_tree = tree_model.Tree.get_one_with_visitors({"id": id})
    list_of_visitors = current_tree.list_of_visitors
    visitors_length = len(list_of_visitors)

    # If the user has visited this tree, print the link to allow them to visit
    user_visited = False

    # Check if the current user has visited this tree
    for visitor in list_of_visitors:
        if visitor.email == current_user.email:
            user_visited = True

    return render_template(
        "display_tree.html",
        current_user=current_user,
        current_tree=current_tree,
        list_of_visitors=list_of_visitors,
        visitors_length=visitors_length,
        user_visited=user_visited,
    )


# Display EDIT tree form - GET
@app.route("/trees/<int:id>/edit", methods=["GET"])
def display_edit_tree_form(id):
    # session validation
    if not "user_id" in session:
        return redirect("/")

    current_user = user_model.User.get_one({"id": session["user_id"]})

    current_tree = tree_model.Tree.get_one({"id": id})

    return render_template(
        "edit_tree_form.html", current_user=current_user, current_tree=current_tree
    )


# UPDATE tree info - POST
@app.route("/trees/<int:id>/edit/submit", methods=["POST"])
def update_tree(id):
    # session validation
    if not "user_id" in session:
        return redirect("/")

    # tree form validation
    if not tree_model.Tree.validate_tree(request.form):
        return redirect(f"/trees/{id}/edit")

    tree_model.Tree.update_one({**request.form, "id": id})
    return redirect(f"/trees/{id}/view")
