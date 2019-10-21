from flask import Flask

###     AUTHOR: AUSTIN PAUL
###     DATE: OCT 21
###     QUICKFIX_IO DIRTYBITS
###     SPRINT 6 OCT 21 BUILD DEPLOYED AT
###     quickfix-io.herokuapp.com

app = Flask(__name__)

#secret key - required for socketio - will be changed at deployment
app.config['SECRET_KEY'] = 'Replace later'

#db connect to postgress - changes at deployment
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://qotdqbrkicixgz:fbb6c132f1f8841a4f89a33178683b0792c5444cf35e578596a0170f7764ea35@ec2-174-129-220-12.compute-1.amazonaws.com:5432/d158l9bo7mprq0'

#deploy set to: