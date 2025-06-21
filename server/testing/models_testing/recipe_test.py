import pytest
from sqlalchemy.exc import IntegrityError
from app import app
from models import db, Recipe, User

class TestRecipe:
    '''Recipe model tests'''

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="testuser")
            user.password_hash = "testpassword"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="""Or kind rest bred with am shed then. In""" + \
                    """ raptures building an bringing be. Elderly is detract""" + \
                    """ tedious assured private so to visited. Do travelling""" + \
                    """ companions contrasted it. Mistress strongly remember""" + \
                    """ up to. Ham him compass you proceed calling detract.""" + \
                    """ Better of always missed we person mr. September""" + \
                    """ smallness northward situation few her certainty""" + \
                    """ something.""",
                minutes_to_complete=60,
                user_id=user.id
            )
            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter(Recipe.title == "Delicious Shed Ham").first()
            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.instructions == """Or kind rest bred with am shed then. In""" + \
                """ raptures building an bringing be. Elderly is detract""" + \
                """ tedious assured private so to visited. Do travelling""" + \
                """ companions contrasted it. Mistress strongly remember""" + \
                """ up to. Ham him compass you proceed calling detract.""" + \
                """ Better of always missed we person mr. September smallness northward situation few her certainty something."""
            assert new_recipe.minutes_to_complete == 60
            assert new_recipe.user_id == user.id

    def test_requires_title(self):
        '''requires each record to have a title.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="testuser")
            user.password_hash = "testpassword"
            db.session.add(user)
            db.session.commit()

            # Test missing title (None)
            recipe = Recipe(instructions="A" * 50, user_id=user.id)
            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()
            db.session.rollback()

            # Test empty title
            with pytest.raises(ValueError, match="Title must be provided"):
                recipe = Recipe(
                    title="",
                    instructions="A" * 50,
                    user_id=user.id
                )

    def test_requires_50_plus_char_instructions(self):
        '''requires instructions to be at least 50 characters.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="testuser")
            user.password_hash = "testpassword"
            db.session.add(user)
            db.session.commit()

            with pytest.raises(ValueError, match="Instructions must be at least 50 characters long"):
                recipe = Recipe(
                    title="Generic Ham",
                    instructions="idk lol",
                    user_id=user.id
                )