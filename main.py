# This is the main file that runs the Catalog app program.
# Credit to Lorenzo Brown from Udacity for being an excellent teacher for
# the Udacity Full Stack Web Developer Nanodegree course.

# Import all necessary ports
import sys
import os
import time
import random
import string
import json
import httplib2
import requests
from model import Catalog, Item, User, Subcatalog
from flask import Flask, render_template, request, url_for
from flask import redirect, jsonify, flash, make_response
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, desc, asc

app = Flask(__name__)


# for Database setup
Base = declarative_base()
engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# for google login via secret json file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog app"


# Create anti-forgery state token
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# For login to take place via Google sign-in after pushing Login button
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
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
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
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                 'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # To handle new accounts that are in Google but not Google Plus
    if 'name' in data:
        if data['name'] == "":
            login_session['username'] = data['email']
        else:
            login_session['username'] = data['name']
    else:
        login_session['username'] = data['email']

    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " width="100" height="100" style="border-radius:50%">'
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# For disconnect to take place after pushing logout button
@app.route('/gdisconnect/')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
                                          'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
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
        flash("Log out success!")
        return redirect(url_for('MyCatalog'))
    else:
        response = make_response(json.dumps(
                                'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        flash("Log out failed!")
        return redirect(url_for('MyCatalog'))


# Create new user if the Google ID does not match what is already in database
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Main page. Displays the main categories as well as the...
# ...latest item (ordered by date). Once login, the page will display...
# ...additional functionality such as Add New, Edit and Delete for...
# ...both Categories and Items within those Categories. These functions...
# ...will only be available if the user is the creator of those items.
# ... Otherwise, he/she will not have these rights other than for his/her
# ...own items.
@app.route('/')
@app.route('/catalog/')
def MyCatalog():
    catalog = session.query(Catalog).first()
    subcatalog = session.query(Subcatalog).filter_by(catalog_id=catalog.id)
    useremail = ""
    if 'email' in login_session:  # i.e. user is logged in
        login_button = 0  # switch off login
        user = session.query(User).filter_by(email=login_session['email']).first()
        if (user is None):
            createUser(login_session)
        user = session.query(User).filter_by(email=login_session['email']).first()
        useremail = user.email

    else:  # i.e. user is not logged in
        login_button = 1  # switch on login
        useremail = ""
    title = "Latest Items"
    items = session.query(Item).order_by(desc(Item.datetime_added)).limit(10).all()
    return render_template('index.html', catalog=catalog,
                           subcatalog=subcatalog, items=items, title=title,
                           login_button=login_button, useremail=useremail)


# Updates the catalog to show the items within a selected Category. Items are
# ordered by relevance and date added.
@app.route('/catalog/<string:subcatalog_name>/')
def UpdateCatalog(subcatalog_name):
    useremail = ""
    if 'email' in login_session:  # i.e. user is logged in
        login_button = 0  # switch off login
        user = session.query(User).filter_by(email=login_session['email']).first()
        if (user is None):
            createUser(login_session)
        user = session.query(User).filter_by(email=login_session['email']).first()
        useremail = user.email

    else:  # i.e. user is not logged in
        login_button = 1  # switch on login
        useremail = ""
    catalog = session.query(Catalog).first()
    subcatalog = session.query(Subcatalog).filter_by(catalog_id=catalog.id)
    localsub = session.query(Subcatalog).filter_by(name=subcatalog_name).first()
    items = session.query(Item).filter_by(subcatalog_id=localsub.id).limit(10).all()
    title = localsub.name + " Items (Top "+str(len(items))+" items of 10)"
    return render_template('index.html', catalog=catalog, subcatalog=subcatalog,
                           items=items, title=title, login_button=login_button,
                           useremail=useremail)


# This takes the user to the Item Description page; where he/she will be able
# to see the specific descriptions for the selected Item. If he/she is the
# owner/creator of that Item, he/she will be able to also edit or delete
# that Item.
@app.route('/catalog/<string:subcatalog_name>/<string:item_name>/', methods=['GET', 'POST'])
def UpdateItems(subcatalog_name, item_name):
    localsub = session.query(Subcatalog).filter_by(name=subcatalog_name).first()
    item = session.query(Item).filter_by(subcatalog_id=localsub.id).filter_by(name=item_name).first()
    can_edit = 0
    useremail = ""
    if 'email' in login_session:  # i.e. user is logged in
        login_button = 0  # switch off login
        user = session.query(User).filter_by(email=login_session['email']).first()
        if (user is None):
            createUser(login_session)
        user = session.query(User).filter_by(email=login_session['email']).first()
        useremail = user.email

    else:  # i.e. user is not logged in
        login_button = 1  # switch on login
        useremail = ""
    localsub = session.query(Subcatalog).filter_by(name=subcatalog_name).first()
    if localsub is None:
        can_edit = 0
    else:
        if useremail != localsub.user_email:
            can_edit = 0
        else:
            can_edit = 1
    return render_template('items.html', subcatalog_name=subcatalog_name,
                           item=item, login_button=login_button,
                           can_edit=can_edit)


# For signed-in user to add a new item. This only works if he/she has
# first created a category under his/her name. Otherwise he will not be
# able to add this Item as there will not be a unique Category to tag to.
@app.route('/catalog/additem/', methods=['GET', 'POST'])
def AddItem():
    useremail = ""
    if 'email' in login_session:  # i.e. user is logged in
        login_button = 0  # switch off login
        user = session.query(User).filter_by(email=login_session['email']).first()
        if (user is None):
            createUser(login_session)
        user = session.query(User).filter_by(email=login_session['email']).first()
        useremail = user.email

    else:  # i.e. user is not logged in
        login_button = 1  # switch on login
        useremail = ""
        return redirect('/login')
    catalog = session.query(Catalog).first()
    subcatalog = session.query(Subcatalog).filter_by(catalog_id=catalog.id).filter_by(user_email=useremail)

    if request.method == 'POST':
        localsub2 = session.query(Subcatalog).filter_by(name=request.form['mycategory']).first()
        itemToAdd = Item(name=request.form['myname'],
                         description=request.form['mydescription'],
                         subcatalog=localsub2, subcatalog_id=localsub2.id,
                         parent_catalog=request.form['mycategory'],
                         user_email=user.email, user_name=user.name,
                         user_id=user.id)
        session.add(itemToAdd)
        session.commit()
        flash("Item added!")
        return redirect(url_for('UpdateCatalog', subcatalog_name=localsub2.name,
                                login_button=login_button))
    else:
        return render_template('new_item.html', subcatalog=subcatalog,
                               login_button=login_button)


# This allows a signed-in user to edit an existing Item, where he/she can then
# amend the Item, and assign a Category tagging to it. The Item is not a
# unique one, whereas the Category is. Hence, the User will be able to create
# multiple copies of Items.
@app.route('/catalog/<string:subcatalog_name>/<string:item_name>/edit/', methods=['GET', 'POST'])
def EditItem(subcatalog_name, item_name):
    useremail = ""
    if 'email' in login_session:  # i.e. user is logged in
        login_button = 0  # switch off login
        user = session.query(User).filter_by(email=login_session['email']).first()
        if (user is None):
            createUser(login_session)
        user = session.query(User).filter_by(email=login_session['email']).first()
        useremail = user.email

    else:  # i.e. user is not logged in
        login_button = 1  # switch on login
        useremail = ""
    localsub = session.query(Subcatalog).filter_by(name=subcatalog_name).first()
    if localsub is None:
        login_button = 1
        return redirect('/login')
    else:
        if useremail != localsub.user_email:
            login_button = 1
            return redirect('/login')
        else:
            login_button = 0

    catalog = session.query(Catalog).first()
    subcatalog = session.query(Subcatalog).filter_by(catalog_id=catalog.id).filter_by(user_email=useremail)
    item = session.query(Item).filter_by(subcatalog_id=localsub.id).filter_by(name=item_name).first()
    if request.method == 'POST':
        itemToDelete = session.query(Item).filter_by(subcatalog_id=localsub.id).filter_by(name=item_name).first()
        session.delete(itemToDelete)
        session.commit()
        localsub2 = session.query(Subcatalog).filter_by(name=request.form['mycategory']).first()
        itemToEdit = Item(name=request.form['myname'],
                          description=request.form['mydescription'],
                          subcatalog=localsub2,
                          parent_catalog=request.form['mycategory'],
                          user_email=useremail, user_name=user.name)
        session.add(itemToEdit)
        session.commit()
        flash("Item edited!")
        return redirect(url_for('UpdateCatalog',
                                subcatalog_name=subcatalog_name,
                                login_button=login_button))
    else:
        return render_template('edit_item.html',
                               subcatalog_name=subcatalog_name,
                               subcatalog=subcatalog, item=item,
                               login_button=login_button)


# This allows a sign-in user to delete an Item that he/she owns. Item will be
# removed from the Category permanently.
@app.route('/catalog/<string:subcatalog_name>/<string:item_name>/delete/', methods=['GET', 'POST'])
def DeleteItem(subcatalog_name, item_name):
    useremail = ""
    if 'email' in login_session:  # i.e. user is logged in
        login_button = 0  # switch off login
        user = session.query(User).filter_by(email=login_session['email']).first()
        if (user is None):
            createUser(login_session)
        user = session.query(User).filter_by(email=login_session['email']).first()
        useremail = user.email

    else:  # i.e. user is not logged in
        login_button = 1  # switch on login
        useremail = ""
    localsub = session.query(Subcatalog).filter_by(name=subcatalog_name).first()
    if localsub is None:
        login_button = 1
        return redirect('/login')
    else:
        if useremail != localsub.user_email:
            login_button = 1
            return redirect('/login')
        else:
            login_button = 0

    if request.method == 'POST':
        itemToDelete = session.query(Item).filter_by(subcatalog_id=localsub.id).filter_by(name=item_name).first()
        session.delete(itemToDelete)
        session.commit()
        flash("Item deleted!")
        return redirect(url_for('UpdateCatalog',
                                subcatalog_name=subcatalog_name,
                                login_button=login_button))
    else:
        item = session.query(Item).filter_by(subcatalog_id=localsub.id).filter_by(name=item_name).first()
        return render_template('delete_item.html',
                               subcatalog_name=subcatalog_name, item=item,
                               login_button=login_button)


# This allows a signed-in user to add a new unique Category. A new Category
# will be added to the Catalog menu (which houses all the Categories of Items.)
@app.route('/catalog/addsubcatalog/', methods=['GET', 'POST'])
def AddSubCatalog():
    useremail = ""
    if 'email' in login_session:  # i.e. user is logged in
        login_button = 0  # switch off login
        user = session.query(User).filter_by(email=login_session['email']).first()
        if (user is None):
            createUser(login_session)
        user = session.query(User).filter_by(email=login_session['email']).first()
        useremail = user.email

    else:  # i.e. user is not logged in
        login_button = 1  # switch on login
        useremail = ""
        return redirect('/login')

    catalog = session.query(Catalog).first()
    subcatalog = session.query(Subcatalog).filter_by(catalog_id=catalog.id)
    if request.method == 'POST':
        sub2Add = Subcatalog(name=request.form['myname'],
                             catalog_id=catalog.id,
                             description=request.form['mydescription'],
                             user_email=useremail, user_name=user.name,
                             user_id=user.id)
        session.add(sub2Add)
        session.commit()
        flash("Category added!")
        return redirect(url_for('MyCatalog'))
    else:
        return render_template('new_subcatalog.html', subcatalog=subcatalog,
                               login_button=login_button)


# This allows a signed-in user to edit an existing Category; but only to a
# unique and different Category. All items previously tagged to the old
# Category will also instantly be tagged to the new Category instead. Changes
# will be reflected instantly on the Home page.
@app.route('/catalog/<string:subcatalog_name>/edit/', methods=['GET', 'POST'])
def EditSubcatalog(subcatalog_name):
    catalog = session.query(Catalog).first()
    subcatalog = session.query(Subcatalog).filter_by(catalog_id=catalog.id)
    useremail = ""
    if 'email' in login_session:  # i.e. user is logged in
        login_button = 0  # switch off login
        user = session.query(User).filter_by(email=login_session['email']).first()
        if (user is None):
            createUser(login_session)
        user = session.query(User).filter_by(email=login_session['email']).first()
        useremail = user.email
    else:  # i.e. user is not logged in
        login_button = 1  # switch on login
        useremail = ""
    localsub = session.query(Subcatalog).filter_by(name=subcatalog_name).first()
    if localsub is None:
        login_button = 1
        return redirect('/login')
    else:
        if useremail != localsub.user_email:
            login_button = 1
            return redirect('/login')
        else:
            login_button = 0

    if request.method == 'POST':
        sub2Add = Subcatalog(name=request.form['myname'],
                             catalog_id=catalog.id,
                             description=request.form['mydescription'],
                             user_email=useremail, user_name=user.name,
                             user_id=user.id)
        session.add(sub2Add)
        session.commit()
        itemsToEdit = session.query(Item).filter_by(subcatalog_id=localsub.id)
        for i in itemsToEdit:
            itemToEdit = Item(name=i.name, description=i.description,
                              subcatalog=sub2Add,
                              parent_catalog=request.form['myname'],
                              user_email=i.user_email, user_name=i.user_name)
            session.add(itemToEdit)
            session.commit()
        itemsToDelete = session.query(Item).filter_by(subcatalog_id=localsub.id)
        for i in itemsToDelete:
            session.delete(i)
            session.commit()
        subToDelete = session.query(Subcatalog).filter_by(id=localsub.id).first()
        session.delete(subToDelete)
        session.commit()
        flash("Category and all related items edited!")
        return redirect(url_for('MyCatalog'))
    else:
        return render_template('edit_subcatalog.html', localsub=localsub,
                               subcatalog=subcatalog, login_button=login_button)


# This allows a signed-in user to delete his/her own unique Category. When
# this happens, all the Items tagged to this Category will instantly be
# deleted as well. Hence be very careful when deleting this!
@app.route('/catalog/<string:subcatalog_name>/delete/', methods=['GET', 'POST'])
def DeleteSubcatalog(subcatalog_name):
    useremail = ""
    if 'email' in login_session:  # i.e. user is logged in
        login_button = 0  # switch off login
        user = session.query(User).filter_by(email=login_session['email']).first()
        if (user is None):
            createUser(login_session)
        user = session.query(User).filter_by(email=login_session['email']).first()
        useremail = user.email
    else:  # i.e. user is not logged in
        login_button = 1  # switch on login
        useremail = ""
    localsub = session.query(Subcatalog).filter_by(name=subcatalog_name).first()
    if localsub is None:
        login_button = 1
        return redirect('/login')
    else:
        if useremail != localsub.user_email:
            login_button = 1
            return redirect('/login')
        else:
            login_button = 0
    if request.method == 'POST':
        itemsToDelete = session.query(Item).filter_by(subcatalog_id=localsub.id)
        for i in itemsToDelete:
            session.delete(i)
            session.commit()
        subToDelete = session.query(Subcatalog).filter_by(id=localsub.id).first()
        session.delete(subToDelete)
        session.commit()
        flash("Category and all related items deleted!")
        return redirect(url_for('MyCatalog'))
    else:
        return render_template('delete_subcatalog.html', subcatalog=localsub,
                               login_button=login_button)


# JSON to see all the Categories in the Catalog menu.
@app.route('/catalog/JSON/')
@app.route('/catalog/json/')
@app.route('/catalog.json/')
def SubcatalogJSON():
    catalog = session.query(Catalog).first()
    subcatalog = session.query(Subcatalog).filter_by(catalog_id=catalog.id)
    return jsonify(Categories=[i.serialize for i in subcatalog])


# JSON to see all the Items within a selected Category.
@app.route('/catalog/<string:subcatalog_name>/JSON/')
@app.route('/catalog/<string:subcatalog_name>/json/')
@app.route('/catalog/<string:subcatalog_name>.json/')
def ItemJSON(subcatalog_name):
    localsub = session.query(Subcatalog).filter_by(name=subcatalog_name).first()
    items = session.query(Item).filter_by(subcatalog_id=localsub.id)
    return jsonify(Category_Items=[i.serialize for i in items])


# This allows the browser to update the CSS upon changes made;
# instead of cacheing old changes which are not relevant.
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


# This allows the browser to update the CSS upon changes made;
# instead of cacheing old changes which are not relevant.
def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


# This helps set up the local server. Secret key is meant for authentication
# purposes.
if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host="0.0.0.0", port=8080)
