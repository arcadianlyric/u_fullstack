import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy import func
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
    page_size = QUESTIONS_PER_PAGE
    start = (page - 1) * page_size
    end = start + page_size
    items = [s.format() for s in selections]
    return len(items), items[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @done: Set up CORS. Allow '*' for origins. Delete the sample route after completing the dones
    '''
    cors = CORS(app, resources={r"*": {"origins": "*"}})

    '''
    @done: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        '''
        @done:
        Create an endpoint to handle GET requests
        for all available categories.
        '''
        try:
            categories = dict([(str(category.id), category.type.lower()) for category in Category.query.all()])
            return jsonify({'categories': categories})
        except Exception as err:
            print(err)
            abort(400)

    @app.route('/questions', methods=['GET'])
    def get_questions():
        '''
        @done:
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
            total_questions, questions = paginate(request, query.all())
            if not questions:
                abort(404)
            categories = dict([(str(category.id), category.type.lower()) for category in Category.query.all()])
            return jsonify({
                            'total_questions': total_questions,
                            'questions': questions,
                            'categories': categories
            })
        except Exception as err:
            print(err)
            abort(400)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        '''
        @done:
        Create an endpoint to DELETE question using a question ID.

        TEST: When you click the trash icon next to a question, the question will be removed.
        This removal will persist in the database and when you refresh the page.
        '''
        try:
            question = Question.query.get(question_id)
            if not question:
                abort(404)
            question.delete()
            return jsonify({
                            'success': True,
                            'deleted_question': question_id
            })
        except Exception as err:
            print(err)
            abort(400)

    '''
    @done:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    def post_questions():
        try:
            body = request.get_json()
            if body: 
                new_question = body.get('question', None)
                new_answer = body.get('answer', None)
                new_difficulty = body.get('difficulty', None)
                new_category = body.get('category', None)
                questions = Question(
                                    question=new_question, answer=new_answer,
                                    difficulty=new_difficulty, category=new_category)
                questions.insert()
                selections = Question.query.order_by(Question.id).all()
                current_question = paginate(request, selections)

            return jsonify({
                            'success': True,
                            'created': questions.id,
                            'questions': current_question,
                            'total_questions': len(Question.query.all())
            })
        except Exception as err:
            print(err)
            abort(400)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        '''
        @done:
        Create a POST endpoint to get questions based on a search term.
        It should return any questions for whom the search term
        is a substring of the question.
        TEST: Search by any phrase. The questions list will update to include
        only question that include that string within their question.
        Try using the word "title" to start.
        '''
        body = request.get_json()
        search_term = body.get('searchTerm')

        if search_term:
            selection = Question.query.filter(Question.question.ilike('%{}%'.format(search_term)))
            total_questions, questions = paginate(request, selection.all())
            if total_questions == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': total_questions
            })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_cagetories(category_id):
        '''
        @done:
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
        except Exception as err:
            print(err)
            abort(400)

    @app.route('/quizzes', methods=['POST'])
    def post_quizzes():
        '''
        @done:
        Create a POST endpoint to get questions to play the quiz.
        This endpoint should take category and previous question parameters
        and return a random questions within the given category,
        if provided, and that is not one of the previous questions.

        TEST: In the "Play" tab, after a user selects "All" or a category,
        one question at a time is displayed, the user is allowed to answer
        and shown whether they were correct or not.
        '''
        try:
            body = request.get_json()
            if not body:
                abort(400)

            previous_questions = body.get('previous_questions', [])
            category = body.get('quiz_category', None)
            category_id = category['id']
            if category_id == 0:
                selection = Question.query
            else:
                selection = Question.query.filter(Question.category == category_id)
            if previous_questions:
                selection = selection.filter(Question.id.notin_(previous_questions))
            all = [s.format() for s in selection.all()]
            if len(all) == 0:
                return jsonify({
                                'success': True
                })
            questions = random.choice(all)
            if questions is not None:
                return jsonify({
                                'success': True,
                                'question': questions
                })
        except Exception as err:
            print(err)
            abort(400)

    '''
    @done:
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

    @app.errorhandler(500)
    def internal_sever_error(error):
        return jsonify({
            'message': 'Internal Server Error'
        }), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'message': 'Bad request'
        }), 400

    return app
