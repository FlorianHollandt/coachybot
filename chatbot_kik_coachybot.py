from flask import Flask, request, Response

from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage

import os 

from nlp_functions import *
from ngrams import corrections
from nltk import sent_tokenize

from datetime import datetime
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

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

# ===========================================================================================

global history
history = dict()

# ===========================================================================================

@app.route('/', methods=['POST'])
def incoming():

    if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):

        return Response(status=403)

    db = conn.cursor()   

    messages = messages_from_json(request.json['messages'])

    for message in messages:
        if isinstance(message, TextMessage):

            #####################################################################
            ###     Retrieving and checking user history
            #####################################################################

            print "Looking up Kik user '" + message.from_user + "' in database..."

            user_attributes = [
                "kik_id" ,
                "kik_name", 
                "name", 
                "gender", 
                "dialogue_count", 
                "dialogue_start", 
                "message_last"
            ]

            #db.execute("SELECT %s FROM users WHERE kik_id = %s;", (",".join(user_attributes), message.from_user))
            db.execute("SELECT " + ','.join(user_attributes) + " FROM users WHERE kik_id = %s;", (message.from_user,))
            user_values = db.fetchone()

            print "Found user data: " + str(user_values)


            # Check if there is a history entry for user -> Create if not

            if message.from_user not in history.keys():
                history[message.from_user] = defaultdict(bool)
                history[message.from_user].update({"dialogue_count" : 1,
                                      "dialogue_start" : message.timestamp,
                                      "message_last" : message.timestamp
                                      })
            else:
                history[message.from_user]["dialogue_count"] += 1


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
            message_facts = []
            answer_facts = []

            for (sentence,sentence_counter) in zip(sentences, range(len(sentences)+1)[1:]):

                print "Step 2." + str(sentence_counter) + ": " + sentence
                sentence = corrections(sentence)
                sentence = remove_fluff(sentence)
                print "Step 3." + str(sentence_counter) + ": " + sentence

                #sentence_tree = list(parser.raw_parse(sentence))[0][0]
                #sentence_type = str(sentence_tree.label())


                #####################################################################
                ###     Greeting
                #####################################################################

                if (
                    is_greeting(sentence) 
                    and "has_greeting" not in answer_facts
                    ):    

                    print "Has greeting, and answer does not include other greeting yet."

                    message_facts.append("has_greeting")   

                    if(
                        not history[message.from_user]["greeting_last"]
                        or message.timestamp - history[message.from_user]["greeting_last"] > (3*60*60*1000)
                        ):


                        current_time = int(str(datetime.now().time())[:2])

                        print "Current time for greeting: " + str(current_time)

                        if current_time >= 22 or current_time < 9:
                            greeting = "Good morning"
                        elif current_time >= 16 and current_time < 22:   
                            greeting = "Good evening"
                        elif current_time >= 12 and current_time < 16:   
                            greeting = "Good afternoon"
                        else:
                            greeting = "Hello"  

                        answer.append(choice([
                            greeting + " " + message.from_user + "!",
                            greeting + "!\nGood to see you, " + message.from_user + ". :)" 
                            ]))
                        answer_facts.append("has_greeting")  
                        history[message.from_user]["greeting_last"] = message.timestamp

                    elif (
                        message.timestamp - history[message.from_user]["greeting_last"] < (10*60*1000)
                        and message.timestamp - history[message.from_user]["greeting_last"] >= (2*60*1000)
                        ):
                        answer.append(choice([
                            "Hello again... We've done this recently.",
                            "This is getting ridiculous. Are you obsessed with greetings? :D",
                            "Is this some kind of 'Hello' game that you want to play? ;)"
                            ]))                        
                        answer_facts.append("has_greeting")  
                        history[message.from_user]["greeting_last"] = message.timestamp                       

                    elif message.timestamp - history[message.from_user]["greeting_last"] < (2*60*1000):
                        history[message.from_user]["greeting_last"] = message.timestamp     

                    else:
                        answer.append(choice([
                            "Hello again, " + message.from_user + "!",
                            "Well... Hello again! :D"
                            ]))
                        answer_facts.append("has_greeting")  
                        history[message.from_user]["greeting_last"] = message.timestamp

                #--------------------------------------------------------------------
                #--   Greet again after long inactivity
                #-------------------------------------------------------------------

                if(
                    message.timestamp - history[message.from_user]["message_last"] > (8*60*60*1000)
                    ):


                    current_time = int(str(datetime.now().time())[:2])

                    print "Current time for greeting: " + str(current_time)

                    if current_time >= 22 or current_time < 9:
                        greeting = "Good morning"
                    elif current_time >= 16 and current_time < 22:   
                        greeting = "Good evening"
                    elif current_time >= 12 and current_time < 16:   
                        greeting = "Good afternoon"
                    else:
                        greeting = "Hello"  

                    answer.append(choice([
                        greeting + " " + message.from_user + "!\nI've just been thinking of you! :)",
                        greeting + "!\nGood to see you again, " + message.from_user + ". :)",
                        "Ah, " + message.from_user + "!\nSo nice to see you again!",
                        "Hey " + message.from_user + "!\n" + greeting,
                        ]))
                    answer_facts.append("has_greeting")  
                    history[message.from_user]["greeting_last"] = message.timestamp


                #####################################################################
                ###     "How are you" from user
                #####################################################################

                if (
                    is_how_are_you(sentence)
                    ): 

                    print "Contains question like 'How are you?'."

                    if(
                        not history[message.from_user]["how_are_you_last"]
                        or message.timestamp - history[message.from_user]["how_are_you_last"] > (3*60*60*1000)
                        ):

                        answer.append(choice([
                            "I'm doing fine, thanks! :)",
                            "I'm doing well, thank you!",
                            "Quite fine actually, thanks for asking!",
                            "Yeah, I'm pretty good."
                            ]))    

                        message_facts.append("has_question_how_are_you")       
                        answer_facts.append("has_answer_how_are_you")  
                        history[message.from_user]["how_are_you_last"] = message.timestamp

                    elif message.timestamp - history[message.from_user]["how_are_you_last"] < (5*60*1000):
                        message_facts.append("has_question_how_are_you")       
                        answer_facts.append("suppress_answer_how_are_you")     # To prevent repetition
                        answer_facts.append("suppress_question_how_are_you")     # To prevent repetition
                        history[message.from_user]["how_are_you_last"] = message.timestamp   
                        continue  

                    else:
                        answer.append(choice([
                            "Jup... Still doing fine.",
                            "Pretty much the same as some minutes ago. :D"
                            ]))
                        message_facts.append("has_question_how_are_you")       
                        answer_facts.append("has_answer_how_are_you")  
                        answer_facts.append("suppress_question_how_are_you")     # To prevent repetition
                        history[message.from_user]["how_are_you_last"] = message.timestamp   
                        continue                     


                #####################################################################
                ###     "How are you" to user
                #####################################################################

                if (
                    "has_question_how_are_you" in message_facts 
                    and "has_question_how_are_you" not in answer_facts
                    and "suppress_question_how_are_you" not in answer_facts
                    ): 

                    print "Contains question like 'How are you?', and no such question in return yet."

                    answer.append(choice([
                        "How has your day been so far?",
                        "How are you today?",
                        "What's on your mind?"
                    ])) 
                    answer_facts.append("has_question_how_are_you")   
                    history[message.from_user].update({
                        "question_open_topic" : "how_are_you",
                        "question_open_start" : message.timestamp
                        })      
                    continue            


                #####################################################################
                ###     Yes-No-Question from user
                #####################################################################

                if (
                    "has_question_how_are_you" not in message_facts 
                    #and sentence_type == "SQ"
                    and False
                    ):

                    print "Y/N-question!"

                    answer.append(choice([
                        "Well... It depends, right?",
                        "What does your heart tell you?",
                        "It's all about definitions, right?\nCan you be more specific?"
                    ]))   
                    message_facts.append("has_yn_question")                        
                    answer_facts.append("has_answer_to_yn_question")   


                #####################################################################
                ###     Open Question from user
                #####################################################################

                if (
                    "has_question_how_are_you" not in message_facts 
                    #and sentence_type == "SBARQ"
                    and False
                    ):

                    print "Open question!"

                    answer.append(choice([
                        "Haha, sorry... Currently, I don't do open questions. ;)",
                        "Enough questions for now. Let's get out and play!"
                    ]))   
                    message_facts.append("has_open_question")                        
                    answer_facts.append("has_answer_to_open_question")  

            if not answer:

                answer.append("Hmmm....")


            #####################################################################
            ###     Sending the message and updating database
            #####################################################################

            print history[message.from_user]
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

        history[message.from_user]["message_last"] = message.timestamp

        db.execute("UPDATE users SET message_last = %s WHERE kik_id = %s;", (message.timestamp, message.from_user))


    #####################################################################
    ###     Finishing activity on database and app
    #####################################################################

    conn.commit()
    db.close()
    #conn.close()

    return Response(status=200)

# ===========================================================================================

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    print('Starting the app...') 
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
