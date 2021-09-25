from flask import Flask, render_template, session, redirect, url_for, request, jsonify
import pyrebase
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import auth
from whitenoise import WhiteNoise

app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

app.secret_key = '' # Generate a random sequence of characters

cred = credentials.Certificate('fbAdminConfig.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://REDACTED-default-rtdb.firebaseio.com/'
})
pb = pyrebase.initialize_app(json.load(open('fbConfig.json')))

def check_token(jwt):
    decoded_token = auth.verify_id_token(jwt)
    uid = decoded_token['uid']
    return uid

@app.route("/")
def index():
    listings_ref = db.reference('listings')
    data = listings_ref.get()
    search_term = request.args.get('search')
    category = request.args.get('category')
    if category not in ['electronics', 'clothes', 'furniture', 'home_appliances', 'appliances', 'others'] and category != None:
        return redirect(url_for('index', search=search_term))
    user_data = jwt_checking()
    if search_term != None and search_term != '':
        data = [i for i in data if search_term.lower() in i['name'].lower()]
    if category != None:
        data = [i for i in data if category.lower() == i['category'] and i['stock'] > 0]
    else:
        category = 'nocat'
        data = [i for i in data if i['stock'] > 0]
    return render_template('index.html', listings=data, username=user_data[1], selected=category, search_term = search_term, numitems=cart_val())

@app.route("/item")
def listing_item():
    id = request.args.get('id')
    if id == None or id=='':
        return redirect(url_for('index'))
    else:
        ref = db.reference('listings/'+id)
        data = ref.get()

        rate_ref = db.reference('ratings/'+data['uid'])
        rate_data = rate_ref.get()
        sum_stars = 0
        for i in rate_data:
            sum_stars += i['stars']
            i['stars'] = 'stars' + str(i['stars'])
        avg_stars = sum_stars / len(rate_data)
        avg_stars_txt = 'stars' + str(round(avg_stars))

        user_data = jwt_checking()

        return render_template('item.html', username=user_data[1], avgstars = avg_stars_txt, avgrating = avg_stars, numratings = len(rate_data), ratings=rate_data, item=data, numitems=cart_val(), err=request.args.get('err'))

@app.route("/cart")
def cart():
    contains_scam_listing = False
    user_data = jwt_checking()
    listings_ref = db.reference('listings')
    totalprice = 0
    data = listings_ref.get()
    filtered_data = []
    print(session['cartitems'])
    for i in session['cartitems']:
        if not data[int(i)]['verified']:
            contains_scam_listing = True
        filtered_data.append(data[int(i)])
        totalprice += float(data[int(i)]['price'])
    return render_template('cart.html', username=user_data[1], cart=filtered_data, numitems=cart_val(), totalprice=totalprice, contains_scam_listing=contains_scam_listing)


@app.route("/login")
def login():
    redir = request.args.get('redir')
    err = request.args.get('error')
    if err != None:
        err = bool(err)
        return render_template("login.html", error=err, username=None, redir=redir, numitems=cart_val())
    else:
        return render_template("login.html", username=None, redir=redir, numitems=cart_val())

@app.route("/register")
def register():
    return render_template('register.html', username=None, numitems=cart_val())


@app.route("/create", methods=["POST", "GET"])
def create():
    user_data = jwt_checking()
    ref = db.reference('warnings/'+user_data[0])
    if user_data[1] == None:
        return redirect(url_for('login', redir="create"))
    data = int(ref.get())
    if data >= 3:
        return render_template('create.html', username=user_data[1], disable = "disabled", numitems=cart_val())
    else:
        return render_template('create.html', username=user_data[1], disable = "", numitems=cart_val())


# Setting Pages
@app.route("/settings/ratings")
def ratings():
    user_data = jwt_checking()
    ref = db.reference('ratings/'+user_data[0])
    data = ref.get()
    if data != None:
        sum_stars = 0
        for i in data:
            sum_stars += i['stars']
            i['stars'] = 'stars' + str(i['stars'])
        avg_stars = sum_stars / len(data)
        avg_stars_txt = 'stars' + str(round(avg_stars))
        if user_data[1] == None:
            return redirect(url_for('login'))
        else:
            return render_template('settings/ratings.html', username=user_data[1], avgstars = avg_stars_txt, avgrating = avg_stars, numratings = len(data), ratings=data, haveRatings=True, numitems=cart_val())
    else:
        return render_template('settings/ratings.html', username=user_data[1], haveRatings=False, numitems=cart_val())

@app.route("/settings/listings")
def my_listings():
    listings_ref = db.reference('listings')
    data = listings_ref.get()
    user_data = jwt_checking()
    data = [i for i in data if user_data[0] == i['uid']]
    ref = db.reference('warnings/'+user_data[0])
    warnings = int(ref.get())
    if warnings >= 3:
        return render_template('settings/listings.html', listings=data, username=user_data[1], disable='disabled', numitems=cart_val())
    else:
        return render_template('settings/listings.html', listings=data, username=user_data[1], disable='', numitems=cart_val())

