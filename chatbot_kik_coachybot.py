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
from nodes import *

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

epoch = datetime.datetime.utcfromtimestamp(0)
def epoch_timestamp(dt):
    return (dt - epoch).total_seconds() * 1000.0

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

            message_facts = []


            #     #                         #     #                                    
            #     #  ####  ###### #####     #     # #  ####  #####  ####  #####  #   # 
            #     # #      #      #    #    #     # # #        #   #    # #    #  # #  
            #     #  ####  #####  #    #    ####### #  ####    #   #    # #    #   #   
            #     #      # #      #####     #     # #      #   #   #    # #####    #   
            #     # #    # #      #   #     #     # # #    #   #   #    # #   #    #   
             #####   ####  ###### #    #    #     # #  ####    #    ####  #    #   #   
                                                                            

             epoch = 

            print "System time: " + epoch_timestamp(datetime.now())
            print "Kik time   : " + message.timestamp
            print "Looking up Kik user '" + message.from_user + "' in database..."

            user_attributes = [
                "kik_id" ,
                "kik_firstname", 
                "kik_lastname", 
                "kik_timezone",                 
                "name", 
                "gender", 
                "dialogue_count", 
                "dialogue_start", 
                "message_previous",
                "message_count",
                "greeting_last",
                "how_are_you_last",
                "topic_current",
                "topic_start",
                "question_open_start",
                "question_open_topic",
                "node_current",
                "node_previous"
            ]

            db.execute("SELECT " + ', '.join(user_attributes) + " FROM users WHERE kik_id = %s;", (message.from_user,))
            user_values = db.fetchone()

            user = defaultdict(bool)

            if user_values:

                print "Found user data: " + str(user_values)
                message_facts.append("known_user") 

                user.update(dict(zip(user_attributes, user_values)))
                user["message_count"] += 1
                user["message_current"] = message.timestamp

            else:

                message_facts.append("unknown_user") 
                print "No user data in database. Looking up " + message.from_user + " in Kik..."

                kik_user = kik.get_user(message.from_user)
                print "User firstname: " + str(kik_user.first_name)
                print "User lastname: " + str(kik_user.last_name)
                print "User timezone: " + str(kik_user.timezone)                

                user.update({
                    "kik_id" : message.from_user,
                    "kik_firstname" : str(kik_user.first_name),
                    "kik_lastname" : str(kik_user.last_name),
                    "kik_timezone" : str(kik_user.timezone),
                    "message_count" : 1,
                    "message_first" : message.timestamp,
                    "message_previous" : message.timestamp,
                    "message_current" : message.timestamp,
                    "dialogue_start" : message.timestamp,
                    "dialogue_count" : 1,
                    "node_current" : "greeting"
                    })

            if user["kik_timezone"]=="None":
                user["kik_timezone"] = "Europe/Berlin"


             ######                                                             
             #     # #  ####  #####  #    # #####  ##### #  ####  #    #  ####  
             #     # # #      #    # #    # #    #   #   # #    # ##   # #      
             #     # #  ####  #    # #    # #    #   #   # #    # # #  #  ####  
             #     # #      # #####  #    # #####    #   # #    # #  # #      # 
             #     # # #    # #   #  #    # #        #   # #    # #   ## #    # 
             ######  #  ####  #    #  ####  #        #   #  ####  #    #  ####  
                                                                    
            disruptions = []

            sentences = preprocess_message(message.body)

            for sentence in sentences:
                if is_how_are_you(sentence):
                    disruptions.append("has_question_how_are_you")  
                if is_greeting(sentence):
                    disruptions.append("has_greeting")

            time_since_last_message = message.timestamp - user["message_previous"]

            if(
                time_since_last_message >= 11*60*60*1000
                ):

                user.update({
                    "node_previous" : user["node_current"],
                    "node_current" : "greeting"
                    })

            elif(
                    (
                        time_since_last_message >= 2*60*60*1000
                        and time_since_last_message < 5*60*60*1000
                        and (
                            "has_greeting" in message_facts
                            or "has_question_how_are_you" in message_facts
                            )
                        ) or (
                        time_since_last_message >= 5*60*60*1000
                        and time_since_last_message < 11*60*60*1000
                        )
                ):

                kik.send_messages([
                    TextMessage(
                        to = message.from_user,
                        chat_id = message.chat_id,
                        body = "Hi " + user["kik_firstname"] + "!\nWe were just talking about something interesting..."
                    )
                ])        

                user["repeat_question"] = True


             #######                                                               #     #                      
             #       #    #   ##   #      # #    #   ##   ##### # #    #  ####     ##    #  ####  #####  ###### 
             #       #    #  #  #  #      # #    #  #  #    #   # ##   # #    #    # #   # #    # #    # #      
             #####   #    # #    # #      # #    # #    #   #   # # #  # #         #  #  # #    # #    # #####  
             #       #    # ###### #      # #    # ######   #   # #  # # #  ###    #   # # #    # #    # #      
             #        #  #  #    # #      # #    # #    #   #   # #   ## #    #    #    ## #    # #    # #      
             #######   ##   #    # ###### #  ####  #    #   #   # #    #  ####     #     #  ####  #####  ###### 
                                                  

            print "Message: " + message.body

            answer, next_node, user = eval(user["node_current"])(sentences, user)

            print "Answer: " + " | ".join(answer)
            print "Next node: " + next_node
            user["node_previous"] = user["node_current"]
            user["node_current"]  = next_node



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
                                                                                                                       

        user["message_previous"] = message.timestamp

        print user

        user_attributes = user.keys()
        user_values = user.values()

        if (
            "unknown_user" in message_facts
            ):  
            db.execute( "INSERT INTO users (kik_id) VALUES (%s );", (message.from_user,))

        for key in user.keys():
            if user[key]:
                db.execute("UPDATE users SET " + key + " = %s WHERE kik_id = %s;", (user[key], message.from_user))

        if(
            user["node_current"]  == "dummy"
            ):
            db.execute( "DELETE FROM users WHERE kik_id = %s;", (message.from_user,))


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
