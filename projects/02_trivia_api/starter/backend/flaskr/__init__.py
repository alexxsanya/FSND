import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_all_categories():
    categories = Category.query.order_by(Category.id).all()
    data = [category.id for category in categories]

    if data is None:
        abort(404)
    else:
        return jsonify({
            'success': True,
            'categories': data,
            'total_questions': len(categories)
        }), 200
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  def question_pagination(request, collection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    f_questions = [question.format() for question in collection]

    return f_questions[start:end]

  @app.route('/questions')
  def get_questions():
    categories = Category.query.order_by(Category.id).all()
    data = [category.id for category in categories]
    # current_category = request.args.get('category', 1, type=int)

    questions = Question.query.all()
    f_questions = question_pagination(request, questions)

    if data is None:
        abort(404) 
    else:
        return jsonify({
            'success': True,
            'questions': f_questions,
            'current_category': 1,
            'categories': data,
            'total_questions': len(f_questions)
        }), 200

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
        question = Question.query.get(question_id)
        question.delete()
        return jsonify({        
        'success': True,
        'status': 200,
        'deleted': question.id
        }), 200
    except:
        abort(404)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions/create', methods=['POST'])
  def add_question():
    data = request.get_json()

    question = data.get('question', None),
    answer = data.get('answer', None),
    difficulty = data.get('difficulty', None),
    category = data.get('category', None)

    try:
      #check if question already exists
      results = Question.query.filter(Question.question.ilike(f'%{question}%')).all()
      if results:

        return jsonify({
            'success': False,
            'status': 422,
            'message': f'{question} already exists',
        }), 422

      else:
        question = Question(
          question=question,
          answer=answer, 
          difficulty=difficulty,
          category=category)

        question.insert()

        categories = Category.query.order_by(Category.id).all()
        data = [category.id for category in categories]
          
        return jsonify({
          'success': True,
          'status': 201,
          'question': question.format(),
          'created': question.id,
          'categories': data
        }), 201
    except:
      abort(400)  

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods=['POST'])
  def search_questions():

    data = request.get_json()
    search = data.get('searchTerm', None)
    current_category =request.args.get('category', 1, type=int)

    try:
      results = Question.query.order_by(Question.id).filter(Question.question.ilike(f'%{search}%')).all()
      f_questions = question_pagination(request, results)


      categories = Category.query.order_by(Category.id).all()
      cat_data = [category.format() for category in categories]
      
      return jsonify({
          'success': True,
          'questions': f_questions,
          'current_category ': current_category,
          'total_questions': len(f_questions),
          'categories': cat_data
      }), 200

    except:
      abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_category_questions(category_id):
    questions = Question.query.filter(Question.category == category_id).all()
    
    f_questions = question_pagination(request, questions)
    
    if f_questions is None:
        abort(404) 
    else:
        return jsonify({
            'success': True,
            'questions': f_questions,
            'current_category': category_id,
            'total_questions': len(f_questions)
        }), 200

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes')
  def get_quiz_questions():
    data = request.get_json()
    previous_questions = data.get('previous_questions', None),
    quiz_category  = data.get('quiz_category', None),

    questions = Question.query.filter(Question.category == quiz_category).all()

    questions_list = [question.format() for question in questions]

    if questions_list is None:
        abort(404) 
    else:

      # Now find a unique question that hasn't been asked and return to user
      
        return jsonify({
            'success': True,
            'question': questions_list,
            'current_category': quiz_category,
        }), 200

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource Not Found'
    }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed'
    }), 405

  @app.errorhandler(422)
  def unprocessed(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'Request Not Processed'
    }), 422

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Server Error'
    }), 500

  
  return app

    
if __name__ == '__main__':
    app = create_app()
    app.run()