@app.route("/settings/transactions")
def transactions():
    user_data = jwt_checking()
    if user_data[1] == None:
        return redirect(url_for('login'))
    else:
        return render_template('settings/transactions.html', username=user_data[1], numitems=cart_val())
# API QUERIES

@app.route("/api/login", methods=['POST'])
def loginhandler():
    email = request.form['email']
    password = request.form['password']
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        jwt = user['idToken']
        session['jwt'] = jwt

        print(jwt_checking()[1])

        return redirect(url_for('index'))
    except:
        return redirect(url_for('login', error=True))
@app.route("/api/register", methods=["POST"])
def registerhandler():
    email = request.form['email']
    password = request.form['password']
    user = auth.create_user (
        email=email,
        email_verified=False,
        password=password,
        display_name=request.form['name']
    )
    user = pb.auth().sign_in_with_email_and_password(email, password)
    jwt = user['idToken']
    session['jwt'] = jwt
    user_data = jwt_checking()[0]
    ref = db.reference('warnings/'+user_data)
    ref.set(0)
    return redirect(url_for('index'))

@app.route('/api/logout')
def logout():
    session.pop('jwt', None)
    return redirect(url_for('index'))

@app.route('/api/listing_verify', methods=['GET'])
def listing_verify():
    data = {'value': 'False'}
    user_data = jwt_checking()
    if user_data[1] == 'goodguyseller':
        data = {'value': 'False'}
    else: 
        data = {'value': 'True'}
    return jsonify(data), 200

@app.route('/api/create_listing', methods=['POST'])
def create_listing():
    ref = db.reference('listings')
    data = ref.get()
    if data != None:
        data = str(data[-1]['id'])
    else:
        data = -1
    usage_id = str(int(data) + 1)
    path = "listings/"+usage_id
    listings_ref = db.reference(path)
    # TODO: data_retrieve = listings_ref.get() [add id verification for future use]
    user_data = jwt_checking()
    # TODO: if data_retrieve == None: [add id verification for future use]
    is_scam = request.form['scam_verifier']
    if is_scam == "False":
        print('no. of calls') # ? SCAM NUMBER GOING UP TOO HIGH
        is_scam = False
        warning_ref = db.reference("warnings/" + user_data[0])
        warning_data = int(warning_ref.get())
        warning_ref.set(warning_data+1)
    else:
        is_scam = True

    print(request.form)
    print(request.form['imgsrc'])

    listings_ref.set({
        'id':usage_id,
        'name':request.form['name'],
        'description':request.form['desc'],
        'price':format(float(request.form['price']), ".2f"),
        'image': request.form['imgsrc'],
        'uid':user_data[0],
        'username': user_data[1],
        'verified':is_scam,
        'stock': 1,
        'category':'electronics'
    })
    return redirect(url_for('my_listings'))

@app.route('/api/addcart')
def add_to_cart():
    k = cart_val()
    request_id = request.args.get('id')
    if request_id not in session['cartitems']:
        session['cartitems'].append(request_id)
        session['cart'] += 1
        return redirect(url_for('index'))
    else:
        return redirect(url_for('listing_item', id=request_id, err="rebuy"))

@app.route('/api/deletecart')
def delete_cart():
    id = int(request.args.get('id'))
    del session['cartitems'][id]
    session['cart'] -= 1
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    if session['cart'] != 0:
        listings_ref = db.reference('listings')
        data = listings_ref.get()
        for i in session['cartitems']:
            data[int(i)]['stock'] -= 1
        listings_ref.set(data)
        cartnum_backup = session['cart']

        totalprice = 0
        filtered_data = []
        for i in session['cartitems']:
            filtered_data.append(data[int(i)])
            totalprice += float(data[int(i)]['price'])
        session['cartitems'] = []
        session['cart'] = 0
        user_data = jwt_checking()
        return render_template('checkout.html', numitems = 0, checkeditems=cartnum_backup, cart=filtered_data, totalprice=totalprice, username=user_data[1])
    else:
        return redirect(url_for('index'))

def cart_val():
    if 'cartitems' not in session:
        session['cartitems'] = []

    if 'cart' in session:
        return session['cart']
    else:
        session['cart'] = 0
        return 0

def jwt_checking(jwt=None):
    jwt_temp = jwt
    if jwt==None and 'jwt' in session:
        jwt_temp = session['jwt']
    if jwt==None and 'jwt' not in session: 
        return ['error: no jwt present', None, None]
    decoded_token = auth.verify_id_token(jwt_temp)
    uid = decoded_token['uid']
    user = auth.get_user(uid)
    username = user.display_name
    userphotosrc = user.photo_url
    return ([uid, username, userphotosrc])


# REDIRECTION MIDDLE-PROCESSORS
@app.route('/redirection/search', methods=['POST'])
def searching():
    search_term = request.form['search_term']
    
    return redirect(url_for('index', search=search_term))

if __name__ == "__main__":
  app.run(debug=True)

