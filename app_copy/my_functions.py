from flask import session, request, redirect, url_for

from app.models import User


def check_login():
    name = None
    email = None
    if 'name' in session:
        name = session['name']
        email = session['email']
    elif request.cookies.get('email') and request.cookies.get('name'):
        name = request.cookies.get('name')
        email = request.cookies.get('email')

    if name is None or email is None:
        return False

    user = User.query.filter(User.email == email).first()
    if user is None:
        return False
    else:
        return user
