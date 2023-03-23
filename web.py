from flask import Flask, g, render_template
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app = Flask(__name__)


# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_test.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)


# class Content(db.Model):
#    __tablename__ = "Sites"
#    # id = db.Column(db.Integer, primary_key=True)
#    Name = db.Column(db.String(120), unique=False, nullable=False)
#    URL = db.Column(db.String(120), unique=False, nullable=False)
#    Date = db.Column(db.String(120), unique=False, nullable=False)
#    Content = db.Column(db.String(5000), unique=False, nullable=False)
#    Parse = db.Column(db.String(120), unique=False, nullable=False)

#    def __repr__(self) -> str:
#       return f'<url: {self.URL}>'


def get_db():
   if 'db' not in g:
      g.db = sqlite3.connect(
         'db_test.db',
         detect_types=sqlite3.PARSE_DECLTYPES
      )
      g.db.row_factory = sqlite3.Row

   return g.db

@app.teardown_appcontext
def close_db(error):
   if 'db' in g:
      g.db.close()
      

@app.route('/')
def hello_world():
   db = get_db()
   cur = db.execute('SELECT * FROM Sites')
   rows = cur.fetchall()
   # for row in rows:
   #      print(f"{row['Date']}, {row['Name']}, {row['URL']}.")
   # print(str(rows))
   db.close()
   return render_template('sites.html', sites = rows)


   # contents = Content.query.all()
   # return str(contents)
if __name__ == '__main__':
   app.debug = True
   app.run()