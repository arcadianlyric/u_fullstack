import os
import tempfile
import json
import pytest
from app import create_app
from models import Dish, Ingredient

# disable auth0 
os.environ["DISABLE_AUTH0"] = "1"

@pytest.fixture
def client():
    db_fd, db_url = tempfile.mkstemp()
    app = create_app(test_cfg={'DATABASE_URL': "sqlite:///{}".format(db_url), 'TESTING': True})
    # app = create_app(test_url=True)
    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_url)
    
@pytest.fixture(autouse=True)
def test_data(client):
    pizza = Dish(name = 'pizza', price = 10)
    ingredient = [
        Ingredient(dish_id = pizza.id,
                    name = 'tomato',
                    allergen = ''),
        Ingredient(dish_id = pizza.id,
                    name = 'cheese',
                    allergen = 'milk'),
        Ingredient(dish_id = pizza.id,
                    name = 'flour',
                    allergen = 'wheat'),
    ]
    pizza.ingredient = ingredient
    pizza.insert()

    salad = Dish(name = 'salad', price = 5)
    ingredient = [
        Ingredient(dish_id = salad.id,
                    name = 'potato',
                    allergen = ''),
        Ingredient(dish_id = salad.id,
                    name = 'nuts',
                    allergen = 'peanut'),
        Ingredient(dish_id = salad.id,
                    name = 'kale',
                    allergen = ''),
    ]
    salad.ingredient = ingredient
    salad.insert()

    icecream = Dish(name = 'icecream', price = 5)
    ingredient = [
        Ingredient(dish_id = icecream.id,
                    name = 'cream',
                    allergen = 'milk'),
    ]
    icecream.ingredient = ingredient
    icecream.insert()

def test_get_ingredient_all(client):
    res = client.get('/ingredient')
    assert res.status_code == 200
    print(res.json['result'])
    assert len(res.json['result']) == 7

def test_get_dish_all(client):
    res = client.get('/dish')
    assert res.status_code == 200
    print(res.json['result'])
    assert len(res.json['result']) == 3

def test_get_dish(client):
    res = client.get('/dish/1')
    assert res.status_code == 200
    dish = res.json['result']
    assert dish['name'] == 'pizza'
    assert [i['name'] for i in dish['ingredient']]\
         == ['tomato', 'cheese', 'flour']
    assert [i['allergen'] for i in dish['ingredient']]\
         == ['', 'milk', 'wheat']

def test_get_dish_bad_request(client):
    res = client.get('/dish/99')
    assert res.status_code == 404

def test_post_dish(client):
    dish = {
        'name' : 'sushi', 'price' : 15,
        'ingredient' : [{'name' : 'salmon', 'allergen' : 'seafood'},
                        {'name' : 'rice', 'allergen' : ''}]
    }
    res = client.post('/dish', json=dish)
    assert res.status_code == 200

    dish_id = res.json['result']['id']
    assert dish_id == 4
    res = client.get('/dish/{}'.format(dish_id))
    assert res.status_code == 200

def test_post_dish_bad_request(client):
    res = client.post('/dish', json=None)
    assert res.status_code == 404

def test_patch_dish(client):
    patch_data = {'ingredient': [{'name' : 'tomato', 'allergen' : ''},
                            {'name' : 'cheese', 'allergen' : 'milk'},
                            {'name' : 'flour', 'allergen' : 'wheat'},
                            {'name' : 'basil', 'allergen' : ''},
    ]} 
    res = client.patch('/dish/1', json=patch_data)
    assert res.status_code == 200
    
    res = client.get('/dish/1')
    dish = res.json['result']
    assert dish['name'] == 'pizza'
    assert [i['name'] for i in dish['ingredient']]\
        == ['tomato', 'cheese', 'flour', 'basil']

def test_delete_dish(client):
    res = client.delete('/dish/3')
    assert res.status_code == 200

def test_delete_dish_bad_request(client):
    res = client.delete('/dish/99999')
    assert res.status_code == 404


