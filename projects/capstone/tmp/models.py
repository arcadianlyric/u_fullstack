import os
import json
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    procedure = Column(String)
    ingredients = db.relationship(
        'Ingredient', backref='recipe', cascade='all, delete-orphan')
    # time to cook in minutes
    time = Column(Integer)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'procedure': self.procedure,
            'ingredients': [ing.format() for ing in self.ingredients],
            'time': self.time
        }


class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    name = Column(String)
    optional = Column(Boolean, default=False)
    measurement = Column(Integer)
    measurement_unit = Column(String)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'name': self.name,
            'optional': self.optional,
            'measurement': self.measurement,
            'measurement_unit': self.measurement_unit
        }
