# Flask Basic eCommerce Application

In this tutorial you will learn building an E-Commerce API using Flask.

# Install PyMongo
Firstly you will need to install PyMongo using pip so that you can use MongoDb in your API.
```sh
python -m pip install pymongo
```

# Import MongoDB
After installing PyMongo you need to import the Mongo DataBase that is present in this repository into your 
mongo server so that you can start building the API over it.
```sh
mongorestore --db ecom_app ecom_app/
```
This will create a new DB with the name `ecom_app` in your Mongo. You should study and understand the data in all the collections
of this newly create DB.


# Install Flask-CORS
Now, you need to enable CORS in your api. For this you need to install Flas-CORS and then import into your server using
```sh
pip install -U flask-cors
```

# Run the Server

After installing all the dependencies you need to run the API. To run the app just type `python final.py` in the terminal. 
This file will create a new DB called `ecom_final_app` which you shouldn't delete from your MongoDB.and start playing around with the final API 
using **Postman**.  


# Postman
To use postman, first, you need to import the postman collection `postman_collection` into your postman. For this you need to open the 
postman app and thhen go to the collections tab, then click on import and import the 'postman_collection'. You will notice
that the complete lists of endpoints in the ecommerce app on your left udner the heading Flask Basic eCommerce App. 
You should read the description about the endpoint by selecting the endpoint and then clicking on the endpoints name on the right. 


### You will have to make sure to not open the `final.py` and look at the code. This way you will never understand the nuances of programming and will end up suffering a lot in the future.


After this you can use the `/signup` endpoint to create a new user and start using the API. Remember to update the username/password in
postman with the username/password of the user you have created to start properly using the API.

# Begin your Project
Start by making changes in `app.py` so that it behaves exactly same as the API provided to you in the Postman collection.
We have completed the code for certain endpoints whose code you already know. You need to complete the rest endpoints.