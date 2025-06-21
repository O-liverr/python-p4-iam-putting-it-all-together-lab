from flask import Flask, session, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import db, User, Recipe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
api = Api(app)

class Signup(Resource):
    def post(self):
        data = request.get_json()
        if not data.get('username'):
            return make_response({'errors': ['Username must be provided']}, 422)
        try:
            user = User(
                username=data['username'],
                image_url=data.get('image_url'),
                bio=data.get('bio')
            )
            user.password_hash = data['password']
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return make_response(user.to_dict(only=('id', 'username', 'image_url', 'bio')), 201)
        except ValueError as e:
            return make_response({'errors': [str(e)]}, 422)

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            return make_response(user.to_dict(only=('id', 'username', 'image_url', 'bio')), 200)
        return make_response({'error': 'Unauthorized'}, 401)

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.authenticate(data['password']):
            session['user_id'] = user.id
            return make_response(user.to_dict(only=('id', 'username', 'image_url', 'bio')), 200)
        return make_response({'error': 'Unauthorized'}, 401)

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id')
            return make_response({}, 204)
        return make_response({'error': 'Unauthorized'}, 401)

class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            recipes = Recipe.query.all()
            return make_response([recipe.to_dict() for recipe in recipes], 200)
        return make_response({'error': 'Unauthorized'}, 401)

    def post(self):
        if session.get('user_id'):
            data = request.get_json()
            try:
                recipe = Recipe(
                    title=data['title'],
                    instructions=data['instructions'],
                    minutes_to_complete=data.get('minutes_to_complete'),
                    user_id=session['user_id']
                )
                db.session.add(recipe)
                db.session.commit()
                return make_response(recipe.to_dict(), 201)
            except ValueError as e:
                return make_response({'errors': [str(e)]}, 422)
        return make_response({'error': 'Unauthorized'}, 401)

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(debug=True)