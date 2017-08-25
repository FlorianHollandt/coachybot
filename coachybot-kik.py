from flask import Flask, request, Response

from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage, IsTypingMessage

import os 

from datetime import datetime
from time import sleep
from pytz import timezone
from collections import defaultdict
import random

import psycopg2
from psycopg2.extensions import AsIs
import urlparse

from node_objects import *

# http://patorjk.com/software/taag/#p=display&f=Banner&t=Connecting
# ===========================================================================================

username = os.environ['BOT_USERNAME'] 
api_key = os.environ['KIK_BOT_API_KEY']

app = Flask(__name__)
kik = KikApi(username, api_key)

config = Configuration(webhook=os.environ['WEBHOOK'])
kik.set_configuration(config)

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

# ===========================================================================================

epoch = datetime.utcfromtimestamp(0)
def epoch_timestamp(dt):
    return (dt - epoch).total_seconds() * 1000.0

def generate_timestring_from_timestamp(timestamp):
    time = datetime.fromtimestamp(float(timestamp))
    return time.strftime("%Y-%m-%d %H:%M:%S")

# ===========================================================================================

@app.route('/', methods=['POST'])
def incoming():


    #####################################################################
    ###     Connecting
    #####################################################################

    if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):

        return Response(status=403)

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

    db = conn.cursor()   

    messages = messages_from_json(request.json['messages'])

    for message in messages:
        if isinstance(message, TextMessage):

            connection_facts = []

            #####################################################################
            ###     User Lookup + Update
            #####################################################################
                                                                            

            user_id = message.from_user
            system_time = epoch_timestamp(datetime.now())/1000
            kik_time = message.timestamp/1000
            print "System time : " + '{:.0f}'.format(system_time) + "   (" + generate_timestring_from_timestamp(system_time) + ")"
            print "Kik    time : " + str(kik_time) + "   (" + generate_timestring_from_timestamp(kik_time) + ")"
            print "Looking up Kik user '" + user_id + "' in database..."


            db.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
            user_keys = [column[0] for column in db.description]
            user_values = db.fetchone()


            user = defaultdict(bool)

            if user_values:

                #print "Found user data: " + str(user_values)
                connection_facts.append("known_user") 

                user.update( dict( zip( user_keys, user_values)))
                #user["message_count"] += 1
                user["message_current"] = kik_time

                node_previous = user["node_previous"]

            else:

                connection_facts.append("unknown_user") 
                print "No user data in database. Looking up " + user_id + " in Kik..."

                kik_user = kik.get_user(user_id)
                print "Username          : '" + str(kik_user.first_name) + "'"
                print "User firstname    : '" + str(kik_user.first_name) + "'"
                print "User lastname     : '" + str(kik_user.last_name) + "'"
                print "User timezone     : '" + str(kik_user.timezone) + "'"   
                print "Message timestamp : '" + str(message.timestamp) + "'"

                user.update({
                    "user_id" : user_id,
                    "firstname" : str(kik_user.first_name),
                    "lastname" : str(kik_user.last_name),
                    "timezone" : kik_user.timezone,
                    #"message_count" : 1,
                    "message_first" : kik_time,
                    "message_current" : kik_time,
                    "node_current" : "Welcome"
                    })

                node_previous = "None"

            if user["timezone"] is None:
                user["timezone"] = 2



            #####################################################################
            ###     Evaluating node
            #####################################################################

            #print "Message: " + message.body

            node_main = eval(user["node_current"])(message.body, user)

            answer    = node_main.answer
            next_node = node_main.node_next
            user      = node_main.user

            #print "Answer: " + " | ".join(answer)
            #print "Next node: " + next_node


            #####################################################################
            ###     Sending message
            #####################################################################

            for line in answer:
                #type_time = random.randint(1100,3500)
                type_time = random.randint( 25, 40)*len(line) 
                # random number is miliseconds per character, giving coachybot a superhuman typing speed
                kik.send_messages([
                    TextMessage(
                        to        = user_id,
                        chat_id   = message.chat_id,
                        body      = line,
                        type_time = type_time)
                ])        
                sleep(int( round( type_time + float(random.randint( 350, 650)))/1000.))              

        #####################################################################
        ###     Updating database
        #####################################################################
                                                                                                                       
        if (
            "unknown_user" in connection_facts
            ):  
            db.execute( "INSERT INTO users (user_id) VALUES (%s );", ( user_id,))

        for key in user.keys():
            if user[key]:
                db.execute("UPDATE users SET %s = %s WHERE user_id = %s;", (AsIs(key), user[key], user_id))

        if(
            user["node_previous"]  == "Terminator"
            ):
            db.execute( "DELETE FROM users WHERE user_id = %s;", (user_id,))


        #####################################################################
        ###     Updating message log
        #####################################################################

        db.execute("SELECT * FROM logs WHERE message_timestamp = %s;", (message.timestamp,))
        log_values = db.fetchone()
        if not log_values:
            db.execute( "INSERT INTO logs (" + 
                "message_timestamp, user_id, message, node_previous, node_current, node_next" +
                ") VALUES (%s, %s, %s, %s, %s, %s);",
             (message.timestamp,
                user_id,
                message.body,
                node_previous,
                user["node_previous"],
                user["node_current"]
                ))


    #####################################################################
    ###     Finishing activity on database and app
    #####################################################################

    conn.commit()
    db.close()
    conn.close()

    return Response(status=200)

# ===========================================================================================


#####################################################################
###     Main application
#####################################################################

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    print('Starting the app...') 
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
