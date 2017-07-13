import random

from datetime import datetime
from pytz import timezone

from nlp_functions import *

import nltk

sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')


# ===========================================================================================

 #     #                                           
 #  #  # ###### #       ####   ####  #    # ###### 
 #  #  # #      #      #    # #    # ##  ## #      
 #  #  # #####  #      #      #    # # ## # #####  
 #  #  # #      #      #      #    # #    # #      
 #  #  # #      #      #    # #    # #    # #      
  ## ##  ###### ######  ####   ####  #    # ###### 
                                                   

#def welcome(user,statement):
#    "Welcome message to first time users"

  #####                                             
 #     # #####  ###### ###### ##### # #    #  ####  
 #       #    # #      #        #   # ##   # #    # 
 #  #### #    # #####  #####    #   # # #  # #      
 #     # #####  #      #        #   # #  # # #  ### 
 #     # #   #  #      #        #   # #   ## #    # 
  #####  #    # ###### ######   #   # #    #  ####  
                                                    

def greeting(message, user):
    "Regular greeting or first message after some time"

    print "Evaluating node 'greeting'"

    message_facts = []
    answer_facts = []
    answer = []

    sentences = preprocess_message(message.body)

    for sentence in sentences:

        if is_greeting(sentence):
            message_facts.append("has_greeting")  
        if is_how_are_you(sentence):
            message_facts.append("has_question_how_are_you")

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
                answer.append(random.choice([
                    current_greeting(current_hour) + " " +  user["kik_firstname"] + "!\nI've just been thinking of you! :)",
                    "Oh, " + current_greeting(current_hour).lower() + "!\nGood to see you again, " + user["kik_firstname"] + ". :)",
                    "Ah, " + user["kik_firstname"] + "!\nSo nice to see you again!",
                    "Hey " +  user["kik_firstname"] + "!\n" + current_greeting(current_hour) + "! :)"
                    ]))
                answer_facts.append("has_username")
                answer_facts.append("has_greeting")
            else:
                answer.append(random.choice([
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
                    answer.append(random.choice([
                        "Good " + current_daytime + " to you, " + user["kik_firstname"] + "! :)",
                        "Hey" + user["kik_firstname"] + ", good to see you! :)",
                        "Oh, hello " + user["kik_firstname"] + "! :)",
                        current_greeting(current_hour) + " " + user["kik_firstname"] + "! :)"
                    ])) 
                    answer_facts.append("has_username","has_greeting")
                else:
                    answer.append(random.choice([
                        "Hey, good " + current_daytime + "! So nice to see you! :)",
                        "Oh, it's you! Hi! :)"
                    ])) 
                    answer_facts.append("has_greeting")
            elif (
                time_since_last_greeting <= (3*60*60*1000) 
                and time_since_last_greeting > (5*60*1000)
                ):
                print "...but there was another greeting recently. Doing only a short greeting!"   

                answer.append(random.choice([
                    "Hello again! :)"
                ])) 
                answer_facts.append("has_greeting")
                answer_facts.append("suppress_question_how_are_you")

                next_node = "dummy"

            else:
                print "...but it is a repetition. No greeting!"   
                answer.append(random.choice([
                    "Hey! :)\nLet's talk about something interesting!"
                ])) 

                next_node = "dummy"

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

            answer.append(random.choice([
                "I'm doing fine, thanks! :)",
                "I'm doing well, thank you!",
                "Quite fine actually, thanks for asking!",
                "Yeah, I'm pretty good."
                ]))    

            next_node = "how_are_you"

        elif(
            time_since_last_how_are_you <= (3*60*60*1000)
            and time_since_last_how_are_you > (5*60*1000)
            ):

            print "...but there was such a question in the last 3 hours. Giving a brief answer..."   
            user["how_are_you_last"] = message.timestamp
            answer_facts.append("has_answer_how_are_you")
            answer_facts.append("suppress_question_how_are_you")

            answer.append(random.choice([
                "Yup, still doing fine."
                ]))   

            next_node = "dummy"

        else:
            
            print "...but it is a repetition. No answer!"  
            answer_facts.append("has_answer_how_are_you")  
            answer_facts.append("suppress_question_how_are_you")

            answer.append(random.choice([
                "You obviously like greetings, right? ;)."
                ]))   

            next_node = "dummy"


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
            "question_open_start" : message.timestamp,
            "topic_current" : "how_are_you",
            "topic_start" : message.timestamp
            }) 

        if (
            "has_username" in answer_facts
            or random.choice([True,False])
            ):
            answer.append(random.choice([
                "How is your " + current_daytime(current_hour) + "?",
                "How was your " + previous_daytime(current_hour) + "?",
                "How are you today?"
                #"What's on your mind?"
            ])) 
        else:
            answer.append(random.choice([
                "How are you today, " + user["kik_username"] + "?",
            ])) 
            answer_facts.append("has_username")    

    	next_node = "how_are_you"  

    else:

    	next_node = "dummy"   

    return answer, next_node, user        


 #     #                     #                     #     #               
 #     #  ####  #    #      # #   #####  ######     #   #   ####  #    # 
 #     # #    # #    #     #   #  #    # #           # #   #    # #    # 
 ####### #    # #    #    #     # #    # #####        #    #    # #    # 
 #     # #    # # ## #    ####### #####  #            #    #    # #    # 
 #     # #    # ##  ##    #     # #   #  #            #    #    # #    # 
 #     #  ####  #    #    #     # #    # ######       #     ####   ####  
          

def how_are_you(message, user):
    "Response to question like 'How are you?' in greeting."

    print "Evaluating node 'how_are_you'"

    message_facts = []
    answer_facts = []
    answer = []

    sentences = preprocess_message(message.body)

    #for sentence in sentences:	



 ######                             
 #     # #    # #    # #    # #   # 
 #     # #    # ##  ## ##  ##  # #  
 #     # #    # # ## # # ## #   #   
 #     # #    # #    # #    #   #   
 #     # #    # #    # #    #   #   
 ######   ####  #    # #    #   #   
   

def dummy(message, user):
    "Dummy node, to test node transition."

    print "Evaluating node 'how_are_you'"

    answer = ["Hmmm... Tell me more!"]

    next_node = "greeting"

    return answer, next_node, user



























