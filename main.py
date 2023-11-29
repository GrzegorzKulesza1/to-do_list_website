from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from random import randint
import datetime
import os

app = Flask(__name__)
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo-lists.db"
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
db.init_app(app)

list_name_placeholder = 'List 1'
list_name = list_name_placeholder
all_todo = []  # A list of user-supplied to-dos. Each item is a dictionary: {"name": , "completed": }.

# Database structure
class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(250))
    name = db.Column(db.String(250))
    completed = db.Column(db.Boolean())


# injects year variable to all templates
@app.context_processor
def inject_year():
    return dict(year=datetime.datetime.now().year)


@app.route('/')
def main_page():
    db.create_all()
    return render_template('index.html',
                           list_name=list_name, all_todo=all_todo)


# The function retrieves a new to-do item from the form in index.html
@app.route('/add', methods=["POST"])
def add():
    todo = request.form["new_todo"]
    all_todo.append({"name": todo, "completed": False})
    # adds a new item to the database if the user provided their list name
    if list_name != list_name_placeholder:
        db_entry = TodoList(list_name=list_name, name=todo, completed=False)
        db.session.add(db_entry)
        db.session.commit()
    return redirect(url_for('main_page'))


# The function retrieves the changed to-do name from the form in edit.html
@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):
    edited_todo = all_todo[index]
    if request.method == "POST":
        # saves the changes to the database if the user uses his list
        if list_name != list_name_placeholder:
            # db_todos retrieves all entries of the current list from the database
            db_todos = TodoList.query.filter_by(list_name=list_name).all()
            db_to_edit = db_todos[index]
            db_to_edit.name = request.form["new_name"]
            db.session.commit()

        edited_todo["name"] = request.form["new_name"]  # Saves changes to the all_todo variable
        return redirect(url_for("main_page"))

    return render_template("edit.html",
                           list_name=list_name, all_todo=all_todo, index=index)


# Function responsible for crossing out completed to-dos.
@app.route("/check", methods=["GET", "POST"])
def checkbox_clicked():
    tasks_completed = request.form.getlist('completed')  # retrieves a list of all selected todos as index
    for index in tasks_completed:
        # changes the completed status to the opposite
        all_todo[int(index)]["completed"] = not all_todo[int(index)]["completed"]

    # if the user uses his list, it makes changes to the completed variable in the database
    if list_name != list_name_placeholder:
        # db_todos retrieves all entries of the current list from the database
        db_todos = TodoList.query.filter_by(list_name=list_name).all()
        for index in tasks_completed:
            db_todos[int(index)].completed = all_todo[int(index)]["completed"]
            db.session.commit()
    return redirect(url_for('main_page'))


# Function removes to-do.
@app.route("/delete/<int:index>", methods=["GET", "POST"])
def delete(index):
    global list_name
    # if the user uses his list,
    if list_name != list_name_placeholder:
        # db_todos retrieves all entries of the current list from the database
        db_todos = TodoList.query.filter_by(list_name=list_name).all()
        db_to_delete = db_todos[index]
        db.session.delete(db_to_delete)
        db.session.commit()
        # Renames the list to the default when all items from the database are deleted
        if len(db_todos) == 1:
            list_name = list_name_placeholder
    del all_todo[index]
    return redirect(url_for('main_page'))


# Retrieves the user-supplied list name from save_list.html
# and saves changes to the list_name variable and the database.
@app.route("/save_list", methods=["GET", "POST"])
def save_list():
    if request.method == "POST":
        global list_name
        new_name = request.form.get("new_list_name")
        new_name = new_name + '#' + str(randint(1000, 9999))
        list_name = new_name

        # Adds all created todos to the database along with the name of the list
        for todo in all_todo:
            db_entry = TodoList(list_name=new_name, name=todo['name'], completed=todo['completed'])
            db.session.add(db_entry)
            db.session.commit()

        return render_template('save_list.html', name=new_name)
    return render_template('save_list.html')


# Gets the entered list name from upload_list.html and retrieves it from the database.
# If the list name does not exist in the database, sends a flash message to upload_list.html.
@app.route('/upload_list', methods=["GET", "POST"])
def upload_list():
    global list_name, all_todo
    if request.method == "POST":
        user_list_name = request.form.get('list_name')
        user_list = TodoList.query.filter_by(list_name=user_list_name).all()
        # Checks whether the list name entered by the user exists in the database.
        if user_list:
            list_name = user_list_name
            all_todo.clear()
            all_todo = [{"name": todo.name, "completed": todo.completed} for todo in user_list]
            return redirect(url_for('main_page'))
        else:
            flash(user_list_name)

    return render_template('upload_list.html')


# After clicking the New list button, it restores the starting values of the variables list_name and all_todo.
@app.route('/new_list')
def new_list():
    global list_name, all_todo
    list_name = list_name_placeholder
    all_todo = []
    return redirect(url_for('main_page'))


if __name__ == '__main__':
    app.run(debug=False)
