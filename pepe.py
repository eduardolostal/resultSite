from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://tester:tester@localhost/pybossa'
db = SQLAlchemy(app)


class user_results(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)

    def __init__(self, nickname, email):
        self.nickname = nickname
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.nickname
        
        
def main():
    print "holita"
    users = user_results.query.all()
    if users:
       print "Eureka"

if __name__ == "__main__":
    main()


