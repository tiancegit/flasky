import unittest

from app.decorators import Permission
from app.models import User, Role, AnonymousUser

'''
我们要在 tests 包中新建一个模块,编写 3 个新测试,测试最近对 User 模型所做的修改,
'''


class UserModelTestCase(unittest.TestCase):
    def test_passsword_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_role_and_permissions(self):
        Role.insert_role()
        u = User(email='john@example.com', password='cat')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
