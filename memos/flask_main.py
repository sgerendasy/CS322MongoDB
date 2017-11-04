import flask
from flask import g
from flask import render_template
from flask import request
from flask import url_for
import random

import json
import logging

import sys

# Date handling
import arrow
from dateutil import tz  # For interpreting local times

# Mongo database
from pymongo import MongoClient

import config
CONFIG = config.configuration()

MONGO_CLIENT_URL = "mongodb://{}:{}@{}:{}/{}".format(
    CONFIG.DB_USER,
    CONFIG.DB_USER_PW,
    CONFIG.DB_HOST,
    CONFIG.DB_PORT,
    CONFIG.DB)


print("Using URL '{}'".format(MONGO_CLIENT_URL))


###
# Globals
###

app = flask.Flask(__name__)
app.secret_key = CONFIG.SECRET_KEY

####
# Database connection per server process
###

try:
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, CONFIG.DB)
    collection = db.dated

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)


###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
    print("Main page entry")
    g.memos = get_memos()
    for memo in g.memos:
        print("Memo: " + str(memo))
    return flask.render_template('index.html')


@app.route("/jstest")
def jstest():
    return flask.render_template('jstest.html')


@app.route("/addMemoPage")
def new():
    return flask.render_template('addMemoPage.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('page_not_found.html',
                                 badurl=request.base_url,
                                 linkback=url_for("index")), 404

#################
#
# Functions used within the templates
#
#################


@app.route("/addMemo")
def addMemo():
    memoToAdd = request.args.get("memo", type=str)
    date = request.args.get("date", type=str)

    if(date == "" or memoToAdd == ""):
        invalidInput = {"Invalid": "input"}
        return flask.jsonify(result=invalidInput)
    date = arrow.get(date)
    entry = {"memoID": str(random.random()), "type": "dated_memo",
             "date": date.isoformat(), "text": memoToAdd}
    collection.insert(entry)
    status = {"Status": "Worked"}
    return flask.jsonify(result=status)


@app.route("/deleteMemo")
def deleteMemo():
    checkedEntries = request.args.get("checked", type=str)
    checkedEntries = checkedEntries.split(",")
    checkedEntriesIntegers = []
    for i in checkedEntries:
        if(i.isdigit()):
            checkedEntriesIntegers.append(int(i)-1)
    checkedEntriesIntegers.sort()
    allEntries = get_memos()

    checkedEntriesIndex = 0
    allEntIndex = 0

    while(checkedEntriesIndex < len(checkedEntriesIntegers) and
          allEntIndex < len(allEntries)):
        if allEntIndex == checkedEntriesIntegers[checkedEntriesIndex]:
            collection.remove({"memoID": allEntries[allEntIndex]["memoID"]})
            checkedEntriesIndex += 1
        allEntIndex += 1

    status = {"Status": "Worked"}
    return flask.jsonify(result=status)


@app.template_filter('humanize')
def humanize_arrow_date(date):
    """
    Date is internal UTC ISO format string.
    Output should be "today", "yesterday", "in 5 days", etc.
    Arrow will try to humanize down to the minute, so we
    need to catch 'today' as a special case.
    """
    try:
        then = arrow.get(date)
        now = arrow.utcnow()
        now = now.replace(hour=0, minute=0, second=0)
        if then.date() == now.date():
            human = "Today"
        else:
            human = then.humanize(now)
            if human == "in a day":
                human = "Tomorrow"
    except:
        human = date
    return human


#############
#
# Functions available to the page code above
#
##############
def get_memos():
    """
    Returns all memos in the database, in a form that
    can be inserted directly in the 'session' object.
    """
    records = []
    for record in collection.find({"type": "dated_memo"}):
        record['date'] = arrow.get(record['date']).isoformat()
        del record['_id']
        records.append(record)
    # sorted() function use taken from Rob Murray:
    # https://stackoverflow.com/questions/35198937/
    # sort-list-of-dictionaries-by-date-in-python-3-4
    records = sorted(records, key=lambda k: k["date"])
    return records


if __name__ == "__main__":
    app.debug = CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT, host="0.0.0.0")
