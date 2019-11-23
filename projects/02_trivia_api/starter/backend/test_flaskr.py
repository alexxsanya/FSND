import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""
    question_three = Question(
        question='What is my country',
        answer='Uganda', 
        difficulty=1,
        category='1')

    new_question = {
        'question':'What is my nationality',
        'answer':'Ugandan',
        'category':'1',
        'difficulty':1,
    }

    bad_request_question = {
        'question':'What is my sex',
        'answer':'male',
        'category':'1',
        'difficulty':'should integer',
    }

    duplicate_question_request = {
        'question':'What is my age',
        'answer':'100',
        'category':'1',
        'difficulty':1,
    }
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = f"postgresql:///{self.database_name}"
        setup_db(self.app, self.database_path)

        question_one = Question(
          question='What is my second name',
          answer='Alex', 
          difficulty=1,
          category='1')

        question_two = Question(
          question='What is my age',
          answer='100', 
          difficulty=1,
          category='1')

        question_one.insert()
        question_two.insert()

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        db.session.remove()
        db.drop_all()
    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True )

    def test_add_question(self):
        res = self.client().post('/questions/create', json = self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_add_question_fail_with_bad_request(self):
        res = self.client().post('/questions/create', json = self.bad_request_question)
        self.assertEqual(res.status_code, 400)

    def test_add_duplication_fails(self):
        res = self.client().post('/questions/create', json = self.duplicate_question_request)
        self.assertEqual(res.status_code, 422)


    def test_paginated_question(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True )
        self.assertEqual(data['total_questions'], 2)

    def test_get_all_categories_questions(self):
        category_id = 1
        res = self.client().get(f'/categories/{category_id}/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True )

    def test_search_questions(self):
        res = self.client().post('/questions?category=1', json={
            'searchTerm':'age'
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['questions'][0].get('answer'), '100')
        self.assertEqual(data['success'], True )

    def test_get_quiz_for_a_category(self):
        res = self.client().post('/quizzes', json={
            'previous_questions':[],
            'quiz_category': {
                'type': 1,
                'id':2
            }
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True )

    def test_get_quiz_for_all_categories(self):
        res = self.client().post('/quizzes', json={
            'previous_questions':[],
            'quiz_category': {
                'type': 'click',
                'id':2
            }
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True )

    def test_delete_a_question(self):
        self.question_three.insert()
        res = self.client().delete('/questions/3/delete')
        self.assertEqual(res.status_code, 200)

    def test_delete_a_question_fails_noexistent_question(self):
        res = self.client().delete('/questions/100/delete')
        self.assertEqual(res.status_code, 404)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()