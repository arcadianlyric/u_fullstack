'''
Tests for jwt flask app.
'''
from models import Recipe, Ingredient
from app import create_app
import os
import json
import tempfile
import pytest

# We'll disable Auth0 calls when testing the core functionality
# to avoid spamming Auth0
# RBAC tests are in test_rbac.py
os.environ["DISABLE_AUTH0"] = "1"


@pytest.fixture
def client():
    '''Provide a test client that uses a temporary SQLite database'''
    db_fd, db_temp_filepath = tempfile.mkstemp()
    app = create_app(
        {'DATABASE_URL': f'sqlite:///{db_temp_filepath}', 'TESTING': True})

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_temp_filepath)


@pytest.fixture(autouse=True)
def test_data(client):
    '''Test dataset with two recipes, used in all tests'''
    pasta = Recipe(
        name='Pasta',
        procedure='Start by...',
        time=30)
    pasta_ingredients = [
        Ingredient(recipe_id=pasta.id,
                   name='Pasta',
                   measurement='2',
                   measurement_unit='packs'),
        Ingredient(recipe_id=pasta.id,
                   name='Tomato Paste',
                   measurement='300',
                   measurement_unit='grams'),
        Ingredient(recipe_id=pasta.id,
                   name='Onion',
                   measurement='1',
                   measurement_unit='pcs'),
    ]
    pasta.ingredients = pasta_ingredients
    pasta.insert()

    omelette = Recipe(
        name='Omelette',
        procedure='Start by...',
        time=10
    )
    omelette_ingredients = [
        Ingredient(
            recipe_id=omelette.id,
            name='Egg',
            measurement='3',
            measurement_unit='pcs'
        ),
        Ingredient(
            recipe_id=omelette.id,
            name='Pepper',
            optional=True,
            measurement='1',
            measurement_unit='pinch'
        )
    ]
    omelette.ingredients = omelette_ingredients
    omelette.insert()


def test_health(client):
    '''Debug endpoint for sanity check'''
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == 'Healthy'


def test_list_recipes(client):
    '''List available recipes'''
    response = client.get('/recipes')
    assert response.status_code == 200
    assert len(response.json['result']) == 2


def test_get_recipe(client):
    '''Getting one recipe'''
    response = client.get('/recipes/1')
    assert response.status_code == 200
    recipe = response.json['result']
    assert recipe['name'] == 'Pasta'
    assert [i['name'] for i in recipe['ingredients']] == [
        'Pasta', 'Tomato Paste', 'Onion']


def test_get_recipe_not_found(client):
    '''Returns NotFound when trying to retrieve a nonexistent recipe'''
    response = client.get('/recipes/1000')
    assert response.status_code == 404


def test_create_recipe(client):
    '''Creates a recipe stub, and check that it exists in the database'''
    recipe = {
        'name': 'Pizza',
        'procedure': 'Pizza making procedure',
        'time': 30
    }
    response = client.post('/recipes', json=recipe)
    assert response.status_code == 200

    pizzas = Recipe.query.filter(Recipe.name == 'Pizza').count()
    assert pizzas == 1


def test_create_recipe_with_ingredients(client):
    '''Creates a recipe with its ingredients, and check that it's persisted'''
    recipe = {
        'name': 'Egg Avocado Sandwich',
        'procedure': 'Doloribus eos ut voluptates quae...',
        'time': 15,
        'ingredients': [
            {
                'name': 'Toasted bread',
                'measurement': 2,
                'measurement_unit': 'pcs'
            },
            {
                'name': 'Boiled egg',
                'measurement': 2,
                'measurement_unit': 'pcs'
            },
            {
                'name': 'Avocado',
                'measurement': 1,
                'measurement_unit': 'pcs'
            },
            {
                'name': 'Lime juice',
                'measurement': 1,
                'measurement_unit': 'tea spoon'
            },
        ]
    }
    response = client.post('/recipes', json=recipe)
    assert response.status_code == 200
    recipe_id = response.json['result']['id']

    response = client.get(f'/recipes/{recipe_id}')
    assert response.status_code == 200

    sandwich = response.json['result']
    assert sandwich['name'] == 'Egg Avocado Sandwich'
    expected_ingredients = [i['name'] for i in recipe['ingredients']]
    actual_ingredients = [i['name'] for i in sandwich['ingredients']]
    assert expected_ingredients == actual_ingredients


def test_create_recipe_bad_request(client):
    '''Create a recipe with missing parameters returns BadRequest response'''
    response = client.post('/recipes', json=None)
    assert response.status_code == 400


