from flask import Flask, request, Response

from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage

import os 

from ngrams import corrections
import nltk

from datetime import datetime
from pytz import timezone
from collections import defaultdict
import random

import psycopg2
import urlparse

from nlp_functions import *
#from nodes import *
from node_objects import *

# http://patorjk.com/software/taag/#p=display&f=Banner&t=Connecting
# ===========================================================================================

username = os.environ['BOT_USERNAME'] 
api_key = os.environ['BOT_API_KEY']

app = Flask(__name__)
kik = KikApi(username, api_key)

config = Configuration(webhook=os.environ['WEBHOOK'])
kik.set_configuration(config)

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

# ===========================================================================================

global history
history = dict()

epoch = datetime.utcfromtimestamp(0)
def epoch_timestamp(dt):
    return (dt - epoch).total_seconds() * 1000.0

def generate_timestring_from_timestamp(timestamp):
    time = datetime.fromtimestamp(float(timestamp))
    return time.strftime("%Y-%m-%d %H:%M:%S")

sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

# ===========================================================================================

@app.route('/', methods=['POST'])
def incoming():

      #####                                                           
     #     #  ####  #    # #    # ######  ####  ##### # #    #  ####  
     #       #    # ##   # ##   # #      #    #   #   # ##   # #    # 
     #       #    # # #  # # #  # #####  #        #   # # #  # #      
     #       #    # #  # # #  # # #      #        #   # #  # # #  ### 
     #     # #    # #   ## #   ## #      #    #   #   # #   ## #    # 
      #####   ####  #    # #    # ######  ####    #   # #    #  ####  
                                                                      

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


            #     #                         #     #                                    
            #     #  ####  ###### #####     #     # #  ####  #####  ####  #####  #   # 
            #     # #      #      #    #    #     # # #        #   #    # #    #  # #  
            #     #  ####  #####  #    #    ####### #  ####    #   #    # #    #   #   
            #     #      # #      #####     #     # #      #   #   #    # #####    #   
            #     # #    # #      #   #     #     # # #    #   #   #    # #   #    #   
             #####   ####  ###### #    #    #     # #  ####    #    ####  #    #   #   
                                                                            

            system_time = epoch_timestamp(datetime.now())/1000
            kik_time = message.timestamp/1000
            print "System time : " + '{:.0f}'.format(system_time) + "   (" + generate_timestring_from_timestamp(system_time) + ")"
            print "Kik    time : " + str(kik_time) + "   (" + generate_timestring_from_timestamp(kik_time) + ")"
            print "Looking up Kik user '" + message.from_user + "' in database..."

            user_attributes = [
                "username" ,
                "firstname", 
                "lastname", 
                "timezone",                 
                "message_first",
                "message_previous",
                #"message_count",
                "message_current",                
                "how_are_you_last",
                "node_previous",
                "node_current"
            ]

            db.execute("SELECT " + ', '.join(user_attributes) + " FROM users WHERE username = %s;", (message.from_user,))
            user_values = db.fetchone()

            user = defaultdict(bool)

            if user_values:

                print "Found user data: " + str(user_values)
                connection_facts.append("known_user") 

                user.update(dict(zip(user_attributes, user_values)))
                #user["message_count"] += 1
                user["message_current"] = message.timestamp

            else:

                connection_facts.append("unknown_user") 
                print "No user data in database. Looking up " + message.from_user + " in Kik..."

                kik_user = kik.get_user(message.from_user)
                print "User firstname: " + str(kik_user.first_name)
                print "User lastname: " + str(kik_user.last_name)
                print "User timezone: " + str(kik_user.timezone)                

                user.update({
                    "username" : message.from_user,
                    "firstname" : str(kik_user.first_name),
                    "lastname" : str(kik_user.last_name),
                    "timezone" : str(kik_user.timezone),
                    #"message_count" : 1,
                    "message_first" : message.timestamp,
                    "message_previous" : message.timestamp,
                    "message_current" : message.timestamp,
                    "node_current" : "Welcome"
                    })

            if user["timezone"]=="None":
                user["timezone"] = "Europe/Berlin"



             #######                                                               #     #                      
             #       #    #   ##   #      # #    #   ##   ##### # #    #  ####     ##    #  ####  #####  ###### 
             #       #    #  #  #  #      # #    #  #  #    #   # ##   # #    #    # #   # #    # #    # #      
             #####   #    # #    # #      # #    # #    #   #   # # #  # #         #  #  # #    # #    # #####  
             #       #    # ###### #      # #    # ######   #   # #  # # #  ###    #   # # #    # #    # #      
             #        #  #  #    # #      # #    # #    #   #   # #   ## #    #    #    ## #    # #    # #      
             #######   ##   #    # ###### #  ####  #    #   #   # #    #  ####     #     #  ####  #####  ###### 
                                                  

            print "Message: " + message.body

            #answer, next_node, user = eval(user["node_current"])(sentences, user)
            node_main = eval(user["node_current"])(message.body, user)

            answer    = node_main.answer
            next_node = node_main.next_node
            user      = node_main.user

            print "Answer: " + " | ".join(answer)
            print "Next node: " + next_node



              #####                                          #     #                                           
             #     # ###### #    # #####  # #    #  ####     ##   ## ######  ####   ####    ##    ####  ###### 
             #       #      ##   # #    # # ##   # #    #    # # # # #      #      #       #  #  #    # #      
              #####  #####  # #  # #    # # # #  # #         #  #  # #####   ####   ####  #    # #      #####  
                   # #      #  # # #    # # #  # # #  ###    #     # #           #      # ###### #  ### #      
             #     # #      #   ## #    # # #   ## #    #    #     # #      #    # #    # #    # #    # #      
              #####  ###### #    # #####  # #    #  ####     #     # ######  ####   ####  #    #  ####  ###### 
                                                                                                   

            print " | ".join(answer)

            kik.send_messages([
                TextMessage(
                    to = message.from_user,
                    chat_id = message.chat_id,
                    body = line
                ) for line in answer
            ])                 


         #     #                                               ######                                                  
         #     # #####  #####    ##   ##### # #    #  ####     #     #   ##   #####   ##   #####    ##    ####  ###### 
         #     # #    # #    #  #  #    #   # ##   # #    #    #     #  #  #    #    #  #  #    #  #  #  #      #      
         #     # #    # #    # #    #   #   # # #  # #         #     # #    #   #   #    # #####  #    #  ####  #####  
         #     # #####  #    # ######   #   # #  # # #  ###    #     # ######   #   ###### #    # ######      # #      
         #     # #      #    # #    #   #   # #   ## #    #    #     # #    #   #   #    # #    # #    # #    # #      
          #####  #      #####  #    #   #   # #    #  ####     ######  #    #   #   #    # #####  #    #  ####  ###### 
                                                                                                                       

        user_attributes = user.keys()
        user_values = user.values()

        if (
            "unknown_user" in connection_facts
            ):  
            db.execute( "INSERT INTO users (username) VALUES (%s );", (message.from_user,))

        for key in user.keys():
            if user[key]:
                db.execute("UPDATE users SET " + key + " = %s WHERE username = %s;", (user[key], message.from_user))

        if(
            user["node_current"]  == "dummy"
            ):
            db.execute( "DELETE FROM users WHERE username = %s;", (message.from_user,))


    #####################################################################
    ###     Finishing activity on database and app
    #####################################################################

    conn.commit()
    db.close()
    conn.close()

    return Response(status=200)

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
    print('Starting the app...') 
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
