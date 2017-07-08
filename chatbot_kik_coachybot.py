from flask import Flask, request, Response

from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage

import os 

from nlp_functions import *
from ngrams import corrections
from nltk import sent_tokenize

from datetime import datetime
from pytz import timezone
from collections import defaultdict
from random import choice

import psycopg2
import urlparse

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

# ===========================================================================================

@app.route('/', methods=['POST'])
def incoming():

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

            #####################################################################
            ###     Retrieving and checking user history
            #####################################################################

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
                "message_last",
                "message_count",
                "greeting_last",
                "how_are_you_last",
                "topic_current",
                "topic_start",
                "question_open_start",
                "question_open_topic"
            ]

            db.execute("SELECT " + ', '.join(user_attributes) + " FROM users WHERE kik_id = %s;", (message.from_user,))
            user_values = db.fetchone()

            user = defaultdict(bool)

            if user_values:

                print "Found user data: " + str(user_values)
                message_facts.append("known_user") 

                user.update(dict(zip(user_attributes, user_values)))
                user["message_count"] += 1

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
                    "message_last" : message.timestamp,
                    "dialogue_start" : message.timestamp,
                    "dialogue_count" : 1
                    })

            if user["kik_timezone"]=="None":
                user["kik_timezone"] = "Europe/Berlin"


            #####################################################################
            ###     Statement normalization
            #####################################################################            

            print message.from_user + ": " + message.body

            statement = message.body
            statement = statement.lower()
            statement = expand_contractions(statement) 

            print "Step 1: " + statement 

            sentences = sent_tokenize(statement)

            answer = []
            answer_facts = []


            for (sentence,sentence_counter) in zip(sentences, range(len(sentences)+1)[1:]):

                print "Step 2." + str(sentence_counter) + ": " + sentence
                sentence = corrections(sentence)
                sentence = remove_fluff(sentence)
                print "Step 3." + str(sentence_counter) + ": " + sentence

                #sentence_tree = list(parser.raw_parse(sentence))[0][0]
                #sentence_type = str(sentence_tree.label())

                if is_greeting(sentence):
                    message_facts.append("has_greeting")  
                    
                if is_how_are_you(sentence):
                    message_facts.append("has_question_how_are_you")

            

            #     #####################################################################
            #     ###     Yes-No-Question from user
            #     #####################################################################

            #     if (
            #         "has_question_how_are_you" not in message_facts 
            #         #and sentence_type == "SQ"
            #         and False
            #         ):

            #         print "Y/N-question!"

            #         answer.append(choice([
            #             "Well... It depends, right?",
            #             "What does your heart tell you?",
            #             "It's all about definitions, right?\nCan you be more specific?"
            #         ]))   
            #         message_facts.append("has_yn_question")                        
            #         answer_facts.append("has_answer_to_yn_question")   


            #     #####################################################################
            #     ###     Open Question from user
            #     #####################################################################

            #     if (
            #         "has_question_how_are_you" not in message_facts 
            #         #and sentence_type == "SBARQ"
            #         and False
            #         ):

            #         print "Open question!"

            #         answer.append(choice([
            #             "Haha, sorry... Currently, I don't do open questions. ;)",
            #             "Enough questions for now. Let's get out and play!"
            #         ]))   
            #         message_facts.append("has_open_question")                        
            #         answer_facts.append("has_answer_to_open_question")  

            # if not answer:

            #     answer.append("Hmmm....")


