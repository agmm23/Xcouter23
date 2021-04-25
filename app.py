from flask import Flask
import sqlalchemy as sql
import pandas as pd


app = Flask(__name__)

connect_string = 'mysql+mysqlconnector://agmm23:mysqlpassword1a@agmm23.mysql.pythonanywhere-services.com/agmm23$xcouter_db'
#connect_string = 'mysql+mysqlconnector://root:password@localhost/xcouter_lub_fem_2020'

sql_engine = sql.create_engine(connect_string)
query = "select * from playbyplay limit 1" #Todo Cambiar la query por una de alchemy

df = pd.read_sql_query(query, sql_engine)

@app.route('/')
def index():
    return df['id_match'][0]

if __name__ == '__main__':
    app.run(debug=True)