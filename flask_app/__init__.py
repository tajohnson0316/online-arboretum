from flask import Flask
import re

app = Flask(__name__)
app.secret_key = "This is my secret key - there are many like it, but this one is mine."

DATABASE = "arboretum_db"
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$")
