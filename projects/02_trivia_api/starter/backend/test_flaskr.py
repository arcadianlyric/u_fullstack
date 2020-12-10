import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('cc', 'cc', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after each test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertGreater(len(data['categories']), 0)
        
    def test_get_questions(self):
        res = self.client().get('/questions')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['questions'])

        question = data['questions'][0]
        self.assertIn('id', question.keys())
        self.assertIn('question', question.keys())
        self.assertIn('answer', question.keys())
        self.assertIn('difficulty', question.keys())
        self.assertIn('category', question.keys())
    
    # def test_delete_questions(self):
    #     res = self.client().delete('/questions/77')
    #     data = json.loads(res.data)

    #     questions = Question.query.filter(Question.id ==48).one_or_none()
        
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertEqual(questions, None)

    def test_delete_questions_empty(self):
            res = self.client().delete('/questions/')
            self.assertEqual(res.status_code, 404)

    def test_search_questions(self):
        '''Test if search term in questions returned. '''
        response = self.client().post('/questions/search', json={'searchTerm':'title'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        # print(data)
        self.assertGreater(len(data.get('questions')), 0)
        for question in data.get('questions'):
            print(question)
            self.assertIn('title', question['question'].lower())

    def test_search_questions_empty(self):
        response = self.client().post('/questions/search', json={'searchTerm':'asdfa'})
        self.assertEqual(response.status_code, 404)

    def test_get_questions_by_cagetories(self):
        res = self.client().get('/categories/5/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

    def test_get_questions_by_cagetories_false_id(self):
        # fail to get question on false category
        res = self.client().get('/categories/99/questions')
        self.assertEqual(res.status_code, 400)

    def test_post_questions(self):
        new_question = {
            "question": "What is the 5th element ?",
            "answer": "B",
            "difficulty": 1,
            "category": 1
        }
        res = self.client().post('/questions', json=new_question)
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertGreater(data['total_questions'], 0)

    def test_post_questions_bad_request(self):
        res = self.client().post('/questions', json={})
        self.assertEqual(res.status_code, 400)

    def test_post_quizzes(self):
        '''Test input category '''
        # category = {'id':1}
        res = self.client().post('/quizzes', json={'quiz_category': {'id': 1}, 'previous_questions': [2]})
        data = res.get_json()
        print(data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_post_quizzes_badrequest(self):
        res = self.client().post('/quizzes', json={})
        self.assertEqual(res.status_code, 400)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()