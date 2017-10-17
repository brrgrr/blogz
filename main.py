from flask import Flask, request, redirect, render_template, flash
from app import app, db
from models import Blog



@app.route('/')
def index():
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    if blog_id == None:
        blogs = Blog.query.order_by(Blog.pub_date.desc()).all()
        return render_template('blog.html', page_title="Build-a-Blog", blogs=blogs)
    else:
        post = Blog.query.get(blog_id)
        return render_template('post.html', page_title="Build-a-Blog: " + post.title, post=post)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html', page_title="Build-a-Blog: Add A New Entry")
    elif request.method == 'POST':
        title = request.form['title'].strip()
        body = request.form['body'].strip()
        if not title or not body:
            # error_check = True
            flash("You must fill out all fields to create a new post.", 'error')
            return render_template('newpost.html', page_title="Build-a-Blog: Add A New Entry", title=title, body=body)
        else:
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            flash('New post, '+ new_blog.title + ', was added at ' + str(new_blog.pub_date), 'success')
            return redirect('/blog?id=' + str(new_blog.id))


if __name__ == '__main__':
    app.run()
