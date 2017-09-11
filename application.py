#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, jsonify, \
    url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Product, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from flask import make_response
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Music Catalog app'

engine = create_engine('sqlite:///musiccatalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    # return "The current session state is %s" % login_session['state']

    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Validate state token

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code

    code = request.data

    try:

        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('''Failed to upgrade
                                            the authorization code.'''), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = \
            make_response(json.dumps('''Token's user ID
                                    doesn't match given user ID.'''), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = \
            make_response(json.dumps('''Token's client ID
                                        does not match app's.'''), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('''Current user
                                            is already connected.'''), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;' \
        'border-radius: 150px;-webkit-border-radius: 150px;' \
        '-moz-border-radius: 150px;"> '
    flash('you are now logged in as %s' % login_session['username'])
    print 'done!'
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = \
            make_response(json.dumps('Current user not connected.'),
                          401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showCategories'))
    else:
        response = make_response(json.dumps('''Failed to revoke
                                            token for given user.''', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/categories/JSON/')
def showCategoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[i.serialize for i in categories])


@app.route('/categories/<int:category_id>/products/JSON/')
def showProductsJSON(category_id):
    products = \
        session.query(Product).filter_by(category_id=category_id).all()
    return jsonify(products=[i.serialize for i in products])


@app.route('/categories/<int:category_id>/products/<int:product_id>/JSON/'
           )
def showSingleProductJSON(category_id, product_id):
    product = session.query(Product).filter_by(id=product_id).one()
    return jsonify(product=product.serialize)


@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return render_template('publicCatalog.html',
                               categories=categories)
    else:
        return render_template('catalog.html', categories=categories)


@app.route('/categories/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash('New category created')
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')


@app.route('/categories/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    categoryToEdit = \
        session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoryToEdit.user_id != login_session['user_id']:
        return "You are not authorized to edit this category"
    if request.method == 'POST':
        if request.form['name']:
            categoryToEdit.name = request.form['name']
            flash('Category successfully edited')
            return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html',
                               category=categoryToEdit)


@app.route('/categories/<int:category_id>/delete/', methods=['GET',
           'POST'])
def deleteCategory(category_id):
    categoryToDelete = \
        session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoryToDelete.user_id != login_session['user_id']:
        return 'You are not authorized to delete this category.'
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        flash('Category successfully deleted')
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html',
                               category=categoryToDelete)


@app.route('/categories/<int:category_id>/products/')
def showProducts(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    products = \
        session.query(Product).filter_by(category_id=category_id).all()
    creator = getUserInfo(category.user_id)
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template('publicproducts.html',
                               category=category, products=products)
    else:
        return render_template('products.html', category=category,
                               products=products)


@app.route(
    '/categories/<int:category_id>/products/new/', methods=['GET', 'POST'])
def newProduct(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if category.user_id != login_session['user_id']:
        return 'You are not authorized to create a new product.'
    if request.method == 'POST':
        newProduct = Product(name=request.form['name'],
                             description=request.form['description'],
                             price=request.form['price'],
                             category_id=category_id,
                             user_id=login_session['user_id'])
        session.add(newProduct)
        session.commit()
        flash('New product successfully added')
        return redirect(url_for('showProducts',
                        category_id=category_id))
    else:
        return render_template('newproduct.html')


@app.route(
    '/categories/<int:category_id>/products/<int:product_id>/edit/',
    methods=['GET', 'POST'])
def editProduct(category_id, product_id):
    category = session.query(Category).filter_by(id=category_id).one()
    product = session.query(Product).filter_by(id=product_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if category.user_id != login_session['user_id']:
        return 'You are not authorized to edit this product.'
    if request.method == 'POST':
        if request.form['name']:
            product.name = request.form['name']
        if request.form['description']:
            product.description = request.form['description']
        if request.form['price']:
            product.price = request.form['price']
        session.add(product)
        session.commit()
        flash('Product successfully edited')
        return redirect(url_for('showProducts',
                        category_id=category_id))
    else:
        return render_template('editproduct.html',
                               category_id=category_id,
                               product_id=product_id, product=product)


@app.route(
    '/categories/<int:category_id>/products/<int:product_id>/delete/',
    methods=['GET', 'POST'])
def deleteProduct(category_id, product_id):
    category = session.query(Category).filter_by(id=category_id).one()
    product = session.query(Product).filter_by(id=product_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if category.user_id != login_session['user_id']:
        return 'You are not authorized to delete this product.'
    if request.method == 'POST':
        session.delete(product)
        session.commit()
        flash('Product successfully deleted')
        return redirect(url_for('showProducts',
                        category_id=category_id))
    else:
        return render_template('deleteproduct.html', category=category,
                               product=product)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
