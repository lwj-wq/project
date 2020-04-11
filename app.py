from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
import os,sys
import click

WIN = sys.platform.startswith('win') # 判断是不是windows系统
if WIN:
    prefix = "sqlite:///" # window系统
else:
    prefix = "sqlite:////" # Mac linux系统

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 对内存做优化
db = SQLAlchemy(app)
# app.config['SECRET_KEY'] = '1903_dev'
# 注册命令
@app.cli.command()
@click.option('--drop',is_flag=True,help='Create after drop')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("初始化数据库完成！")

# models 数据层
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))

class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(20))
    year = db.Column(db.String(4))
@app.cli.command()
def forge():
    db.create_all()
    name = "sadk"
    movies = [
        {'title':"杀破狼",'year':"2010"},
        {'title':"分手大师",'year':"2017"},
        {'title':"机器之血",'year':"2017"},
        {'title':"这个杀手不太冷",'year':"2017"},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('导入数据完成')

@app.route('/')
def index():
    # user = User.query.first() #读取用户记录
    movies = Movie.query.all() #读取所有的电影信息记录
    return render_template("index.html",movies=movies)

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