import os 
import sys
import json

from flask import Flask, request, Response
import requests

from datetime import datetime
from collections import defaultdict
import random

import psycopg2
import urlparse

from node_objects import *

# ===========================================================================================

page_access_token = os.environ['FACEBOOK_PAGE_ACCESS_TOKEN']
verify_token      = os.environ['FACEBOOK_VERIFY_TOKEN']

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

app = Flask(__name__)

# ===========================================================================================

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == verify_token:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    print "Establishing database connection..."
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    db = conn.cursor()   
    print "Database connection established :)"

    data = request.get_json()

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                user = defaultdict(bool)
                connection_facts = []

                if messaging_event.get("message"):  # someone sent us a message

                    facebook_timestamp = messaging_event["timestamp"]/1000
                    user_id            = messaging_event["sender"]["id"]

                    db.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
                    user_keys = [column[0] for column in db.description]
                    user_values = db.fetchone()
                    #print "Retrieved user keys: " + str(user_keys) + " and values:" + str(user_values)

                    if user_values:
                        connection_facts.append( "known_user") 
                        print "Found user data in database."

                        user.update( dict( zip( user_keys, user_values)))
                        del user["lastname"]
                        del user["profile_pic"]
                        del user["locale"]
                        user["message_current"] = facebook_timestamp
                        if not user["message_previous"]:
                            user["message_previous"] = facebook_timestamp                 

                    else: # User is unknown
                        connection_facts.append("unknown_user") 
                        print "No user data in database. Looking up user profile..."

                        facebook_user = get_user_information( user_id)

                        print "User ID           : '" + str(user_id) + "'"
                        print "User firstname    : '" + str(facebook_user["first_name"]) + "'"
                        print "User lastname     : '" + str(facebook_user["last_name"]) + "'"
                        print "User timezone     : '" + str(facebook_user["timezone"]) + "'"   
                        print "User localization : '" + str(facebook_user["locale"]) + "'"   

                        user.update({
                            "user_id"          : user_id,
                            "firstname"        : facebook_user["first_name"],
                            "lastname"         : facebook_user["last_name"],
                            "timezone"         : facebook_user["timezone"],
                            "locale"           : facebook_user["locale"],
                            "profile_pic"      : facebook_user["profile_pic"],
                            "message_first"    : facebook_timestamp,
                            "message_previous" : facebook_timestamp,
                            "message_current"  : facebook_timestamp,
                            "node_current"     : "Welcome"
                            })

                    print "User dump before evaluating node: " + str(user)

                    node_main = eval(user["node_current"])(messaging_event["message"]["text"], user, True)

                    answer    = node_main.answer
                    next_node = node_main.next_node
                    user      = node_main.user

                    print "User dump after evaluating node: " + str(user)

                    for line in answer:
                        type_time = random.randint( 25, 40)*len(line)
                        send_action_typing_in_miliseconds( user_id, type_time)
                        send_message( user_id, line)
                        sleep(int( round( type_time + float(random.randint( 350, 650)))/1000.))

                    print "Inserting user data to database"
                    if (
                        "unknown_user" in connection_facts
                            ):  
                        db.execute( "INSERT INTO users (user_id) VALUES (%s);", (user_id,))

                    for key in user.keys():
                        if key=="user_id":
                            pass
                        elif user[key]:
                            print "Updating column '" + key + "' with value '" + str(user[key]) + "'"
                            db.execute(r"UPDATE users SET " + key + " = %s WHERE user_id = %s;", (user[key], user_id))

                    if(
                        user["node_previous"]  == "Terminator"
                        ):
                        db.execute( "DELETE FROM users WHERE user_id = %s;", (user_id,))

                    conn.commit()
                    db.close()
                    conn.close()

                    if False: # Explore the data at hand...
                        (w1, w2) = (12, 36)
                        print " {:{w1}}| {:{w1}}| {:{w2}}| {:{w1}}".format(
                            "Key", "Subkey", "Value", "Type", w1=w1, w2=w2)
                        for key in messaging_event.keys():
                            if type(messaging_event[key]).__name__ != "dict":
                                print " {:<{w1}}| {:<{w1}}| {:<{w2}}| {:<{w1}}".format(
                                    key, 
                                    "", 
                                    messaging_event[key], 
                                    type(messaging_event[key]).__name__, 
                                    w1=w1, 
                                    w2=w2)
                            else:
                                for subkey in messaging_event[key].keys():
                                    print " {:<{w1}}| {:<{w1}}| {:<{w2}}| {:<{w1}}".format(
                                        key,
                                        subkey,
                                        messaging_event[key][subkey],
                                        type(messaging_event[key][subkey]).__name__,
                                        w1=w1,
                                        w2=w2)
                        user_information = get_user_information( messaging_event["sender"]["id"])
                        for key in user_information.keys():
                            print " {:<{w1}}| {:<{w1}}| {:<{w2}}| {:<{w1}}".format(
                                "user", 
                                key, 
                                user_information[key], 
                                type(user_information[key]).__name__, 
                                w1=w1, 
                                w2=w2)                            

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return Response(status=200)



def send_message(recipient_id, message_text):

    print "Sending message..."

    params = {
        "access_token": page_access_token
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post(
        "https://graph.facebook.com/v2.6/me/messages", 
        params=params, 
        headers=headers, 
        data=data)


def send_action_typing_in_miliseconds(recipient_id, time_in_ms=1000):

    print "Pretending to type..."

    params = {
        "access_token": page_access_token
    }
    headers = {
        "Content-Type": "application/json"
    }
    typing_on = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "sender_action":"typing_on"
    })
    typing_off = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "sender_action":"typing_off"
    })    
    r = requests.post(
        "https://graph.facebook.com/v2.6/me/messages", 
        params=params, 
        headers=headers, 
        data=typing_on)
    sleep( time_in_ms)
    r = requests.post(
        "https://graph.facebook.com/v2.6/me/messages", 
        params=params, 
        headers=headers, 
        data=typing_off)


@app.route('/', methods=['GET'])
def get_user_information( recipient_id):
    query_string = ('https://graph.facebook.com/v2.6/' 
        + recipient_id
        + "?fields=first_name,last_name,profile_pic,locale,timezone,gender"
        + "&access_token="
        + page_access_token) 
    return json.loads( requests.get( query_string).content)

# ===========================================================================================


 #     #                       #                                                               
 ##   ##   ##   # #    #      # #   #####  #####  #      #  ####    ##   ##### #  ####  #    # 
 # # # #  #  #  # ##   #     #   #  #    # #    # #      # #    #  #  #    #   # #    # ##   # 
 #  #  # #    # # # #  #    #     # #    # #    # #      # #      #    #   #   # #    # # #  # 
 #     # ###### # #  # #    ####### #####  #####  #      # #      ######   #   # #    # #  # # 
 #     # #    # # #   ##    #     # #      #      #      # #    # #    #   #   # #    # #   ## 
 #     # #    # # #    #    #     # #      #      ###### #  ####  #    #   #   #  ####  #    #                                                                                             

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    print "Starting the app..." 
    port = int( os.environ.get('PORT', 5000))
    app.run( host='0.0.0.0', port=port)
