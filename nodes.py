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
                "How are you today, " + user["kik_firstname"] + "?"
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

    for sentence in sentences:

        if has_question_why(sentence):
            message_facts.append("has_question_why")  
        if has_protest_to_question(sentence):
            message_facts.append("has_protest_to_question")
        if is_greeting(sentence):
            message_facts.append("has_greeting")
        if is_how_are_you(sentence):
            message_facts.append("has_question_how_are_you")
        if is_good(sentence):
            message_facts.append("is_good")
        if is_bad(sentence):
            message_facts.append("is_bad")            
        
	if has_elaboration(sentences):
		message_facts.append("has_elaboration")


	time_since_last_message = message.timestamp - user["message_last"]

	if(			# Interruption
		time_since_last_message >= 3*60*60*1000
		):

		print "There was an interruption in the conversation. Return to full greeting..."

		answer, next_node, user = greeting(message, user)
		return answer, next_node, user

	elif(		# Why-Question
		"has_question_why" in answer_facts
		):

		print "User wants to know the reason for this question..."

		answer.append(random.choice([
			"Oh, that's a nice way to start a conversation. You should gibe it a try sometimes! ;)"
			"\nBut really, how are you today?"
			]))

		next_node = "how_are_you"

	elif(		# Protest to question
		"has_protest_to_question" in message_facts
		):

		print "User does not want to answer the question..."

		answer.append(random.choice([
			"Come on, I just wanted to get the conversation started."
			"\nThere is something annoying you, right?"
			]))

		next_node = "dummy" # "aggression"

	elif(		# Positive answer, but no further elaboration
		"is_good" in message_facts
		and "has_elaboration" not in message_facts
		):

		answer.append(random.choice([
			"That's good to hear. So... Was there any particular highlight?",
			"Great! What was today's highlight?"
			]))

		next_node = "dummy" # highlight

	elif(		# Negative answer with no further elaboration
		"is_bad" in message_facts
		and "has_elaboration" not in message_facts
		):

		answer.append(random.choice([
			"Okay... Do you want to talk about it?",
			"What happened?",
			"Can you tell me some more?",
			"Really???"
			]))

		next_node = "dummy" # how_are_you_bad

	else:		# Backup plan, if no pattern matches

		answer.append(random.choice([
			"OK..."
			]))

		next_node = "dummy"

    return answer, next_node, user



 ######                             
 #     # #    # #    # #    # #   # 
 #     # #    # ##  ## ##  ##  # #  
 #     # #    # # ## # # ## #   #   
 #     # #    # #    # #    #   #   
 #     # #    # #    # #    #   #   
 ######   ####  #    # #    #   #   
   

def dummy(message, user):
    "Dummy node, to test node transition."

    print "Evaluating node 'dummy'"

    answer = ["It was nice talking to you! :)"]

    next_node = "greeting"

    return answer, next_node, user



 #######                                                 
    #    ###### #    # #####  #        ##   ##### ###### 
    #    #      ##  ## #    # #       #  #    #   #      
    #    #####  # ## # #    # #      #    #   #   #####  
    #    #      #    # #####  #      ######   #   #      
    #    #      #    # #      #      #    #   #   #      
    #    ###### #    # #      ###### #    #   #   ###### 
                                                         

def template(message, user):
    "Node template"

    print "Evaluating node 'Template'"

    message_facts = []
    answer_facts = []
    answer = []

    sentences = preprocess_message(message.body)

    for sentence in sentences:

        if has_question_why(sentence):
            message_facts.append("has_question_why")  
        if has_protest_to_question(sentence):
            message_facts.append("has_protest_to_question")
        if is_greeting(sentence):
            message_facts.append("has_greeting")
        if is_how_are_you(sentence):
            message_facts.append("has_question_how_are_you")

	time_since_last_message = message.timestamp - user["message_last"]

	if(			# Medium interruption
		(
			time_since_last_message >= 2*60*60*1000
			and time_since_last_message < 5*60*60*1000
			and (
				"has_greeting" in answer_facts
				or "has_question_how_are_you" in answer_facts
				)
			) or (
			time_since_last_message >= 5*60*60*1000
			and time_since_last_message < 11*60*60*1000
			)
		):

		print "There was a medium interruption in the conversation. Resuming..."

		answer.append(random.choice([
			"Hi " + user["kik_firstname"] + "!\nWe were just talking about something interesting..."
			]))

		next_node = "dummy"

	elif(		# Major interruption
		time_since_last_message >= 11*60*60*1000
		):

		print "There was a major interruption in the conversation. Return to full greeting..."

		answer = ["Hello again!"]
		next_node = "dummy"

		#answer, next_node, user = greeting(message, user)
		#return answer, next_node, user

	elif(		# Why-Question
		"has_question_why" in answer_facts
		):

		print "User wants to know the reason for this question..."

		answer.append(random.choice([
			"Well... It's just an intersting topic, right?"
			]))

		next_node = "dummy"

	elif(		# Protest to question
		"has_protest_to_question" in answer_facts
		):

		print "User does not want to answer the question..."

		answer.append(random.choice([
			"Oh, sorry! So this is a touchy subject for you, right?"
			]))

		next_node = "dummy"

	elif(		# Actual relevant decision
		True
		):

		answer.append(random.choice([
			"OK..."
			]))

		next_node = "dummy"

	else:		# Backup plan, if no pattern matches

		answer.append(random.choice([
			"OK..."
			]))

		next_node = "dummy"

    return answer, next_node, user

