def test_update_recipe(client):
    '''Updating a recipe value is persisted on later retrieval'''
    new_data = {
        'name': 'Burrito',
        'ingredients': [
            {
                'name': 'Avocado',
                'measurement': 1,
                'measurement_unit': 'pcs'
            }
        ]
    }
    response = client.patch('/recipes/1', json=new_data)
    assert response.status_code == 200
    assert response.json['success']
    assert response.json['result']['name'] == 'Burrito'

    response = client.get('/recipes/1')
    assert response.status_code == 200
    assert response.json['result']['name'] == 'Burrito'
    ingredients = response.json['result']['ingredients']
    assert len(ingredients) == 1
    assert ingredients[0]['name'] == 'Avocado'


def test_update_recipe_not_found(client):
    '''Updating nonexisting recipe fails'''
    response = client.patch('/recipes/1000', json={'name': 'Burrito'})
    assert response.status_code == 404


def test_update_recipe_no_data(client):
    '''Updating a recipe without values fails'''
    response = client.patch('/recipes/1', json={})
    assert response.status_code == 400


def test_delete_recipe(client):
    '''Deleting a recipe is persisted'''
    response = client.delete('/recipes/1')
    assert response.status_code == 200

    response = client.get('/recipes/1')
    assert response.status_code == 404


def test_delete_recipe_404(client):
    '''Deleting a nonexistent recipe fails with NotFound'''
    response = client.delete('/recipes/1000')
    assert response.status_code == 404


def test_get_ingredients(client):
    '''Listing ingredients separate from the recipe'''
    response = client.get('/ingredients')
    assert response.status_code == 200

    ingredients = response.json['result']
    # ingredients of test recipes
    assert len(ingredients) == 5


def test_create_ingredient(client):
    '''Adding ingredient related to a recipe is persisted on the recipe'''
    response = client.get('/recipes/1')
    recipe = response.json['result']
    recipe_ingredient_ids = [i['id'] for i in recipe['ingredients']]
    assert len(recipe_ingredient_ids) == 3

    new_ingredient = {
        'recipe_id': recipe['id'],
        'name': 'Garlic',
        'measurement': 2,
        'measurement_unit': 'cloves',
        'optional': True
    }
    response = client.post('/ingredients', json=new_ingredient)
    assert response.status_code == 200

    # get updated result
    response = client.get('/recipes/1')
    updated_recipe = response.json['result']
    assert len(updated_recipe['ingredients']) == 4
    newly_added = updated_recipe['ingredients'][-1]
    assert newly_added['name'] == 'Garlic'
    assert newly_added['measurement'] == 2
    assert newly_added['measurement_unit'] == 'cloves'
    assert newly_added['optional']


def test_create_ingredient_bad_request(client):
    '''Adding ingredient with no input fails'''
    response = client.post('/ingredients', json=None)
    assert response.status_code == 400


def test_get_ingredient(client):
    '''Getting an ingredient record'''
    response = client.get('/ingredients/1')
    assert response.status_code == 200
    assert response.json['result']['name'] == 'Pasta'


def test_get_ingredient_404(client):
    '''Getting a nonexistent ingredient fails with NotFound'''
    response = client.get('/ingredients/1000')
    assert response.status_code == 404


def test_update_ingredient(client):
    '''Updating an ingredient is persisted'''
    response = client.get('/ingredients/1')
    old_data = response.json
    new_data = {
        'name': 'Green Eggs',
        'measurement': 10,
        'measurement_unit': 'boxes',
        'optional': False
    }
    response = client.patch('/ingredients/1', json=new_data)
    assert response.status_code == 200
    recipe = response.json['result']
    assert recipe['name'] == 'Green Eggs'
    assert recipe['measurement'] == 10
    assert recipe['measurement_unit'] == 'boxes'
    assert recipe['optional'] is False
    assert recipe['recipe_id'] == old_data['result']['recipe_id']


def test_update_ingredient_bad_request(client):
    '''
    Updating an ingredient with unknown field fails
    with BadRequest response
    '''
    response = client.patch(
        '/ingredients/1', json={'random_field': 'random_value'})
    assert response.status_code == 400


def test_update_ingredient_404(client):
    '''Updating a nonexistent ingredient fails with NotFound'''
    response = client.patch('/ingredients/1000', json={'name': 'test'})
    assert response.status_code == 404


def test_delete_ingredient(client):
    '''Deleting an ingredient is persisted'''
    response = client.delete('/ingredients/1')
    assert response.status_code == 200

    response = client.get('/ingredients/1')
    assert response.status_code == 404


def test_delete_ingredient_404(client):
    '''Deleting a nonexistent ingredient fails with NotFound'''
    response = client.delete('/ingredients/1000')
    assert response.status_code == 404
