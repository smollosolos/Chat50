import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///chat.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#SQL
"""
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL);
--CREATE TABLE groups ( host_id INTEGER, group_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, member TEXT);
CREATE TABLE groups ( host_id INTEGER, group_id INTEGER, member TEXT);

CREATE TABLE messages ( message TEXT, group_id INTEGER, messenger INTEGER, date TEXT);
CREATE UNIQUE INDEX username ON users (username);
"""


def check_user(user):
     if "id" not in session:
            try:
                db.execute("INSERT INTO users (username) VALUES (?)", user)
            except ValueError:
                    return render_template("error.html", message = "Username Taken")
            except:
                return render_template("error.html", message = "An error occured")


@app.route("/", methods=["GET"])
def index():
    if "id" in session:
        db.execute("DELETE FROM messages WHERE group_id = (SELECT group_id FROM groups WHERE host_id = ?)", session["id"])
        db.execute("DELETE FROM groups WHERE host_id = ?", session["id"])
        db.execute("DELETE FROM users WHERE id = ?", session["id"])
    session.clear()

    return render_template("index.html", message = "")


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        u = request.args.get("username")
        check_user(u)
        session["id"] = db.execute("SELECT id FROM users WHERE username = ?", u)[0]["id"]
        group_id = 1
        g = db.execute("SELECT MAX(group_id) AS id FROM groups")[0]["id"]
        if g:
             group_id = g + 1
        db.execute("INSERT INTO groups (host_id, group_id, member) VALUES (?,?, ?)", session["id"], group_id, session["id"])
        return render_template("chat.html")
    else:
         group_id = db.execute("SELECT group_id FROM groups WHERE member = ?", session["id"])[0]["group_id"]
         db.execute("INSERT INTO messages (message,group_id,messenger,date) VALUES (?,?,?,?)", request.form.get("message"), group_id, session["id"], datetime.datetime.now())
         return render_template("chat.html")

@app.route("/load", methods=["FETCH", "GET"])
def load():
    data = db.execute("SELECT message, username, date FROM messages JOIN users ON messages.messenger = users.id WHERE group_id = (SELECT group_id FROM groups WHERE member = ?)",session["id"])
    return render_template("load.html", data = data, client = session["id"], code = db.execute("SELECT group_id FROM groups WHERE member = ?", session["id"])[0]["group_id"])

@app.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "GET":
        u = request.args.get("username")
        check_user(u)
        session["id"] = db.execute("SELECT id FROM users WHERE username = ?", u)[0]["id"]
        return render_template("join.html")
    else:
        code = request.form.get("code")
        host = db.execute("SELECT host_id FROM groups WHERE group_id = ?", code)[0]["host_id"]
        db.execute("INSERT INTO groups (host_id, group_id, member) VALUES (?, ?, ?)", host, code, session["id"])
        return render_template("chat.html")








