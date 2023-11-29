# To-do List Website
A web application built using Flask. Users can add, edit, delete, and mark tasks as completed. The application also
supports saving and uploading To-do lists.

### Features
- Displays the current to-do list.
- Add, edit and delete to-dos.
- Mark tasks as completed.
- Save the current to-do list with a custom name.
- Retrie a saved to-do list from the database based on the provided name.

### Requirements
To work the program requires Python 3.x, Flask and Flask-SQLAlchemy library to work. 
You can install the required modules:
```bash
pip install -r requirements.txt
```

You also need to generate a secret key and set it as an environment variable _FLASK_SECRET_KEY_.
```bash
export FLASK_SECRET_KEY=your_secret_key
```
or on Windows:
```bash
set FLASK_SECRET_KEY=your_secret_key
```
