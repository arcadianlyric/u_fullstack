import os
import pytest

from test_app import client, test_data

# Enabling Auth0 if it was disabled before
# NOTE: Please run these tests in moderation
# to not get rate-limited by Auth0 servers
if os.environ.get("DISABLE_AUTH0"):
    del os.environ["DISABLE_AUTH0"]

# Require role tokens to be available in the environment,
# must be set in setup.sh
READONLY_TOKEN = os.environ["READONLY_TOKEN"]
ADMIN_TOKEN = os.environ["ADMIN_TOKEN"]


@pytest.fixture
def admin_headers():
    return {'Authorization': f'Bearer {ADMIN_TOKEN}'}


@pytest.fixture
def readonly_headers():
    return {'Authorization': f'Bearer {READONLY_TOKEN}'}


# Unauthenticated user test
def test_guest_access(client):
    '''Request without access tokens is denied'''
    response = client.get('/recipes')
    assert response.status_code == 401


# Read-Only role tests

def test_readonly_list_recipes(client, readonly_headers):
    '''Can read recipes with the read only token'''
    response = client.get('/recipes', headers=readonly_headers)
    assert response.status_code == 200
    assert len(response.json['result']) == 2


def test_readonly_create_recipe(client, readonly_headers):
    '''Creating a recipe with read only token is denied'''
    recipe = {
        'name': 'Pizza',
        'procedure': 'Pizza making procedure',
        'time': 30
    }
    response = client.post('/recipes', json=recipe, headers=readonly_headers)
    assert response.status_code == 401


# Admin role tests

def test_admin_list_recipes(client, admin_headers):
    '''Reading recipes with admin token'''
    response = client.get('/recipes', headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json['result']) == 2


def test_admin_create_recipe(client, admin_headers):
    '''Creating recipe with admin token'''
    recipe = {
        'name': 'Pizza',
        'procedure': 'Pizza making procedure',
        'time': 30
    }
    response = client.post('/recipes', json=recipe, headers=admin_headers)
    assert response.status_code == 200


def test_admin_delete_recipe(client, admin_headers):
    '''Deleting recipe with admin token'''
    response = client.delete('/recipes/1', headers=admin_headers)
    assert response.status_code == 200
