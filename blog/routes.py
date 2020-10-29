import os
import secrets
from PIL import Image
from flask import render_template, flash,redirect,url_for, request
from blog import app,db,bcrypt
from blog.forms import RegistrationForm,LoginForm,UpdateAccountForm
from blog.models import User,Post
from flask_login import login_user,current_user,logout_user,login_required


posts = [
    {
        'author':'Faraz Khan',
        'title': 'Blog Post one',
        'content': 'First post Content',
        'date_posted':'April 20,2020'
    },
    {
        'author':'Abdullah Tahir',
        'title': 'Blog Post two ',
        'content': 'Second post Content',
        'date_posted':'May 10,2020'
    }
]

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/blog')
def blog():
    return render_template('home.html',posts=posts)

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('blog'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You are able to Login.','success')
        return redirect(url_for('login'))
    return render_template('auth/register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            flash('You have been logged in.','success')
            next_page = request.args.get('next')
            return redirect(url_for('account')) if next_page else redirect(url_for('blog'))
        else:
            flash('Login Unsucessful. Please check email and password','danger')
    return render_template('auth/login.html',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



#function to save picture
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    # giving a random filename to every image
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profilepics',picture_fn)
    output_size = (200,200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account",methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            '''
            The code below checks if the current user pic is available and it's not the default pic
            If yes, then it's deletes the previous image to save space
            '''
            if current_user.image_file and current_user.image_file != 'default.jpg':
                current_picture_path = os.path.join(app.root_path,'static/profilepics',current_user.image_file)
                os.remove(current_picture_path)
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        '''
        Assigning values to sqlalchemy database
        '''
        flash('Your account has been updated.','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='profilepics/'+current_user.image_file)
    return render_template('account.html',image=image_file,form=form)
