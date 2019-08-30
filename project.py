#!/usr/bin/env python3

import string
import random
import sys
import json
from flask import (Flask, render_template, request, redirect, jsonify, url_for,
                   flash, make_response, session as login_session)
from flask_cors import CORS, cross_origin
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
import google_auth as gAuth

app = Flask(__name__)

# Read the secret key
try:
    app.secret_key = open('secret_key.txt', 'r').read()
except IOError as ioe:
    print('Error: File \'secret_key.txt\' must be present in the root folder')
    print(ioe.pgerror)
    print(ioe.diag.message_detail)
    sys.exit(1)

app.config['CORS_HEADERS'] = 'Content-Type'

CORS(app,
     origins="http://localhost:5000",
     allow_headers=[
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Credentials",
        "Access-Control-Allow-Origin"],
     supports_credentials=True)

# Database connection:
engine = create_engine('sqlite:///itemcatalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog')
def index():
    """
    Web app home page. Shows all the items available in the database.
    """
    generate_state()
    categories = session.query(Category).order_by(desc(Category.name))
    items = session.query(Item).order_by(desc(Item.id)).limit(10)
    return render_template('content.html',
                           categories=categories,
                           items=items,
                           client_id=gAuth.CLIENT_ID,
                           state=login_session['state'],
                           user=get_user())


@app.route('/catalog/categories/<int:category_id>')
def show_category_items(category_id):
    """
    Show the category items for a given category ID.
    """
    categories = session.query(Category).order_by(desc(Category.name))
    items = session.query(Item).filter_by(category_id=category_id)
    items = items.order_by(desc(Item.id))
    return render_template('content.html',
                           categories=categories,
                           items=items,
                           client_id=gAuth.CLIENT_ID,
                           state=login_session['state'],
                           user=get_user())


@app.route('/catalog/items/delete/<int:item_id>')
def delete_item(item_id):
    """
    Deletes a item from the catalog given an item ID.
    """
    if is_authenticated():
        item = session.query(Item).filter_by(id=item_id).one()

        if item is not None:
            if login_session['user']['email'] == item.user.email:
                session.delete(item)
                session.commit()
                return redirect(url_for('index'))
            else:
                message = 'User not authorized to delete this item'
                return redirect(url_for('index', message=[message]))
        else:
            return redirect(url_for('index', message=['Item not found']))
    else:
        message = 'User is not authenticated'
        return redirect(url_for('index', message=[message]))


@app.route('/catalog/items/new', methods=['POST'])
def create_item():
    """
    Creates an item given all of the information.
    """
    user = session.query(User).filter_by(email=request.form['email']).first()
    new_item = Item(title=request.form['title'],
                    description=request.form['description'],
                    category_id=request.form['categoryId'],
                    user=user)
    session.add(new_item)
    session.commit()

    return redirect(url_for('index'))


@app.route('/catalog/items/edit', methods=['POST'])
def edit_item():
    """
    Edit an item given new information.
    """
    if is_authenticated():
        item_id = request.form['itemIdEdit']
        item = session.query(Item).filter_by(id=item_id).one()
        if item is not None:
            if login_session['user']['email'] == item.user.email:
                item.title = request.form['titleEdit']
                item.description = request.form['descriptionEdit']
                item.category_id = request.form['categoryIdEdit']
                session.add(item)
                session.commit()
                return redirect(url_for('index'))
            else:
                message = 'User not authorized to edit this item'
                return redirect(url_for('index', message=[message]))
        else:
            return redirect(url_for('index', message=['Item not found']))
    else:
        message = 'User is not authenticated'
        return redirect(url_for('index', message=[message]))


@app.route('/catalog/authenticated')
def authenticated():
    """
    Check if the user is already authenticated.
    """
    if is_authenticated():
        return make_response(
                             jsonify(message="User is already logged in",
                                     status=200, data=True))
    else:
        return make_response(jsonify(message="User is not logged in",
                                     status=200,
                                     data=False))


@app.route('/catalog/gconnect', methods=['POST'])
def G_Login():
    """
    Does a login to the Google account.
    """
    if 'state' in request.form:
        if request.form['state'] != login_session['state']:
            return redirect(url_for('index'))

        if not is_authenticated():
            user_json = gAuth.Google_Callback()

            if user_json:
                user_data = json.loads(user_json)
                login_session['user'] = {
                    'name': user_data['name'],
                    'picture': user_data['picture'],
                    'email': user_data['email']
                }

                check_user(user_data)
            else:
                logout_session()
            return make_response(jsonify(
                message="Successfully logged in. Reload the page.",
                status=200,
                data=True
            ))
        else:
            return make_response(jsonify(
                message="Already logged in",
                status=200,
                data=False
            ))
    else:
        print('Error: \'state\' is not within the request')

        return redirect(url_for('Index'))


@app.route('/catalog/logout', methods=['POST'])
def logout():
    """
    Ends the user session. Disconnects from Google.
    """
    logout_session()

    return make_response(jsonify(
        message="User logged out",
        status=200,
        data="Logged Out"
    ))


@app.route('/catalog/json')
def catalog_json():
    """
    Reads the entire catalog from the database.
    """
    categories = session.query(Category).all()
    return jsonify(Category={int(c.id): {'name': c.name,
                   'items': [i.serialize for i in
                             session.query(Item).filter_by(category_id=c.id)]}
                             for c in categories})


@app.route('/catalog/items/<int:item_id>/json')
def get_item_by_id(item_id):
    """
    Reads in JSON format a particular item from a given ID.
    """
    item = session.query(Item).filter_by(id=item_id).first()
    return jsonify(item.serialize if item is not None else {})


def generate_state():
    """
    Generates a new random state for the session.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state


def is_authenticated():
    """
    Check if the user is authenticated.
    """
    return 'user' in login_session


def logout_session():
    """
    Ends the session variables.
    """
    if is_authenticated():
        login_session.pop('user', None)
        login_session.pop('state', None)


def get_user():
    """
    Get the user from the session variable.
    """
    return login_session.get('user', None)


def check_user(user_data):
    """
    Checks if the user is in the database; if not, then a new user is created.
    """
    user = session.query(User).filter_by(email=user_data['email']).first()

    if user is None:
        new_user = User(name=user_data['name'], email=user_data['email'],
                        picture=user_data['picture'])
        session.add(new_user)
        session.commit()

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
