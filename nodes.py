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
                                                    

def greeting(sentences, user):
    "Regular greeting or first message after some time"

    print "Evaluating node 'greeting'"

    message_facts = []
    answer_facts = []
    answer = []

    for sentence in sentences:
        if is_greeting(sentence):
            message_facts.append("has_greeting")  
        if is_how_are_you(sentence):
            message_facts.append("has_question_how_are_you")

    time_since_last_message = user["message_current"] - user["message_previous"]
    
    if user["greeting_last"]:
        time_since_last_greeting = user["message_current"]- user["greeting_last"]
    else:
        time_since_last_greeting = 1000*60*60*24*365

    current_time = datetime.now(tz=timezone(user["kik_timezone"])).time()
    current_hour = int(str(current_time)[:2])

    print "Current time in timezone " + user["kik_timezone"] + ": " + str(current_hour)

    if (
        time_since_last_greeting > (8*60*60*1000)
        ):
            print "Last message was quite some time ago... Let's do some greeting!"   
            user["greeting_last"] = user["message_current"]

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
            user["greeting_last"] = user["message_current"]  

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
        time_since_last_how_are_you = user["message_current"]- user["how_are_you_last"]
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
            user["how_are_you_last"] = user["message_current"]
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
            user["how_are_you_last"] = user["message_current"]
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
            "question_open_start" : user["message_current"],
            "topic_current" : "how_are_you",
            "topic_start" : user["message_current"]
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
          

def how_are_you(sentences, user):
    "Response to question like 'How are you?' in greeting."

    print "Evaluating node 'how_are_you'"

    message_facts = []
    answer_facts = []
    answer = []
    reflections_open = []
    reflections_closed = []
    rationale = []

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
        if is_statement_about_self(sentence):
            message_facts.append("has_statement_about_self")
            reflections_closed.append(capitalize_fragment(perform_closed_reflection(sentence)))
            #print reflections_closed
            reflections_open.append(capitalize_fragment(perform_open_reflection(sentence)))
            #print reflections_open
        if has_rationale(sentence):
            rationale.append(capitalize_fragment(reflect_rationale(sentence)))

        
    if has_elaboration(sentences):
        message_facts.append("has_elaboration")

    time_since_last_message = user["message_current"]- user["message_previous"]

    if(            # Medium interruption
        user["repeat_question"]
        ):

        print "Re-formulate the node's question, because of an interruption"

        answer.append(random.choice([
            "So... How are you, acutally?"
            ]))
        
        user["repeat_question"] = False

        next_node = "how_are_you" # The same node again...

    elif(        # Why-Question
        "has_question_why" in message_facts
        ):

        print "User wants to know the reason for this question..."

        answer.append(random.choice([
            "Oh, that's a nice way to start a conversation, right?"
            "\nBut really, how are you today?"
            ]))

        next_node = "how_are_you"

    elif(        # Protest to question
        "has_protest_to_question" in message_facts
        ):

        print "User does not want to answer the question..."

        answer.append(random.choice([
            "Come on, I just wanted to get the conversation started."
            "\nThere is something annoying you, right?"
            ]))

        next_node = "dummy" # "aggression"

    elif(        # Positive answer with rationale
        "is_good" in message_facts
        and rationale
        ):

        answer.append(random.choice([
            rationale[-1] + "? Sounds good... Can you tell me more about it?",
            ]))

        next_node = "dummy" # how_are_you_reason   

    elif(        # Positive answer with statement about self
        "is_good" in message_facts
        and reflections_open
        ):

        answer.append(random.choice([
            "Wow, " + reflections_closed[-1] + "? That's great!",
            "Really  -  " + reflections_closed[-1] + "? That's amazing!",
            "Oh, nice! Can you tell me some more about how and why " + reflections_closed[-1] + "?"
            ]))

        next_node = "dummy" # reflection_positive    


    elif(        # Positive answer, but no further elaboration
        "is_good" in message_facts
        and "has_elaboration" not in message_facts
        ):

        answer.append(random.choice([
            "That's good to hear. So... Was there any particular highlight?",
            "Great! What was today's highlight?"
            ]))

        next_node = "dummy" # highlight

    elif(        # Negative or neutral answer with rationale
        rationale
        ):

        answer.append(random.choice([
            rationale[-1] + "? Okay... Can you tell me some more about it?",
            ]))

        next_node = "dummy" # how_are_you_reason   

    elif(        # Negative answer with statement about self
        "is_bad" in message_facts
        and reflections_open
        ):

        answer.append(random.choice([
            "Oh no! But why " + reflections_open[-1] + "?",
            "Hmm... So " + reflections_closed[-1] + "?"
            ]))

        next_node = "dummy" # reflection_negative        

    elif(        # Negative answer with no further elaboration
        "is_bad" in message_facts
        and "has_elaboration" not in message_facts
        ):

        answer.append(random.choice([
            "Okay... Do you want to talk about it?",
            "What happened?",
            "Can you tell me some more?",
            "Really???"
            ]))

        next_node = "how_are_you_bad" # how_are_you_bad

    elif(        # Neutral answer with statement about self
        reflections_open
        ):

        answer.append(random.choice([
            "Hmm... So " + reflections_closed[-1] + "?"
            ]))

        next_node = "dummy" # reflection_negative 

    else:        # Backup plan, if no pattern matches

        answer.append(random.choice([
            "Hm, I see...",
            "Okay...",            
            "Really?",            
            "Can you elaborate on that?"           
            ]))

        next_node = "how_are_you"

    return answer, next_node, user



 #     #                                                                          ######                
 #     #  ####  #    #      ##   #####  ######    #   #  ####  #    #             #     #   ##   #####  
 #     # #    # #    #     #  #  #    # #          # #  #    # #    #             #     #  #  #  #    # 
 ####### #    # #    #    #    # #    # #####       #   #    # #    #    #####    ######  #    # #    # 
 #     # #    # # ## #    ###### #####  #           #   #    # #    #             #     # ###### #    # 
 #     # #    # ##  ##    #    # #   #  #           #   #    # #    #             #     # #    # #    # 
 #     #  ####  #    #    #    # #    # ######      #    ####   ####              ######  #    # #####  
                                                                                                        

