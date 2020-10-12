import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS

app = Flask(__name__)

@app.route("/test", methods=["GET","POST"])
def first_post():
    try:
        my_json = request.get_json()
        name = my_json.get("name")
        age = my_json.get("age")
        
        if not all([name, age]):
            return jsonify(msg='not enough param')
        age+=10
        return jsonify(name=name, age=age)
    except Exception as e:
        print(e)
        return jsonify(msg='error')

        
        
app.run()
  