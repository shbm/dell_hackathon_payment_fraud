from flask import Flask, jsonify, request, abort, make_response, Response, render_template, session, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from datetime import datetime
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
import pickle
import bcrypt
import pandas as pd
import random

model = pickle.load(open("./model/pickle.pkl", "rb"))

app = Flask(__name__)
app.secret_key = 'any random string'

app.config['SESSION_TYPE'] = 'filesystem'

CORS(app)
auth = HTTPBasicAuth()

app.config["MONGO_URI"] = "mongodb://localhost:27017/ecom_app"
mongo = PyMongo(app)

dataset = pd.read_pickle('./model/dataset.pkl')

# TODO: read values from the csv and pass to predict
def get_data(amount, fraud):
    df = dataset[((dataset['amount'] > amount-500) & (dataset['amount'] < amount+500)) & (dataset['isFraud'] == fraud)].head()
    return df

def predict(amount):
    r = random.randrange(0,2)
    if(r == 0):
        r = 0
    else:
        r = 1
    samp = get_data(1000,r).sample()
    del samp['isFraud']
    return model.predict(samp)

@app.route('/', methods=['GET'])
def index():
    Product = list(mongo.db.products.find({}))
    print(Product)
    return render_template('index.html', products=Product)

@app.route('/success', methods=['GET'])
def success():
    s = request.args.get('username')
    print(" ---> ", s)
    if session['email'] == 'zzzshbm09@gmail.com':
        return render_template('failiure.html', severe=0)
    elif session['email'] == 'shbm0909@gmail.com':
        return render_template('severe_failiure.html', severe=1)
    if s == 1 or s is None:
        return render_template('success.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('email')
    return redirect(url_for('index'))

@app.route('/proceed-to-payment/<amt>', methods=['POST', 'GET'])
def proceed_to_payment(amt):
    print(amt)
    if request.method == 'POST':
        total = request.form['amount-total']
        print(total)
    if request.method == 'GET':
        print("total")
    return redirect(url_for('index'))
    # return render_template('checkout.html', amount = amt)

@app.route('/checkout', methods=['POST'])
def checkout():
    amount = request.form['amount-total']
    print(amount)
    return render_template('checkout.html', amount=amount)

@app.route('/proceed_checkout', methods=['POST', 'GET'])
def proceed_checkout():
    is_fraud = predict(request.form['total-amount'])[0]
    print("--->", is_fraud)
    if is_fraud == 0:
        return redirect(url_for('success', success=0))
    else:
        return redirect(url_for('success', success=1))

@app.route('/add_cart/<product_id>', methods=['GET'])
def add_cart(product_id):
    users = mongo.db.users
    users.update({'email': session['email']},{'$push': {'cart': product_id}})
    print(product_id)
    return product_id

@app.route('/cart', methods=['GET'])
def cart():
    users = mongo.db.users
    product = mongo.db.products
    cart = (list(users.find({'email' : session['email']}))[0]['cart'])
    products = []
    total = 0
    for i in cart:
        products.append(list(product.find({'_id': ObjectId(i)}))[0])
    for i in products:
        total += (i['price'])
    print(total)
    return render_template('cart.html', products=products, total=total)

@app.route('/fraud', methods=['GET'])
def fraud():
    print(auth.username(), "usernae")
    return render_template('index.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'email' : request.form['email']})
        print(existing_user)
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({
                'name' : request.form['name'],
                'password' : hashpass,
                'email' : request.form['email'],
                'phone_number' : request.form['phone_number'],
                'cart' : []
                })
            session['email'] = request.form['email']
            return redirect(url_for('index'))
        
        return 'That username already exists!'
    
    if request.method == 'GET':
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'email' : request.form['email']})

        if login_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
                session['email'] = request.form['email']
                return redirect(url_for('index'))

        return 'Invalid username/password combination'
    
    if request.method == 'GET':
        return render_template('login.html')


@app.route('/products', methods=['GET'])
def products():
    resp = {
        'data': list(mongo.db.products.find())
    }
    return Response(dumps(resp), mimetype='application/json')

@app.route('/product/<string:p_id>', methods=['GET'])
def get_product(p_id):
    resp = {
        'data': list( mongo.db.products.find({"_id": ObjectId(p_id)}) )
    }
    return Response(dumps(resp), mimetype='application/json')

@app.route('/products/<string:category>', methods=['GET'])
def products_cateory(category):
    return Response(dumps(mongo.db.products.find({"category": category})), mimetype='application/json')

@app.route('/cart', methods=['GET'])
@auth.login_required
def get_cart_details():
  username = auth.username()  
  resp = {
    'data': list(mongo.db.carts.find({"username": username}))
  }
  return Response(dumps(resp), mimetype='application/json')


@app.route('/cart/remove/<string:p_id>', methods=['DELETE'])
@auth.login_required
def remove_product(p_id):
  Product = mongo.db.products.find_one_or_404({"_id": ObjectId(p_id)})
  username = auth.username()
  if mongo.db.carts.find({"username": username}).count() == 0:
    abort(404)
  cart = mongo.db.carts.find_one_or_404({"username": username})
  product_list = cart['products']
  print (product_list)
  if len(product_list) != 0:
    for i, product in enumerate(product_list):
      if str(product['_id']) == str(ObjectId(p_id)):
          product_list.pop(i)
          new_cart = mongo.db.carts.update({"username": username},{"username": username, "products": product_list})
          resp = {
              'cart': list(mongo.db.carts.find({"username": username}))
          }
          return Response(dumps(resp), mimetype='application/json')
          break
    return jsonify({'result': 'product not in cart'})          
  else:
    return jsonify({'result': 'product list is empty'})

if __name__ == '__main__':
    app.run(debug = True)
