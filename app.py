from flask import Flask,render_template
app = Flask(__name__)

@app.route('/')
def index():
    name = "Bruce"
    movies = [
        {'title':"大赢家",'year':"2020"},
        {'title':"囧妈",'year':"2020"},
        {'title':"疯狂外星人",'year':"2019"},
        {'title':"战狼",'year':"2017"}
    ]
    return render_template("index.html",name=name,movies=movies)