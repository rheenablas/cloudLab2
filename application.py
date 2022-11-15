import csv
from flask import Flask, render_template, request, url_for, redirect, session, g
from flask_session import Session
import pymysql as db
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField, FloatField, SelectField
from wtforms.validators import NumberRange, Optional


application = Flask(__name__)
application.config["SECRET_KEY"] = "sec-key-cloud3204-lab"


descFlag = True
Session(application)

class QueryForm(FlaskForm):
    age = IntegerField("Age: ", validators=[Optional(strip_whitespace=True)])
    #rate = FloatField("Rate: ", validators=[Optional(strip_whitespace=True)])
    year = IntegerField("Year: ", validators=[Optional(strip_whitespace=True)])
    gender = SelectField('Gender: ', choices = [('', ''), ("Males", "Males"), ("Females", "Females")])
    stat_code = SelectField("Statistic Code: ", choices = [('', ''), ("VSA49C01", "VSA49C01"), ("VSA49C02", "VSA49C02")])
    submit = SubmitField("Query")


@application.before_request
def startUp():
    g.buttonFlag = session.get("buttonFlag", True)

'''@app.teardown_appcontext
def close_db_at_end_of_requests(e=None):
    close_db(e)'''

def openConnection(): 
    connection = db.connect(host="mydb.c7mnuswakhel.eu-west-1.rds.amazonaws.com", user="root", password="cloud3204", database="ebdb")
    cur = connection.cursor(db.cursors.DictCursor)
    return connection, cur

def closeConnection(con, cur):
    cur.close()
    con.close()


def createTable():
    connection, cursor = openConnection()
    cursor.execute("DROP TABLE IF EXISTS marriage;")
    cursor.execute("""
        create table marriage 
            (
                AGE INTEGER,
                YEAR INTEGER,
                CODE VARCHAR (8),
                GENDER VARCHAR (7),
                RATE FLOAT
            );
            """)
    connection.commit()
    closeConnection(connection, cursor)

def insertDataToTable():
    connection, cursor = openConnection()
    header, rows = readData()
    for row in rows:
        print(row)
        cursor.execute("""INSERT INTO marriage (AGE, YEAR, CODE, GENDER, RATE) VALUES (%s, %s, %s, %s, %s)""", (row[0], row[1], row[2], row[3], row[4]))
        connection.commit()
    closeConnection(connection, cursor)


def getValueData(data):
    return [list(row.values()) for row in data]

def readFromTable():
    connection, cursor = openConnection()
    cursor.execute("SELECT * FROM marriage;")
    data = cursor.fetchall()
    data = getValueData(data)
    closeConnection(connection, cursor)
    return data

def orderFromTable(header):
    connection, cursor = openConnection()
    if descFlag:
        cursor.execute(f"""SELECT * FROM marriage ORDER BY {header};""")
    else:
        cursor.execute(f"""SELECT * FROM marriage ORDER BY {header} DESC;""")
    data = cursor.fetchall()
    data = getValueData(data)
    closeConnection(connection, cursor)
    return data

def queryFromTable(query):
    connection, cursor = openConnection()
    statement = "select * from marriage where "
    if len(query) > 1:
        additionalStatements = []
        for header in query:
            if query[header] != "" and query[header] != None:
                additionalStatements.append(f"{header} = '{query[header]}'")
        statement += " and ".join(additionalStatements)
    else:
        statement = f"{list(query.keys()[0])} = '{query[0]}'"
    print(statement)
    print()
    cursor.execute(statement)
    data = cursor.fetchall()
    data = getValueData(data)
    closeConnection(connection, cursor)
    return data

# Reads csv file from directory to produce statistics 
# Does not save into database
def readData():
    with open("d.csv", "r") as csvFile:
        header = []
        rows = []
        csvReader = csv.reader(csvFile)
        header = next(csvReader)
        header[0] = "Age"
        for row in csvReader:
            row[0] = int(row[0].split()[0])
            row[3] = row[3].split()[-1]
            row[-1] = float((row[-1]))
            rows.append(row)
    csvFile.close()
    return header, rows


def getHeader():
    with open("d.csv", "r") as csvFile:
        header = []
        csvReader = csv.reader(csvFile)
        header = next(csvReader)
        header[0] = "Age"
    return header


@application.route("/", methods=["GET"])
def home():
    return render_template("home.html")
    

@application.route("/data", methods=["GET", "POST"])
def data():
    header, rows = readData()
    return render_template("data.html", header=header, rows=rows)


@application.route("/dataSaved", methods=["GET", "POST"])
def dataSaved():
    session['buttonFlag'] = False   #data is now generated
    header = getHeader()
    createTable()
    insertDataToTable()   
    txt = "Data is saved"
    rows = readFromTable()
    return render_template("dataSaved.html", header=header, rows=rows, txt=txt)


@application.route("/Sort/")
def Sort():
    header = getHeader() 
    rows = readFromTable()
    return render_template("dataSaved.html", rows=rows, header=header)


@application.route("/sort/<sortBy>")
def sort(sortBy):
    global descFlag
    header = getHeader() 
    if descFlag:
        rows = orderFromTable(sortBy)
        descFlag = False
    else:
        rows = orderFromTable(sortBy)
        descFlag = True
    return render_template("dataSaved.html", rows=rows, header=header)


@application.route("/query", methods=["GET", "POST"])
def query():
    query_result = []
    form = QueryForm()
    query = None
    header = None
    if request.method == "POST":
        if form.validate_on_submit():
            header = getHeader()
            age = form.age.data
            year = form.year.data
            stat_code = form.stat_code.data
            gender = form.gender.data
            query = {"AGE":age, "YEAR": year, "CODE": stat_code, "GENDER": gender}
            query_result = queryFromTable(query)
            print(query_result)
    return render_template("query.html", form=form, query_result=query_result, query=query, header=header)

