from flask import request, redirect, render_template, session, flash
from app import app, db
from models import Blog, User

# pagination
POSTS_PER_PAGE = 5

def logged_in():
    if 'username' in session:
        username = session['username']
    else:
        username = ''
    user = User.query.filter_by(username=username).first()
    return user


@app.before_request
def require_login():
    #allowed_routes = ['login', 'blog', 'index', 'signup']
    disallowed_routes = ['newpost']
    # if request.endpoint not in allowed_routes and 'username' not in session:
    if request.endpoint in disallowed_routes and 'username' not in session:
        flash('You must be logged in to post.', 'warning')
        return redirect('/login')


@app.route('/logout')
def logout():
    if logged_in():
        del session['username']
        flash('Logged out.', 'success')
    return redirect('/blog')

@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
def index(page=1):
    page_title = 'Home'
    #users = User.query.all()
    users = User.query.order_by(User.username).paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html', page_title=page_title, users=users, logged_in=logged_in())


@app.route('/login', methods=['POST', 'GET'])
def login():
    page_title = 'Login'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            # User enters a username that is stored in the database with the correct password and is redirected to the /newpost page with their username being stored in a session.
            session['username'] = username
            flash('Logged in.', 'success')
            return redirect('/newpost')
        elif user and user.password != password:
            # User enters a username that is stored in the database with an incorrect password and is redirected to the /login page with a message that their password is incorrect.
            flash('Password is incorrect.', 'danger')
            return render_template('login.html', page_title=page_title, username=username, logged_in=logged_in())
        elif not user:
            # User tries to login with a username that is not stored in the database and is redirected to the /login page with a message that this username does not exist.
            flash('Username does not exist.', 'warning')
            return render_template('login.html', page_title=page_title, username=username, logged_in=logged_in())
    if logged_in():
        flash('Already logged in as ' + session['username'] + '.', 'info')
    return render_template('login.html', page_title=page_title, logged_in=logged_in())


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    page_title = 'Signup'
    has_error = False
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        verify = request.form['verify'].strip()
        if not username or not password or not verify:
            # User leaves any of the username, password, or verify fields blank and gets an error message that one or more fields are invalid.
            flash('You must fill out all fields to signup.', 'danger')
            has_error = True
        if not password == verify:
            # User enters different strings into the password and verify fields and gets an error message that the passwords do not match.
            flash('Passwords do not match.', 'warning')
            has_error = True
        if username and User.query.filter_by(username=username).first():
            # User enters a username that already exists and gets an error message that username already exists.
            flash('Username already exists', 'info')
            has_error = True
        if len(password) < 3 or len(username) < 3:
            # User enters a password or username less than 3 characters long and gets either an invalid username or an invalid password message.
            flash('Username and password must be at least 3 characters.', 'warning')
            has_error = True
        if has_error:
            return render_template('signup.html', page_title=page_title, username=username, logged_in=logged_in())
        else:
            # User enters new, valid username, a valid password, and verifies password correctly and is redirected to the '/newpost' page with their username being stored in a session.
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    return render_template('signup.html', page_title='Signup', logged_in=logged_in())


@app.route('/blog', methods=['POST', 'GET'])
@app.route('/blog/<int:page>', methods=['POST', 'GET'])
def blog(page=1):
    page_title = 'Posts'
    user_id = request.args.get('user')
    blog_id = request.args.get('id')
    if user_id != None:
        owner = User.query.get(user_id)
        posts = Blog.query.filter(Blog.owner_id == user_id, Blog.deleted == False).order_by(Blog.pub_date.desc()).paginate(page, POSTS_PER_PAGE, False)
        return render_template('user.html', page_title=page_title + ' by ' + owner.username, posts=posts, logged_in=logged_in(), user_id=user_id)
    if blog_id != None:
        post = Blog.query.get(blog_id)
        return render_template('post.html', page_title='Post: ' + post.title, post=post, logged_in=logged_in())

    posts = Blog.query.filter_by(deleted=False).order_by(Blog.pub_date.desc()).paginate(page, POSTS_PER_PAGE, False)
    return render_template('blog.html', page_title='All ' + page_title, posts=posts, logged_in=logged_in())


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    page_title = 'Add A New Entry'
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        title = request.form['title'].strip()
        body = request.form['body'].strip()
        if not title or not body:
            flash('You must fill out all fields to create a new post.', 'warning')
            return render_template('newpost.html', page_title=page_title, title=title, body=body, logged_in=logged_in())
        else:
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
            flash('New post created.\n' + new_blog.title + ', was added at ' +
                  str(new_blog.pub_date) + ' by ' + str(session['username']), 'success')
            return redirect('/blog?id=' + str(new_blog.id))
    return render_template('newpost.html', page_title=page_title, logged_in=logged_in())

@app.route('/delete-post', methods=['POST'])
def delete_post():
    current = logged_in()
    post_id = int(request.form['post-id'])
    post = Blog.query.get(post_id)
    if post.owner_id == current.id:
        post.deleted = True
        db.session.add(post)
        db.session.commit()
        flash('Post deleted.', 'warning')
    else:
        flash('Permission denied', 'danger')
    return redirect('/blog?user='+str(current.id))

if __name__ == '__main__':
    app.run()
