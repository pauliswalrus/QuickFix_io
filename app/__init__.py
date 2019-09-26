from flask import Flask


app = Flask(__name__)

#secret key - required for socketio - will be changed at deployment
app.config['SECRET_KEY'] = 'Replace later'

#db connect to postgress - changes at deployment
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://eeuyotcvqfkbua:361187423674645ecc0637ec587f8b9d11b12767c50aecf338a298e7dde8e64d@ec2-174-129-18-42.compute-1.amazonaws.com:5432/d4daah96ejr9e0'