###############################################################################################################################
###############################################################################################################################
###############################################################################################################################


            #####################################################################
            ###     Greeting
            #####################################################################

            time_since_last_message = message.timestamp - user["message_last"]
            
            if user["greeting_last"]:
                time_since_last_greeting = message.timestamp - user["greeting_last"]
            else:
                time_since_last_greeting = 1000*60*60*24*365

            current_time = datetime.now(tz=timezone(user["kik_timezone"])).time()
            current_hour = int(str(current_time)[:2])

            print "Current time in timezone " + user["kik_timezone"] + ": " + str(current_hour)

            if (
                time_since_last_greeting > (8*60*60*1000)
                ):
                    print "Last message was quite some time ago... Let's do some greeting!"   
                    user["greeting_last"] = message.timestamp

                    if random.choice([True,False]):
                        answer.append(choice([
                            current_greeting(current_hour) + " " +  user["kik_firstname"] + "!\nI've just been thinking of you! :)",
                            "Oh, " + current_greeting(current_hour).lower() + "!\nGood to see you again, " + user["kik_firstname"] + ". :)",
                            "Ah, " + user["kik_firstname"] + "!\nSo nice to see you again!",
                            "Hey " +  user["kik_firstname"] + "!\n" + current_greeting(current_hour) + "! :)"
                            ]))
                        answer_facts.append("has_username","has_greeting")
                    else:
                        answer.append(choice([
                            "Ah, it's you! What a pleasant surprise! :)"
                            ]))
                        answer_facts.append("has_greeting")


            elif (
                "has_greeting" in message_facts
                ):
                    print "Message contains greeting..."
                    user["greeting_last"] = message.timestamp   

                    if(
                        not user["greeting_last"]
                        or time_since_last_greeting > (3*60*60*1000)
                        ):
                        print "...and no greeting was registered recently. Going for full greeting!"   

                        if random.choice([True,False]):
                            answer.append(choice([
                                "Good " + current_daytime + " to you, " + user["kik_firstname"] + "! :)",
                                "Hey" + user["kik_firstname"] + ", good to see you! :)",
                                "Oh, hello " + user["kik_firstname"] + "! :)",
                                current_greeting(current_hour) + " " + user["kik_firstname"] + "! :)"
                            ])) 
                            answer_facts.append("has_username","has_greeting")
                        else:
                            answer.append(choice([
                                "Hey, good " + current_daytime + "! So nice to see you! :)",
                                "Oh, it's you! Hi! :)"
                            ])) 
                            answer_facts.append("has_greeting")
                    elif (
                        time_since_last_greeting <= (3*60*60*1000) 
                        and time_since_last_greeting > (5*60*1000)
                        ):
                        print "...but there was another greeting recently. Doing only a short greeting!"   

                        answer.append(choice([
                            "Hello again! :)"
                        ])) 
                        answer_facts.append("has_greeting")
                        answer_facts.append("suppress_question_how_are_you")

                    else:
                        print "...but it is a repetition. No greeting!"   


            #####################################################################
            ###     "How are you" from user
            #####################################################################

            if user["how_are_you_last"]:
                time_since_last_how_are_you = message.timestamp - user["how_are_you_last"]
            else:
                time_since_last_how_are_you = 1000*60*60*24*365

            if (
                "has_question_how_are_you" in message_facts
                ): 

                print "Contains question like 'How are you?'..."
                message_facts.append("has_question_how_are_you")  

                if(
                    not user["how_are_you_last"]
                    or time_since_last_how_are_you> (3*60*60*1000)
                    ):

                    print "...and there was no such question in the last 3 hours. Answering...!"   
                    user["how_are_you_last"] = message.timestamp
                    answer_facts.append("has_answer_how_are_you")

                    answer.append(choice([
                        "I'm doing fine, thanks! :)",
                        "I'm doing well, thank you!",
                        "Quite fine actually, thanks for asking!",
                        "Yeah, I'm pretty good."
                        ]))    

                if(
                    time_since_last_how_are_you <= (3*60*60*1000)
                    and time_since_last_how_are_you > (5*60*1000)
                    ):

                    print "...but there was such a question in the last 3 hours. Giving a brief answer..."   
                    user["how_are_you_last"] = message.timestamp
                    answer_facts.append("has_answer_how_are_you")
                    answer_facts.append("suppress_question_how_are_you")

                    answer.append(choice([
                        "Yup, still doing fine."
                        ]))   

                else:
                    
                    print "...but it is a repetition. No answer!"  
                    answer_facts.append("has_answer_how_are_you")  
                    answer_facts.append("suppress_question_how_are_you")
      

            #####################################################################
            ###     "How are you" to user
            #####################################################################

            if (
                ("has_question_how_are_you" in message_facts
                    or "has_greeting" in answer_facts
                    )
                and "suppress_question_how_are_you" not in answer_facts
                ): 

                print "It's a good time to aks the user how he is doing."
                answer_facts.append("has_question_how_are_you")   
                user.update({
                    "question_open_topic" : "how_are_you",
                    "question_open_start" : message.timestamp
                    }) 

                if (
                    "has_username" in answer_facts
                    or random.choice([True,False])
                    ):
                    answer.append(choice([
                        "How is you " + current_daytime(current_hour) + "?",
                        "How was you " + previous_daytime(current_hour) + "?",
                        "How are you today?",
                        "What's on your mind?"
                    ])) 
                else:
                    answer.append(choice([
                        "How are you today, " + user["kik_username"] + "?",
                    ])) 
                    answer_facts.append("has_username")


            #####################################################################
            ###     Sending the message
            #####################################################################

            for key in user.keys():
                print("{:12}: {}".format(key,str(user[key])))
            print "Message: " + ", ".join(message_facts)
            print "Answer: " + ", ".join(answer_facts)
            print " | ".join(answer)

            kik.send_messages([
                TextMessage(
                    to = message.from_user,
                    chat_id = message.chat_id,
                    body = line
                ) for line in answer
            ])                 


        #####################################################################
        ###     Updating database
        #####################################################################

        user["message_last"] = message.timestamp

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


    #####################################################################
    ###     Finishing activity on database and app
    #####################################################################

    conn.commit()
    db.close()
    conn.close()

    return Response(status=200)

# ===========================================================================================

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    print('Starting the app...') 
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