def how_are_you_bad(sentences, user):
    "Can you tell me more about that negative experience that you mentioned?"

    print "Evaluating node 'how_are_you_bad'"

    message_facts = []
    answer_facts = []
    answer = []
    rationale = []

    for sentence in sentences:
        if has_question_why(sentence):
            message_facts.append("has_question_why")  
        if has_protest_to_question(sentence):
            message_facts.append("has_protest_to_question")
        if has_negation(sentence):
            message_facts.append("has_negation")
        if has_affirmation(sentence):
            message_facts.append("has_affirmation")
        if has_rationale(sentence):
            rationale.append(capitalize_fragment(reflect_rationale(sentence)))

    if has_elaboration(sentences):
        message_facts.append("has_elaboration")


    if(            # Medium interruption
        user["repeat_question"]
        ):

        print "Re-formulate the node's question, because of an interruption"

        answer.append(random.choice([
            "So... You mentioned that something is bothering you, right?\n"
            "Can you tell me something about it?"
            ]))
        
        next_node = "how_are_you_bad" # The same node again...

    elif(        # Why-Question
        "has_question_why" in message_facts
        ):

        print "User wants to know the reason for this question..."

        answer.append(random.choice([
            "Something is toubling you, right? Maybe I can help you finding a solution."
            ]))

        next_node = "how_are_you_bad" # The same node again...

    elif(        # User does not want to talk about it
        "has_protest_to_question" in message_facts
        or (
            "has_negation" in message_facts
            #and "has_elaboration"
            )
        ):

        print "User does not want to answer the question..."

        answer.append(random.choice([
            "Oh, sorry! So this is a touchy subject for you, right?",
            "I totally respect that. Let's talk about somethin else instead..."
            ]))

        next_node = "dummy" # Some appropriate node

    elif(        # User responds positively, but does not talk
        "has_affirmation" in message_facts
        and "has_elaboration" not in message_facts
        ):

        answer.append(random.choice([
            "OK, so... What is bothering you?"
            ]))

        next_node = "dummy" #how_are_you_reason

    elif(        # User offers the reason for his negative experience 
        rationale
        ):

        # Dummy answer, actually the node "how_are_you_reason" needs to be evaluated directly
        answer.append(random.choice([
            "OK, so... " + rationale[-1] + "?"
            ]))

        # answer, next_node, user = how_are_you_reason(sentences,user)

        next_node = "dummy" #how_are_you_reason

    elif(        # User dumps some text...
        "has_elaboration" in message_facts
        ):

        answer.append(random.choice([
            "Interesting! Can you tell me some more about it?",
            "Hm... Tell me a bit more about it.",
            "OK, I see... What else?"
            ]))

        next_node = "dummy" #how_are_you_reason

    else:        # Backup plan, if no pattern matches

        answer.append(random.choice([
            "Alright, that's enough. It was nice talking to you, " + user["kik_firstname"]
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
   

def dummy(sentences, user):
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
                                                         

def template(sentences, user):
    "Node template"

    print "Evaluating node 'how_are_you_bad'"

    message_facts = []
    answer_facts = []
    answer = []

    for sentence in sentences:
        if has_question_why(sentence):
            message_facts.append("has_question_why")  
        if has_protest_to_question(sentence):
            message_facts.append("has_protest_to_question")
        if is_how_are_you(sentence):
            message_facts.append("has_question_how_are_you")

    time_since_last_message = user["message_current"] - user["message_previous"]

    if(            # Medium interruption
        user["repeat_question"]
        ):

        print "Re-formulate the node's question, because of an interruption"

        answer.append(random.choice([
            "So... What do you feel about X?"
            ]))
        
        next_node = "dummy" # The same node again...

    elif(        # Why-Question
        "has_question_why" in message_facts
        ):

        print "User wants to know the reason for this question..."

        answer.append(random.choice([
            "Well... It's just an intersting topic, right?"
            ]))

        next_node = "dummy" # The same node again...

    elif(        # Protest to question
        "has_protest_to_question" in message_facts
        ):

        print "User does not want to answer the question..."

        answer.append(random.choice([
            "Oh, sorry! So this is a touchy subject for you, right?"
            ]))

        next_node = "dummy" # Some appropriate node

    elif(        # Actual relevant decision
        True
        ):

        answer.append(random.choice([
            "OK..."
            ]))

        next_node = "dummy"

    else:        # Backup plan, if no pattern matches

        answer.append(random.choice([
            "OK..."
            ]))

        next_node = "dummy"

    return answer, next_node, user

























