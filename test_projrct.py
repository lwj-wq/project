import unittest

from app import app,db,Movie,User

class ProjectTestCase(unittest.TestCase):

    # 测试固件
    def setUp(self):

        app.config.update(
            TESTING = True,
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        )
        db.create_all()
        user = User(name='Test',username='test')
        user.set_password('123456')
        movie = Movie(title='Test Movie Title',year='2020')

        db.session.add_all([user,movie])
        db.session.commit()

        self.client = app.test_client()  # 创建测试客户端
        self.runner = app.test_cli_runner() # 创建测试命令运行器

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # 测试app是否存在
    def test_app_exist(self):
        self.assertIsNotNone(app)

    # 程序是否处于测试模式
    def tesr_app_id_testing(self):
        self.assertTrue(app.config['TESTING'])

    # 测试404页面
    def test_404_page(self):
        response = self.client.get('/lalalalla')  #传入一个不存在的URL
        data = response.get_data(as_text=True)
        self.assertIn('页面跑丢了 ~~ 404',data)
        self.assertIn('返回首页',data)
        self.assertEqual(response.status_code,404)

    # 测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test的电影列表',data)
        self.assertIn('Test Movie Title',data)
        self.assertEqual(response.status_code,200)











