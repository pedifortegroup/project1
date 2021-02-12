from flask import render_template, request, flash, session, redirect, url_for, jsonify
import hashlib
from app import app, db
from app.models import User, Notes

from app.my_functions import check_login

@app.route('/')
def index():
    logged_in = True
    if 'name' in session:
        name = session['name']
        email = session['email']
    else:
        name = request.cookies.get('name')
        email = request.cookies.get('email')
        if name is None or email is None:
            logged_in = False
    

    return render_template('index.html', name=name, email=email, logged_in=logged_in)


@app.route('/login', methods=['POST', 'GET'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password']
        print('Submitted email ' + str(email))
        print('Submitted password ' + str(password))
        # hash submitted password
        password_hash = hashlib.sha256(password.encode())
        hashed = password_hash.hexdigest()

        # query the database for hashed password and email
        user = User.query.filter((User.email == email) & (User.password_hash == hashed)).first()

        if user is None:
            flash("Invalid email or password!")
            return render_template('login.html')
        else:
            # python sessions https://pythonbasics.org/flask-sessions/
            session['name'] = user.name
            session['email'] = user.email
            resp = redirect(url_for('dashboard'))
            # python sessions https://pythonbasics.org/flask-cookies/
            resp.set_cookie('name', user.name)
            resp.set_cookie('email', user.email)
            return resp


@app.route('/signup', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        email = request.form['email']
        print('email is {}'.format(email))
        name = request.form['name']
        phone = request.form['phone']
        gender = request.form['gender']
        home_address = request.form['home_address']
        occupation = request.form['occupation']
        office_address = request.form['office_address']

        if gender == '':
            flash('Please select gender!')
            return render_template('signup.html')

        if name == '' or phone == '' :
            flash('Please enter your name and phone number')
            return render_template('signup.html')

        if home_address is None or occupation is None or office_address is None:
            flash('Please enter details')
            return render_template('signup.html')


        if len(office_address) < 2 or len(home_address) < 2 :
            flash('Please enter title and content')
            return render_template('signup.html')

        if gender is None:
            flash('Please select gender!')
            return render_template('signup.html')
        password = request.form['password']
        password2 = request.form['password2']
        if password == '':
            flash('Please enter your password.')
            return render_template('signup.html')
        if password != password2:
            flash('Passwords does not match!')
            return render_template('signup.html')
        # "Signup success"
        password_hash = hashlib.sha256(password.encode())
        hashed = password_hash.hexdigest()
        user = User(name=name, email=email, phone=phone, password_hash=hashed,gender=gender,office_address=office_address,home_address=home_address,occupation=occupation)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful!")
        session['name'] = user.name
        session['email'] = user.email
        return redirect(url_for('dashboard'))


@app.route('/logout')
def log_user_out():
    session.pop('name', None)
    session.pop('email', None)
    resp = redirect(url_for('index'))
    resp.set_cookie('name', '')
    resp.set_cookie('email', '', expires=0)
    return resp


@app.route('/notes/create', methods=['POST'])
def create_note():
    title = request.form['title']
    content = request.form['content']
    author = request.form['author']


    # check submitted stuffs
    if title is None or content is None or author is None:
        flash('Please enter title,content and author')
        return redirect(url_for('dashboard'))

    if len(title) < 2 or len(content) < 2 :
        flash('Please enter title and content')
        return redirect(url_for('dashboard'))

    # check user session and cookies
    user = check_login()
    # if user is False redirect to login
    if user is False:
        return redirect(url_for('login_page'))
    # create note
    new_note = Notes(title=title, content=content, user_id=user.id,author=author)
    db.session.add(new_note)
    db.session.commit()
    flash('{} has been saved successfully!'.format(title))
    return redirect(url_for('dashboard'))


@app.route('/notes/all')
def get_notes():
    # check user session and cookies
    user = check_login()
    # if user is False redirect to login
    if user is False:
        return redirect(url_for('login_page'))

    user_id = user.id

    notes_obj = Notes.query.filter(Notes.user_id == user_id).all()
    notes = []
    for item in notes_obj:
        item_dict = {
            'title': item.title,
            'content': item.content,
            'created': item.created,
            'id': item.id,
            'author':item.author
        }
        notes.append(item_dict)

    return render_template('notes.html', notes=notes)


@app.route('/notes/edit/<note_id>')
def edit_note_page(note_id):
    note = Notes.query.filter_by(id=note_id).first()
    if note is None:
        flash('Note not found!')
        return render_template('notes.html')

    return render_template('edit.html', note=note)


@app.route('/notes/update/<note_id>', methods=['POST','GET'])
def update_note(note_id):
    title = request.form['title']
    content = request.form['content']
    author = request.form['author']
    # check submitted stuffs
    if title is None or content is None:
        flash('Please enter title and content')
        return redirect(url_for('get_notes'))

    if len(title) < 2 or len(content) < 2 or len(author) < 2:
        flash('Please enter title,content and author')
        return redirect(url_for('get_notes'))

    # check user session and cookies
    user = check_login()
    # if user is False redirect to login
    if user is False:
        return redirect(url_for('login_page'))

    # get the note
    note = Notes.query.filter_by(id=note_id).first()
    if note is None:
        flash('Note not found!')
        return redirect(url_for('get_notes'))

    # update the note
    note.title = title
    note.content = content
    note.author = author
    db.session.commit()
    flash('{} updated successfully!'.format(note.title))
    return redirect(url_for('get_notes'))

@app.route('/notes/delete/<note_id>')
def delete_note(note_id):
    #check user session and cookies
    user = check_login()
    #if user is false redirect to login
    if user is False: 
        return redirect(url_for('login'))
    
    #get the note
    note = Notes.query.filter_by(id = note_id).first()
    if note is None:
        flash('Note not found!')
        return redirect(url_for('get_notes'))
    if note.user_id == user.id:
        # delete note
        db.session.delete(note)
        db.session.commit()
        flash('{} was deleted'.format(note.title))
        return redirect(url_for('dashboard'))
    else:
        #user is the owner of notes.
        flash('unable to delete{}! permission denied'.format(note.title))
        return redirect(url_for('get_notes'))

@app.route('/notes/content/<note_id>')
def content_note(note_id):
    #check user session and cookies
    user = check_login()
    #if user is false redirect to login
    if user is False:
        return redirect(url_for('login'))
    note = Notes.query.filter_by(id = note_id).first()
    return render_template('content.html',note=note)

@app.route('/dashboard')
def dashboard():
    logged_in = True
    if 'name' in session:
        name = session['name']
        email = session['email']
    else:
        name = request.cookies.get('name')
        email = request.cookies.get('email')
        if name is None or email is None:
            logged_in = False

    user = check_login()

    user_id = user.id

    notes_obj = Notes.query.filter(Notes.user_id == user_id).all()
    notes = []
    for item in notes_obj:
        item_dict = {
            'title': item.title,
            'content': item.content,
            'created': item.created,
            'id': item.id,
            'author':item.author
            
        }
        notes.append(item_dict)
    return render_template('dashboard.html', name=name, email=email, logged_in=logged_in,notes=notes)
    
    
@app.route('/profile')
def profile():
    logged_in = True
    if 'name' in session:
        name = session['name']
        email = session['email']
    else:
        name = request.cookies.get('name')
        email = request.cookies.get('email')
        if name is None or email is None:
            logged_in = False

    user = check_login()

    user_id = User.id

    user_profile = User.query.filter(User.user_id == user_id).all()
    user = []
    for user in user_profile:
        user_dict = {
            'age': user.age,
            'occupation': user.content,
            'registered': user.registered,
            'id': user.id,
            'home_address':user.home_address,
            'office_address':user.office_address

            
        }
        user.append(user_dict)
    return render_template('profile.html', name=name, email=email, logged_in=logged_in,user=user)

@app.route('/create_profile/<id>', methods=['GET','POST'])
def create_profile(id):
    user= User.query.filter(User.id == id).first()
    if request.method == 'GET':
        return render_template('createprofile.html')
    
    else:

        home_address = request.form['home_address']
        occupation = request.form['occupation']
        office_address = request.form['office_address']


        # check submitted stuffs
        if home_address is None or occupation is None or office_address is None:
            flash('Please enter details')
            return render_template('createprofile.html')


        if len(office_address) < 2 or len(home_address) < 2 :
            flash('Please enter title and content')
            return render_template('createprofile.html')

        # check user session and cookies
    
        user.office_address=office_address
        user.home_address=home_address
        user.occupation=occupation
        db.session.commit()
        flash("Registration successful!")
        return redirect(url_for('profile'))
