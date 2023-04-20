from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DATABASE
from flask import flash
from flask_app.models import user_model


class Tree:
    def __init__(self, data):
        self.id = data["id"]
        self.species = data["species"]
        self.location = data["location"]
        self.reason = data["reason"]
        self.planted_at = data["planted_at"]
        self.user_id = data["user_id"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.user = None
        self.list_of_visitors = []

    # GET a list of ALL trees
    @classmethod
    def get_all(cls):
        query = """ 
        SELECT *
        FROM trees t LEFT JOIN users u
        ON t.user_id = u.id;
        """

        results = connectToMySQL(DATABASE).query_db(query)

        list_of_trees = []

        for row in results:
            current_tree = cls(row)
            current_tree_planter = {
                "id": row["u.id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "password": row["password"],
                "created_at": row["u.created_at"],
                "updated_at": row["u.updated_at"],
            }
            current_tree.user = user_model.User(current_tree_planter)
            list_of_trees.append(current_tree)

        return list_of_trees

    # GET ONE tree
    @classmethod
    def get_one(cls, data):
        query = """ 
        SELECT *
        FROM trees
        WHERE id = %(id)s;
        """

        results = connectToMySQL(DATABASE).query_db(query, data)

        return cls(results[0])

    # GET ONE tree with a list of users that have visited
    @classmethod
    def get_one_with_visitors(cls, data):
        query = """ 
        SELECT *
        FROM trees t 
        LEFT JOIN visitors v ON v.tree_id = t.id
        LEFT JOIN users u ON v.user_id = u.id
        WHERE t.id = %(id)s;
        """

        results = connectToMySQL(DATABASE).query_db(query, data)

        current_tree = cls(results[0])
        current_tree.user = user_model.User.get_one({"id": current_tree.user_id})

        for row in results:
            if row["u.id"] != None:
                visitor = {
                    "id": row["u.id"],
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "email": row["email"],
                    "password": row["password"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
                current_tree.list_of_visitors.append(user_model.User(visitor))

        return current_tree

    # CREATE a tree
    @classmethod
    def create_one(cls, data):
        query = """ 
        INSERT INTO trees (species, location, reason, planted_at, user_id)
        VALUES (%(species)s, %(location)s, %(reason)s, %(planted_at)s, %(user_id)s);
        """

        new_tree_id = connectToMySQL(DATABASE).query_db(query, data)

        return new_tree_id

    # UPDATE a tree
    @classmethod
    def update_one(cls, data):
        query = """ 
        UPDATE trees
        SET species = %(species)s, location = %(location)s, reason = %(reason)s, planted_at = %(planted_at)s
        WHERE id = %(id)s;
        """

        return connectToMySQL(DATABASE).query_db(query, data)

    # DELETE a tree and any visitor records
    @classmethod
    def delete_one(cls, data):
        query = """ 
        DELETE FROM visitors
        WHERE tree_id = %(id)s;
        """

        connectToMySQL(DATABASE).query_db(query, data)

        query2 = """ 
        DELETE FROM trees
        WHERE id = %(id)s;
        """

        connectToMySQL(DATABASE).query_db(query2, data)

    """ --STATIC METHODS-- """

    @staticmethod
    def validate_tree(data):
        is_valid = True
        if len(data["species"]) < 5:
            is_valid = False
            flash(
                "Please provide a valid species name for the tree: at least 5 characters",
                "error_species",
            )
        if len(data["location"]) < 2:
            is_valid = False
            flash(
                "Please provide the location where your tree is planted",
                "error_location",
            )
        if len(data["reason"]) > 50:
            is_valid = False
            flash(
                "Please limit Reason field to 50 characters",
                "error_reason",
            )
        if len(data["planted_at"]) == 0:
            is_valid = False
            flash(
                "Please provide the date of planting/re-planting",
                "error_date",
            )

        return is_valid
