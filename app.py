from flask import Flask,render_template,request,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy
import os,sys
import click
from werkzeug.security import generate_password_hash,check_password_hash

from flask_login import LoginManager,UserMixin,login_user,logout_user,login_required,current_user

WIN = sys.platform.startswith('win') # 判断是不是windows系统
if WIN:
    prefix = "sqlite:///" # window系统
else:
    prefix = "sqlite:////" # Mac linux系统

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 对内存做优化
app.config['SECRET_KEY'] = 'dev'

db = SQLAlchemy(app)

login_manager = LoginManager(app)  #实例化扩展类
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user
login_manager.login_view = 'login'
login_manager.login_message = '您未登录'


# models 数据层
class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self,password):
        return check_password_hash(self.password_hash,password)


class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(20))
    year = db.Column(db.String(4))

# 注册命令
@app.cli.command()
@click.option('--drop',is_flag=True,help='Create after drop')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("初始化数据库完成！")

@app.cli.command()
def forge():
    db.create_all()
    name = "Bruce"
    movies = [
        {'title':"杀破狼",'year':"2015"},
        {'title':"分手大师",'year':"2014"},
        {'title':"机器之血",'year':"2017"},
        {'title':"南极之恋",'year':"2018"},
        {'title': "大人物", 'year': "2019"},
        {'title': "大赢家", 'year': "2020"},
        {'title': "囧妈", 'year': "2020"},
        {'title': "战狼3", 'year': "2019"},
        {'title': "半个喜剧", 'year': "2019"},
        {'title': "哪吒之魔童降世", 'year': "2019"},

    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('导入数据完成')

# 生成管理员账户
@app.cli.command()
@click.option('--username',prompt=True,help='用户名')
@click.option('--password',prompt=True,help='密码',confirmation_prompt=True,hide_input=True)
def admin(username,password):
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('更新用户')
        user.username = username
        user.set_password(password)
    else:
        click.echo('创建用户')
        user = User(username=username,name="Bruce")
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('完成')


@app.route('/',methods=['GET','POST'])
def index():
    # user = User.query.first() #读取用户记录
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        title = request.form.get('title')
        year = request.form.get('year')
        # 验证数据不为空，year长度不能超过4，title长度不能超过60
        if not title or not year or len(year)>4 or len(title)>60:
            flash('输入错误')
            return redirect(url_for('index'))
        movie = Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash('数据插入成功')
        return redirect(url_for('index'))

    movies = Movie.query.all() #读取所有的电影信息记录
    return render_template("index.html",movies=movies)

# 编辑视图
@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('输入错误')
            return redirect(url_for('edit'),movie_id=movie_id)

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('数据编辑成功')
        return redirect(url_for('index'))
    return render_template('edit.html',movie=movie)

# 删除
@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('删除数据成功')
    return redirect(url_for('index'))

# 登录
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('输入错误')
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('登录成功')
            return redirect(url_for('index'))

        flash('用户名或密码错误')
        return redirect(url_for('login'))
    return render_template('login.html')

# 登出
@app.route('/logout')
def logout():
    logout_user()
    flash('退出')
    return redirect(url_for('index'))

# 设置
@app.route('/settings',methods=['GET','POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name)>20:
            flash('输入错误')
            return redirect(url_for('settings'))
        current_user.name = name
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('设置完成name成功')
        return redirect(url_for('index'))
    return render_template('settings.html')

# 处理页面404错误
@app.errorhandler(404)
def page_not_found(e):
    # user = User.query.first()
    return render_template('404.html'),404

# 模板上下文处理函数，在多个模板内部都需要使用的变量
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)