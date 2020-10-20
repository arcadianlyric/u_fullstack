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
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        
    def test_get_questions(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        

    def test_delete_questions(self):
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)

        questions = Question.query.filter(Question.id == 5).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(questions, None)


    def test_search_questions(self):
        '''Test if search term in questions returned. '''
        response = self.client().post(f'/questions/search', json={'searchTerm':'title'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreater(len(data['questions']), 0)
        for question in data['questions']:
            print(question)
            self.assertIn('title', question['question'].lower())
    # def test_search_questions(self):
        
    #     searchTerm = 'title'
    #     res = self.client().get(f'/questions?searchTerm=title')
    #     data = res.get_json()
    #     # print(data)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertGreater(len(data['questions']), 0)
    #     for question in data['questions']:
    #         # print(question)
    #         self.assertIn(searchTerm, question['question'].lower())


    def test_get_questions_by_cagetories(self):
        
        res = self.client().get('/categories/5/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])


    def test_post_questions(self):
        new_question = {
            'question': 'What is the 5th element ?',
            'answer': 'B',
            'difficulty': 1,
            'category': 1
        }

        res = self.client().post('/questions', json=new_question)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertGreater(data['total_questions'], 0)


    def test_post_quizzes(self):
        '''Test input category '''
        category = {'id':1}
        res = self.client().post('/quizzes', json={'quiz_category': {'id': 1}, 'previous_questions': [2]})
        data = res.get_json()
        print(data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])





# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()