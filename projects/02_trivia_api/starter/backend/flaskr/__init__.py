import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, selections):
  '''
  Simple pagination.
  Returns a tuple with elements:
  - current page number
  - total items count (before pagination)
  - the current page items
  '''
  page = request.args.get('page', 1, type=int)
  # page_size = request.args.get('limit', QUESTIONS_PER_PAGE, type=int)
  page_size = QUESTIONS_PER_PAGE
  start = (page - 1) * page_size
  end = start + page_size
  items = [s.format() for s in selections]
  return page, len(items), items[start:end]
  
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response


  @app.route('/categories')
  def get_categories():
    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    try:
      categories = dict([(str(category.id), category.type) for category in Category.query.all()])
      return jsonify({
        'categories': categories
      })

    except:
      abort(400)




  # def paginate_questions(request, selection):
  #   '''
  #   Return page, iterms count, every 10 questions per page.
  #   '''
  #   page = request.args.get('page', 1, type=int)
  #   start =  (page - 1) * QUESTIONS_PER_PAGE
  #   end = start + QUESTIONS_PER_PAGE
  #   items = [s.format() for s in selection]
  #   return page, len(items), items[start:end]

  @app.route('/questions', methods=['GET'])
  def get_questions():
    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    try:
      query = Question.query
      page, questions_cnt, questions = paginate(request, query.all())
      if not questions:
        abort(404)

      categories = dict([(category.id, category.type) for category in Category.query.all()])

      return jsonify({
        'categries': categories,
        'page': page,
        'total_questions': questions_cnt,
        'questions': questions
      })

    except:
      abort(400)


 
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    try: # encountered error name 'question_id' is not defined when try missing a endent
      question = Question.query.get(question_id)
      if question:
        question.delete()
      return jsonify({
        'success': True
      })

    except:
      abort(400)


  @app.route('/questions', methods=['POST'])
  def post_questions():
    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    try:
      data = request.get_json()
      new_question = data.get('question', None)
      new_answer = data.get('answer', None)
      new_difficulty = data.get('difficulty', None)
      new_category = data.get('category', None)

      questions = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      questions.insert()
      selections = Question.query.order_by(Question.id).all()
      current_question = paginate(request, selections)

      return jsonify({
        'success': True,
        'created': questions.id,
        'questions': current_question,
        'total_questions': len(Question.query.all())
      })
    
    except:
      abort(400)


  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    try:
      query = Question.query
      data = request.get_json()
      search_term = data.get('searchTerm')
      # print(search_term)
      if search_term:
        query = query.filter(Question.question.ilike('%{}%'.format(search_term)))
      
      page, total_questions, questions = paginate(request, query.all())
    
      if len(questions) == 0:
        abort(404)
      
      categories = dict([(str(c.id), c.type.lower()) for c in Category.query.all()])
      return jsonify({
        'page': page,
        'questions': questions,
        'total_questions': total_questions,
        'current_category': categories
      })
    except Exception as err:
      print(err)

    # try:
      
    #   search_term = request.args.get('searchTerm')
    #   if search_term:
    #     # print(search_term)
    #     query = Question.query
    #     selections = query.fiter(Question.question.ilike('%{}%'.format(search_term))).all()
      
    #     page, questions_cnt, questions = paginate(request, selections)
    #     # categories = dict([(str(category.id), category.lower()) for category in Category.query.all()])
    #     if len(questions) == 0:
    #       abort(404)
      
    #     return jsonify({
    #       'page': page,
    #       'total_questions': questions_cnt,
    #       'questions': questions,
    #       'searchTerm': search_term
          
    #     })

    # except:
    #   abort(400)

  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_cagetories(category_id):
    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''

    try:
      questions = Question.query.filter(Question.category == category_id).all()
      questions = [q.format() for q in questions]
      if not questions:
        abort(404)
      return jsonify({
        'questions': questions
      })

    except:
      abort(400)


  @app.route('/quizzes', methods=['POST'])
  def post_quizzes():
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
    try:
      query = Question.query
      body = request.get_json()
      if not body:
        abort(404)

      previous_questions = body['previous_questions']
      category_id = body['quiz_category']['id']
      if not category_id:
        abort(404)
      if category_id:
        # legal category, else all categories
        # if category_id in range(1,7):
        query = query.filter(Question.category == category_id)
        if previous_questions:
          query = query.filter(Question.id.notin_(previous_questions))

      # questions = query.order_by(func.random())
      rand = [q.format() for q in query.all()]
      out = random.choice(rand)
      return jsonify({
        'questions': out
      })

    except Exception as err:
      print(err)
      abort(400)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'message': 'Not Found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'message': 'Unprocessable Entity'
    }), 422

  return app

    