from datetime import datetime
from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:XfoLalnS9rAh7u6K@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Blog %r>' % self.title


@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.method == 'GET' and request.args.get('id'):
        blog_id = request.args.get('id')
        blog_post = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog.html',title="Build-a-Blog", blogs=blog_post)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html',title="Build-a-Blog", blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html',title="Build-a-Blog")
    elif request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        new_blog = Blog(title, body)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/blog?id='+ str(new_blog.id))





if __name__ == '__main__':
    app.run()