import unittest
from blog import app,db,bcrypt
from blog.models import User, Post
from blog.config import Config
from flask_login import login_user,current_user
from flask import url_for,request
import time


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_user(self):
        user1 = User(username="test",email="test@gmail.com",password="password")
        db.session.add(user1)
        db.session.commit()
        self.assertEqual([user1],User.query.filter_by(username="test").all())
        self.assertEqual(user1,User.query.get(1))

    def test_create_post(self):
        user1 = User(username="test",email="test@gmail.com",password="password")
        db.session.add(user1)
        db.session.commit()
        post1 = Post(title="test blog",content="testdata",user_id=user1.id)
        db.session.add(post1)
        db.session.commit()
        self.assertEqual(post1,Post.query.get(1))

    def test_users_post(self):
        user1 = User(username="test",email="test@gmail.com",password="password")
        db.session.add(user1)
        db.session.commit()
        post1 = Post(title="test blog",content="testdata",user_id=user1.id)
        db.session.add(post1)
        db.session.commit()
        self.assertEqual(user1.posts,[post1])

    def test_main_page(self):
        with app.test_client() as c:
            response = c.get('/')
            self.assertEqual(response.status_code, 200)

    def test_blogroute(self):
        with app.test_client() as c:
            response = c.get('/blog')
            self.assertEqual(response.status_code, 200)

    def test_login(self):
        user1 = User(username="test",email="test@gmail.com",password="$2b$12$vNS5wRs6kDYL17psPISOeedVvAHlGQHHsYgZ4BjmbUIcwqWVufkZS")
        db.session.add(user1)
        db.session.commit()
        # random key for this session only
        app.config['SECRET_KEY'] = '64529050a317171fa534714b75b55b03'
        with app.test_client() as c:
            # also pass form="" as param in dict (instance of LoginForm() in login route)
            response = c.post('/login',data=dict(email='test@gmail.com', password='password',remember=True,form=""),follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(request.path,'/blog')
            self.assertEqual(current_user.username,'test')

    def test_account_login_required(self):
        with app.test_client() as c:
            response = c.get('/account',follow_redirects=True)
            # print("url:",request.path)
            self.assertEqual(request.path,'/login')
            self.assertEqual(request.url, 'http://localhost/login?next=%2Faccount')


    def test_delete_post(self):
        user1 = User(username="test",email="test@gmail.com",password="$2b$12$vNS5wRs6kDYL17psPISOeedVvAHlGQHHsYgZ4BjmbUIcwqWVufkZS")
        db.session.add(user1)
        db.session.commit()
        post1 = Post(title="test blog",content="testdata",user_id=user1.id)
        db.session.add(post1)
        db.session.commit()
        self.assertEqual(user1.posts,[post1]) # check user has post
        # random key for this session only
        app.config['SECRET_KEY'] = '64529050a317171fa534714b75b55b03'
        with app.test_client() as c:
            response = c.post('/login',data=dict(email='test@gmail.com', password='password',remember=True,form=""),follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(request.path,'/blog')
            self.assertEqual(current_user.username,'test') # check current user
            post_before = Post.query.all()
            # print("before deletion:",post_before)  checking if post is available

            #deleting
            del_response = c.post('/blog/1/delete',follow_redirects=True)
            self.assertEqual(request.path,'/blog')

            post_after = Post.query.all()
            # print("after deletion:",post_after)  checking if post is deleted
            self.assertEqual(post_after,[])


    def test_update_post(self):
        user1 = User(username="test",email="test@gmail.com",password="$2b$12$vNS5wRs6kDYL17psPISOeedVvAHlGQHHsYgZ4BjmbUIcwqWVufkZS")
        db.session.add(user1)
        db.session.commit()
        post1 = Post(title="test blog",content="testdata",user_id=user1.id)
        db.session.add(post1)
        db.session.commit()
        self.assertEqual(user1.posts,[post1]) # check user has post
        # random key for this session only
        app.config['SECRET_KEY'] = '64529050a317171fa534714b75b55b03'
        with app.test_client() as c:
            response = c.post('/login',data=dict(email='test@gmail.com', password='password',remember=True,form=""),follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(request.path,'/blog')
            self.assertEqual(current_user.username,'test') # check current user

            #updating
            del_response = c.post('/blog/1/update',data=dict(title='test updated', content='testdata updated',form=""),follow_redirects=True)
            self.assertEqual(request.path,'/blog/1')

            #checking post
            post = Post.query.get(1)
            self.assertEqual(post.title,'test updated')
            # print(post)

            
            


if __name__ == '__main__':
    unittest.main()


'''
References:
https://stackoverflow.com/questions/32290830/how-to-unit-test-a-form-submission-when-multiple-forms-on-a-route#
'''