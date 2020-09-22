from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
import sys
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://cc@localhost:5432/todoapp'
db = SQLAlchemy(app)

class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)

  def __repr__(self):
    return f'<Todo {self.id} {self.description}>'

db.create_all()

@app.route('/todos/create', methods=['POST','GET'])
def create_todo():
  error = False
  body = {}
  try:
    description = request.get_json()['description'] # not request.form.get_json
    todo = Todo(description=description)
    db.session.add(todo)
    db.session.commit()
    body['description'] = todo.description
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)
# @app.route('/todos/create', methods=['POST'])
# def create_todo():
#   description = request.get_json()['description']
#   todo = Todo(description=description)
#   db.session.add(todo)
#   db.session.commit()
#   return jsonify({
#     'description': todo.description
#   })

@app.route('/') # must be '/'
def index():
  return render_template('index.html', data=Todo.query.all())

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html', data=[
#       {'description': 'todo1'},
#       {'description': 'todo2'}
#     ])


  