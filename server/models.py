from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship('Recipe', backref='user', lazy=True)

    serialize_rules = ('-recipes.user',)

    @property
    def password_hash(self):
        raise AttributeError('password_hash is not a readable attribute')

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates('username')
    def validate_username(self, key, username):
        if not username or not username.strip():
            raise ValueError('Username must be provided')
        return username

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    serialize_rules = ('-user.recipes', 'user.id', 'user.username', 'user.image_url', 'user.bio')

    @validates('title')
    def validate_title(self, key, title):
        if title is None or (isinstance(title, str) and not title.strip()):
            raise ValueError('Title must be provided')
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if instructions is None or (isinstance(instructions, str) and not instructions.strip()):
            raise ValueError('Instructions must be provided')
        if len(instructions) < 50:
            raise ValueError('Instructions must be at least 50 characters long')
        return instructions