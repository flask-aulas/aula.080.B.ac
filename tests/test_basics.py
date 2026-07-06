import unittest
from flask import current_app
from app import create_app, db
from app.models import User, Role


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_delete_user_removes_user_from_database(self):
        role = Role.query.filter_by(name='User').first()
        if role is None:
            role = Role(name='User')
            db.session.add(role)
            db.session.commit()

        user = User(username='to_delete', role=role)
        db.session.add(user)
        db.session.commit()

        response = self.app.test_client().post(f'/delete_user/{user.id}')

        self.assertEqual(response.status_code, 302)
        self.assertIsNone(User.query.get(user.id))

    def test_edit_user_updates_username(self):
        role = Role.query.filter_by(name='User').first()
        if role is None:
            role = Role(name='User')
            db.session.add(role)
            db.session.commit()

        user = User(username='old_name', role=role)
        db.session.add(user)
        db.session.commit()

        response = self.app.test_client().post(
            f'/edit_user/{user.id}',
            data={'new_username': 'new_name'}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.query.get(user.id).username, 'new_name')
