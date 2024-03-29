from flask import Flask, render_template, request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import os
import bcrypt

with open('/home3/prathmes/stellarstories.mdakbari.live/StellarStories/config.json', 'r') as c:
# with open('config.json', 'r') as c:
    params = json.load(c)['params']
local_server = False
app = Flask(__name__)
app.secret_key ="manthan"



 


if(local_server):

    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
    app.config['UPLOAD_FOLDER'] = params['file_upload2']

else:
    app.config['UPLOAD_FOLDER'] = params['file_upload']
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']


# db.init_app(app)
db = SQLAlchemy(app)

class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    p_number = db.Column(db.String, nullable=False)
    msg = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=True)
    img_file = db.Column(db.String, nullable=True)
    username = db.Column(db.String, nullable=False)
    # email = db.Column(db.String, nullable=False)

class Signup(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
         return bcrypt.checkpw(password.encode('utf-8'), self.password)
         

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)  
    per_page = 3
    posts = Posts.query.order_by(Posts.date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    # days_ago = (datetime.now() - posts.date).days
    # post.days_ago = f"{days_ago} {'day' if days_ago == 1 else 'days'} ago"
  
    for post in posts.items:
        days_ago = (datetime.now() - post.date).days
        post.days_ago = f"{days_ago} {'day' if days_ago == 1 else 'days'} ago"
        post.username = post.username.strip()


    # for i in range(len(posts.items)):
    #     posts.items[i].username = posts.items[i].username.strip()

    return render_template('index.html', posts=posts, params=params)


# About 
@app.route("/about")
def about():
    return render_template('about.html')

# signup
@app.route("/signup", methods=['GET','POST'])
def signup():
    if (request.method == 'POST'):
        uname = request.form.get('uname')
        email = request.form.get('email')
        password = request.form.get('pass')


        if ' ' in uname:
            flash('Username cannot contain spaces', 'error')
            return render_template('signup.html')
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return render_template('signup.html')
        if Signup.query.filter_by(uname=uname).first():
            flash('Username already exists', 'error')
            return render_template('signup.html')
        if Signup.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('signup.html')
        # hasshed_password = generate_password_hash(password)
        new_user = Signup(uname=uname,email=email,password=password)    
        # new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')

    return render_template('signup.html')

    
#  Dashbord 
@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
    if 'user' in session and session['user']:
         dashborduser = Signup.query.filter_by(uname=session['user']).first()
         if dashborduser:  
            posts = Posts.query.filter_by(username=dashborduser.uname).all()
            return render_template('dashbord.html', params=params, posts=posts)
 
    if request.method == 'POST':
        uname = request.form.get('uname')
        upassword = request.form.get('pass')

        user = Signup.query.filter_by(uname=uname).first()
        # password = Signup.query.filter_by(password=upassword).first()

    
        if user and upassword:
            session['user'] = uname
            posts = Posts.query.filter_by(username=user.uname).all()
            print(user.uname)
            return render_template('dashbord.html', posts=posts, username=user.uname)
        else:
            flash('Invalid Username or Password', 'error')
            return render_template('login.html')
        # if uname==params['admin_name'] and upassword==params['admin_password']:
        #     session['user'] = uname
        #     posts = Posts.query.all()
        #     return render_template('dashbord.html', posts=posts)

    return render_template('login.html')    


@app.route("/allpost")
def all_post():
    post = Posts.query.order_by(Posts.date.desc()).all()
    return render_template('all_post.html', post=post)

#delete post from 
@app.route("/deletepost/<string:sno>", methods=['GET','POST'])
def deletepost(sno):
    post = Posts.query.filter_by(sno=sno).first()
    db.session.delete(post)
    db.session.commit()
    return redirect("/allpost")

# Edit Btn   
@app.route("/edit/<string:sno>", methods=['GET','POST'])
def edit(sno):
    if 'user' in session and session['user']:
        user_from_database = Signup.query.filter_by(uname=session['user']).first()
        if user_from_database:
            if request.method == "POST":
                title = request.form.get('title')
                # username = request.form.get('username')
                content = request.form.get('content')
                slug = request.form.get('slug')
                # img_file = request.form.get('img_file')
                img_file = request.files['img_file']
                date = datetime.now()            

                if img_file:
                    filename = secure_filename(img_file.filename)
                    img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


                if int(sno) == 0:
        
                    post = Posts(username=user_from_database.uname, title=title, content=content, slug=slug, img_file=filename, date=date)
                    db.session.add(post)
                    db.session.commit()
                else:
                    post = Posts.query.filter_by(sno=sno).first()
                    # post.username = username
                    post.title = title
                    post.content = content
                    post.slug = slug
                    if img_file:
                        post.img_file = filename
                    post.date = date
                    db.session.commit()
                return redirect("/dashboard")

            post = Posts.query.filter_by(sno=sno, username=user_from_database.uname).first()               
            return render_template("edit.html", params=params, post=post)
    return render_template('edit.html')


#Delete
@app.route("/delete/<string:sno>", methods=['GET','POST'])
def delete(sno):
    if 'user' in session and session['user']:
        deletepost = Signup.query.filter_by(uname=session['user']).first()
        if deletepost:
            post = Posts.query.filter_by(sno=sno).first()
            db.session.delete(post)
            db.session.commit()
        return redirect("/dashboard")


# Show Post
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    days_ago = (datetime.now() - post.date).days
    post.days_ago = f"{days_ago} {'day' if days_ago == 1 else 'days'} ago"
  
    return render_template('post.html', params=params, post=post) 


# show all post for user
@app.route('/user/<string:username>/posts', methods=['GET'])
def user_posts(username):
    user = Signup.query.filter_by(uname=username).first_or_404()
    posts = Posts.query.filter_by(username=username).all()\

    for post in posts:
        days_ago = (datetime.now() - post.date).days
        post.days_ago = f"{days_ago} {'day' if days_ago == 1 else 'days'} ago"
  
    return render_template('user_post.html', user=user, posts=posts)


@app.route("/older_post" , methods=['GET'])
def older_post():
    pass


#File upload 
@app.route("/upload", methods=['GET','POST'])
def upload():
    if 'user' in session and session['user']:
        uploadfile = Signup.query.filter_by(uname=session['user']).first()
        if uploadfile:
            if(request.method == 'POST'):
                f = request.files['file']
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
                return redirect('/dashboard')

# Logout
@app.route("/logout")
def logout():
    session.pop('user') 
    return redirect('/dashboard')  
   
#  Contact 
@app.route("/contact", methods=['GET','POST'])   
def contact():
    if(request.method == 'POST'):
      name = request.form.get('name')
      email = request.form.get('email')
      p_number = request.form.get('p_number')
      msg = request.form.get('msg')
      entry = Contact(name=name, email=email, p_number=p_number, msg=msg, date =datetime.now() )
      db.session.add(entry)
      db.session.commit()     
            
    return render_template('contact.html')
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/<path:path>')
def catch_all(path):
    return render_template('404.html'), 404
@app.route("/post")
def post():
    return render_template('post.html') 


if __name__ == '__main__':
    # app.debug = True
    app.run()