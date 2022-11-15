import csv
from flask import Flask, render_template, request, url_for, redirect, session, g
from forms import QueryForm
from flask_session import Session
import pymysql as db


app = Flask(__name__)
app.config["SECRET_KEY"] = "sec-key-cloud3204-lab"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"



descFlag = True
Session(app)

@app.before_request
def startUp():
    g.buttonFlag = session.get("buttonFlag", True)

'''@app.teardown_appcontext
def close_db_at_end_of_requests(e=None):
    close_db(e)'''

def openConnection(): 
    connection = db.connect(host="mydb.c7mnuswakhel.eu-west-1.rds.amazonaws.com", user="root", password="cloud3204", database="ebdb")
    cursor = connection.cursor(db.cursors.DictCursor)
    return connection, cursor

def closeConnection(con, cur):
    cur.close()
    con.close()


def createTable():
    connection, cursor = openConnection()
    cursor.execute("DROP TABLE IF EXISTS marriage")
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
        cursor.execute("""INSERT INTO marriage (AGE, YEAR, CODE, GENDER, RATE) VALUES (%s, %s, %s, %s, %s)""",
                row[0], row[1], row[2], row[3], row[4])
        connection.commit()
    closeConnection(connection, cursor)


def readFromTable():
    connection, cursor = openConnection()
    cursor.execute("SELECT * FROM marriage")
    data = cursor.fetchall()
    closeConnection(connection, cursor)
    return data

def orderFromTable(header):
    connection, cursor = openConnection()
    cursor.execute(f"""SELECT * FROM marriage ORDER BY {header};""")
    data = cursor.fetchall()
    closeConnection(connection, cursor)
    return data

def queryFromTable(query):
    connection, cursor = openConnection()
    cursor.execute("""select * from marriage 
                        where AGE = ? or YEAR = ? or CODE = ? or GENDER = ?;""", (query))
    data = cursor.fetchall()
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
        print(header)
        header[0] = "Age"
        for row in csvReader:
            row[0] = int(row[0].split()[0])
            row[3] = row[3].split()[-1]
            row[-1] = float((row[-1]))
            #print(row)
            #break
            rows.append(row)
    #print(header)
    csvFile.close()
    return header, rows


def getHeader():
    with open("d.csv", "r") as csvFile:
        header = []
        csvReader = csv.reader(csvFile)
        header = next(csvReader)
        header[0] = "Age"
    return header


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")
    

@app.route("/data", methods=["GET", "POST"])
def data():
    header, rows = readData()
    return render_template("data.html", header=header, rows=rows, )


@app.route("/dataSaved", methods=["GET", "POST"])
def dataSaved():
    session['buttonFlag'] = False   #data is now generated
    header = getHeader()
    createTable()
    insertDataToTable()   
    txt = "Data is saved"
    rows = readFromTable()
    return render_template("dataSaved.html", header=header, rows=rows, txt=txt)


@app.route("/Sort/")
def Sort():
    header = getHeader() 
    rows = readFromTable()
    return render_template("dataSaved.html", rows=rows, header=header)


@app.route("/sort/<sortBy>")
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


@app.route("/query", methods=["GET", "POST"])
def query():
    query_result = None
    form = QueryForm()
    query = None
    header = None
    if request.method == "POST":
        if form.validate_on_submit():
            header = getHeader()
            queryList = [form.age.data, form.year.data, form.stat_code.data, form.gender.data]
            age = form.age.data
            year = form.year.data
            stat_code = form.stat_code.data
            gender = form.gender.data
            query = {"Age":age, "Year": year, "Statistic Code": stat_code, "Gender": gender}
            query_result = queryFromTable(queryList)
    return render_template("query.html", form=form, query_result=query_result, query=query, header=header)

