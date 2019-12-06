from flask import Flask
import os

###     AUTHOR: AUSTIN PAUL
###     DATE: NOV 6
###     QUICKFIX_IO DIRTYBITS
###     quickfix-io.herokuapp.com

app = Flask(__name__)

#secret key - required for socketio - will be changed at deployment
app.config['SECRET_KEY'] = 'Replace later'
#app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

#db connect to postgress - changes at deployment
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://fipsywozuktmiq:a80571a707b328ffc69b488a26efb377dd0dc9c978097aa2e4492467ff750243@ec2-174-129-220-12.compute-1.amazonaws.com:5432/d158l9bo7mprq0'
# new URI - postgres://fipsywozuktmiq:a80571a707b328ffc69b488a26efb377dd0dc9c978097aa2e4492467ff750243@ec2-174-129-220-12.compute-1.amazonaws.com:5432/d158l9bo7mprq0
#deploy set to: