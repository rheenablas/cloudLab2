import csv
from flask import Flask, render_template, request, url_for, redirect, session, g
from forms import QueryForm
from database import close_db, get_db
from flask_session import Session
from flask_mysqldb import MySQL


app = Flask(__name__)
app.config["SECRET_KEY"] = "sec-key-cloud3204-lab"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
'''
app.config["MYSQL_HOST"] = "localhost" #"mydb.c7mnuswakhel.eu-west-1.rds.amazonaws.com"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "cloud3204"
app.config["MYSQL_DB"] = "database"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

db = MySQL(app)'''
descFlag = True
Session(app)

@app.before_request
def startUp():
    g.buttonFlag = session.get("buttonFlag", True)

@app.teardown_appcontext
def close_db_at_end_of_requests(e=None):
    close_db(e)



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
    session['buttonFlag'] = False   #data is now generated
    header, rows = readData()
    return render_template("data.html", header=header, rows=rows, )


@app.route("/dataSaved", methods=["GET", "POST"])
def dataSaved():
    #insertDataToTable()
    header, rows = readData()
    db = get_db()
    for row in rows:
        db.execute("""INSERT INTO marriage (AGE, YEAR, CODE, GENDER, RATE)
            VALUES (?, ?, ?, ?, ?);""", (row[0], row[1], row[2], row[3], row[4]))
        db.commit()

    txt = "Data is saved"
    rows = db.execute("""SELECT * FROM marriage;""").fetchall()
    #rows = readFromTable()
    return render_template("dataSaved.html", header=header, rows=rows, txt=txt)


@app.route("/Sort/")
def Sort():
    db = get_db()
    header = getHeader() 
    rows = db.execute(f"""SELECT * FROM marriage ;""").fetchall()
    return render_template("dataSaved.html", rows=rows, header=header)


@app.route("/sort/<sortBy>")
def sort(sortBy):
    global descFlag
    db = get_db()
    header = getHeader() 
    if descFlag:
        rows = db.execute(f"""SELECT * FROM marriage ORDER BY {sortBy};""").fetchall()
        descFlag = False
    else:
        rows = db.execute(f"""SELECT * FROM marriage ORDER BY {sortBy} DESC;""").fetchall()
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
            age = form.age.data
            year = form.year.data
            stat_code = form.stat_code.data
            gender = form.gender.data
            query = {"Age":age, "Year": year, "Statistic Code": stat_code, "Gender": gender}
            db = get_db()
            query_result = db.execute("""select * from marriage 
                        where AGE = ? or YEAR = ? or CODE = ? or GENDER = ?;""", (age, year, stat_code, gender)).fetchall()
    return render_template("query.html", form=form, query_result=query_result, query=query, header=header)

