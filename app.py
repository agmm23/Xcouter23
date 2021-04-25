from flask import Flask
import sqlalchemy as sql
import pandas as pd
import os.path
import sys
import configparser

app = Flask(__name__)

absPath = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'config.ini')

config = configparser.ConfigParser()
config.read(absPath)

host = config['MySQL.Info']['host']
usr = config['MySQL.Info']['user']
usrPass = config['MySQL.Info']['password']
db = config['MySQL.Info']['database']


connect_string = 'mysql+mysqlconnector://{usr}:{usrPass}@{host}/{db}'.format(usr=usr, usrPass=usrPass, host=host, db=db)

sql_engine = sql.create_engine(connect_string)
query = "select * from playbyplay limit 1" #Todo Cambiar la query por una de alchemy

df = pd.read_sql_query(query, sql_engine)

@app.route('/')
def index():
    return df['id_match'][0]

if __name__ == '__main__':
    app.run(debug=True)