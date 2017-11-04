"""
Flask web app connects to Mongo database.
Keep a simple list of dated memoranda.

Representation conventions for dates: 
   - We use Arrow objects when we want to manipulate dates, but for all
     storage in database, in session or g objects, or anything else that
     needs a text representation, we use ISO date strings.  These sort in the
     order as arrow date objects, and they are easy to convert to and from
     arrow date objects.  (For display on screen, we use the 'humanize' filter
     below.) A time zone offset will 
   - User input/output is in local (to the server) time.  
"""

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
  print("Entered add memo print")

  memoToAdd = request.args.get("memo", type=str)
  date = request.args.get("date", type=str)
  
  if(date == "" or memoToAdd == ""):
    print("Bad format: " + date + "  " + memoToAdd)
    invalidInput = {"Invalid": "input"}
    return flask.jsonify(result=invalidInput)
  date = arrow.get(date)
  # can I create a memoID by incrementing a global variable that is initialized by counting number of entries in db?
  # do I need "type?"
  entry = {"memoID":str(random.random()), "type": "dated_memo", "date": date.isoformat(), "text":memoToAdd} 
  collection.insert(entry)
  print("Added: " + str(memoToAdd) + "  date: " + str(date))
  weird = {"Why":"Need"}
  return flask.jsonify(result=weird)

@app.route("/deleteMemo")
def deleteMemo():
  print("Entered delete memo")
  checkedEntries = request.args.get("checked", type=str)
  checkedEntries = checkedEntries.split(",")
  checkedEntriesIntegers = []
  for i in checkedEntries:
    if(i.isdigit()):
      checkedEntriesIntegers.append(int(i)-1)
  checkedEntriesIntegers.sort()
  allEntries = get_memos()

  checkedEntriesIndex = 0
  allEntriesIndex = 0

  while(checkedEntriesIndex < len(checkedEntriesIntegers) and allEntriesIndex < len(allEntries)):
    if allEntriesIndex == checkedEntriesIntegers[checkedEntriesIndex]:
      collection.remove({"memoID" : allEntries[allEntriesIndex]["memoID"]})
      checkedEntriesIndex += 1
    allEntriesIndex += 1

  weird = {"Why":"Need"}
  return flask.jsonify(result=weird)


@app.template_filter( 'humanize' )
def humanize_arrow_date( date ):
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
    records = [ ]
    for record in collection.find( { "type": "dated_memo" } ):
        record['date'] = arrow.get(record['date']).isoformat()
        del record['_id']
        records.append(record)
    # taken from Rob Murray: https://stackoverflow.com/questions/35198937/sort-list-of-dictionaries-by-date-in-python-3-4
    records = sorted(records, key = lambda k: k["date"])
    return records 


if __name__ == "__main__":
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT,host="0.0.0.0")

    
