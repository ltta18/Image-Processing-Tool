from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user,  login_required
from flask_security import roles_required, roles_accepted
from PIL import ImageEnhance
from image_processing import app, db, bcrypt, user_datastore
from image_processing.form import LoginForm, RegistrationForm, UpdateAccountForm
from image_processing.models.model import *
import os
import secrets
import PIL.Image

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html", title="Image Processing Tool")

@app.route('/about')
def about():
    return render_template("about.html", title="About")
    
@app.route("/resize", methods=['GET','POST'])
def resize():
    if not current_user.is_authenticated:
        return render_template('error.html', title="Authentication Error", message="Please sign in to use this function.", route="/")
    
    if request.method == 'POST':
        #get data
        try:
            width = int(request.form['width'])
            height = int(request.form['height'])
        except ValueError:
            return render_template('error.html', title="Error!", message="Please enter an integer for width and height.")
        
        file = request.files['inputGroupFile01']
        file_name = file.filename
        if not file_name.endswith(('.png', '.jpg', '.jpeg')):
            return render_template('error.html', title="Error!", message="Please enter .png, .jpg, or .jpeg file!")
        
        #get destination to the file 
        target = os.path.dirname(os.path.abspath(__file__))
        destination = '//'.join([target, 'static//images', file_name])

        os.chdir(os.path.dirname(destination))
        for i in os.listdir():
            os.remove(i)
        file.save("%s"%file_name)
        
        try:
            img = PIL.Image.open(destination,'r')
            resized = img.resize((width, height))
            resized.save("resized_%s"%file_name)
        except: 
            return render_template('error.html', tittle="Error!", message="Cannot open file.")
        save_user_images(resized, "resized_%s"%file_name)
        img.close()
        os.remove(destination)
        destination = '/'.join(['/static/images', "resized_%s"%file_name])

        return render_template('done.html', title="Complete!", destination=destination)
    if current_user.has_role('premium'):
        return render_template('premium.html', title="Resize Images", route="/resize")
    return render_template('user.html', title="Resize Images", route="/resize")


@app.route("/crop", methods=['GET','POST'])
def crop():
    if not current_user.is_authenticated:
        return render_template('error.html', title="Authentication Error", message="Please sign in to use this function.", route="/")
    
    if request.method == 'POST':
        #get data
        width = int(request.form['dataWidth'])
        height = int(request.form['dataHeight'])
        x = int(request.form['dataX'])
        y = int(request.form['dataY'])

        file = request.files['inputGroupFile01']
        file_name = file.filename
        if not file_name.endswith(('.png', '.jpg', '.jpeg')):
            return render_template('error.html', title="Error!", message="Please enter .png, .jpg, or .jpeg file!")
        
        #get destination to the file 
        target = os.path.dirname(os.path.abspath(__file__))
        destination = '//'.join([target, 'static//images', file_name])

        os.chdir(os.path.dirname(destination))
        for i in os.listdir():
            os.remove(i)
        file.save("%s"%file_name)
        
        try:
            img = PIL.Image.open(destination,'r')
            cropped = img.crop((x, y, x+width, y+height))
            cropped.save("cropped_%s"%file_name)
        except:
            return render_template('error.html', tittle="Error!", message="Cannot open file.")
        save_user_images(cropped, "cropped_%s"%file_name)
        img.close()
        os.remove(destination)
        destination = '/'.join(['static/images', "cropped_%s"%file_name])
        return render_template('done.html', title="Complete!", destination=destination)

    if current_user.has_role('premium'):
        return render_template('premium.html', title="Crop Images", route="/crop")
    return render_template('user.html', title="Crop Images", route="/crop")

@app.route("/filter", methods=['GET','POST'])
def filter():
    if not current_user.has_role('premium'):
        return render_template('error.html', title="Authentication Error", message="Please sign in to use this function.")
    return render_template('premium.html', route="/filter")

@app.route("/register", methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pass)
        db.session.add(user)
        user_datastore.add_role_to_user(form.email.data, 'user')
        db.session.commit()
        flash('Account created for %s!'%form.username.data,'success')
        return redirect(url_for('login'))  
    return render_template('/account/register.html', title="Register", form=form)

@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    return render_template('/account/login.html', title="Login", form=form)

@app.route("/logout", methods=['GET','POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/premium', methods=['GET','POST'])
def get_premium():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_datastore.remove_role_from_user(current_user.email, 'user')
        user_datastore.add_role_to_user(current_user.email, 'premium')
        db.session.commit()
        return render_template('premium.html', title="Image Processing Tool")
    return render_template('get_premium.html', title="Premium Upgrade")

@app.route('/done')
def done():
    return render_template('done.html')


#account routes 
@app.route('/account')
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename="profile_pic/" + current_user.image_file)
    return render_template('/account/account_template.html', title='Account', image_file=image_file, form=form, route="/user/info")

@app.route('/user/history')
@login_required
def user_history():
    images = Image.query.filter_by(user_id=current_user.id).all()
    image_file = url_for('static', filename="profile_pic/" + current_user.image_file)
    return render_template('/account/account_template.html', route="/user/history", images=images, image_file=image_file)


@app.route('/delete/<int:image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    image = Image.query.get_or_404(image_id)
    if image.users != current_user:
        abort(403)
    db.session.delete(image)
    db.session.commit()
    os.remove(os.path.join(app.root_path, 'static/user_images', image.filename))
    flash('Your image has been successfully deleted', 'success')
    return redirect(url_for('user_history'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pic', picture_fn)

    output_size = (125,125)
    i = PIL.Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

def save_user_images(form_picture, image_filename):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(image_filename)
    picture_fn = random_hex + f_ext
    user_images = os.path.join(app.root_path, 'static/user_images', picture_fn)
    form_picture.save(user_images)
    image = Image(filename=picture_fn, users=current_user)
    db.session.add(image)
    db.session.commit()
    return picture_fn

