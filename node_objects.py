import random
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from pytz import timezone


from skills import *


 #######                                                 
    #    ###### #    # #####  #        ##   ##### ###### 
    #    #      ##  ## #    # #       #  #    #   #      
    #    #####  # ## # #    # #      #    #   #   #####  
    #    #      #    # #####  #      ######   #   #      
    #    #      #    # #      #      #    #   #   #      
    #    ###### #    # #      ###### #    #   #   ###### 


class Template(object):
    """
    Template node
    """

    def __init__(self, text, user=defaultdict(bool), verbose=True):
        """
        Evaluates user input under consideration of the user history.

        Arguments:
            - text            Mandatory                    A string, can contain several sentences
            - user            Optional (empty dict)        A dictionary of facts about the user and their history
            - verbose         Optional (True)              A flag to hide or display state information
        """

        if verbose: print "Evaluating node '" + type(self).__name__ + "'"    

        # Making sure that 'sentences' is a list of strings

        if not(
            isinstance( text, str)
            or isinstance( text, unicode)
            ):
            if verbose: print "Argument 'text' must be a (unicode) string."
            if verbose: print "Instead, text argument of type '" + type(text).__name__ + "' was given."
            raise TypeError

        # Standard user for development and debugging     
        # 
        # Unit tests pass also with default "dict()" user argument, but
        #  get inerpreted as new user and receive full greeting        

        if isinstance(user, str):
            if user == "dev_standard_user":
                user = {
                    "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
                    "message_current"  : 1501225200  # Friday, July 28, 2017 7:00:00 AM          
                }  

        # Making sure that 'user' is a dictionary

        if not (isinstance( user, dict) or isinstance( user, defaultdict)):
            if verbose: print "Argument 'user' must be a dictionary."
            if verbose: print "Instead, user argument of type '" + type(user).__name__ + "' was given."
            raise TypeError
        user_backup = deepcopy(user)            
        if isinstance( user, dict) and  not isinstance( user, defaultdict):
            if verbose: print "Converting 'user' from dict to defaultdict."
            user = defaultdict(bool)
            user.update(user_backup)

        # Making sure that timestamp is numeric

        if (
            "timestamp" in user.keys()
            and not isinstance( user["timestamp"], int)
            ):
            if verbose: print "Timestamp value must be an integer (offset from UTC)."
            if verbose: print "Instead, timestamp of type '" + type(user["timestamp"]).__name__ + "' was given."
            raise TypeError

        # Instance attributes

        self.message       = text
        self.message_facts = []
        self.answer        = []
        self.answer_facts  = []
        self.current_hour  = None
        self.node_next     = "Terminator"
        self.user          = user
        self.user_backup   = user_backup
        self.verbose       = verbose
     

        # Recognizing disruptions

        if all(key in user.keys() for key in ("message_current", "message_previous")):
            time_since_last_message = user["message_current"] - user["message_previous"]
            if(
                time_since_last_message >= 11*60*60
                ):
                self.message_facts.append("has_interruption_long")
                if verbose: print "Long interruption of more than 11 hours..."
            elif(
                time_since_last_message < 11*60*60
                and time_since_last_message >= 5*60*60
                ):
                self.message_facts.append("has_interruption_medium")
                if verbose: print "Medium interruption of more than 5 hours..."
            elif(
                time_since_last_message < 5*60*60
                and time_since_last_message >= 2*60*60
                ):
                self.message_facts.append("has_interruption_short")      
                if verbose: print "Short interruption of more than 2 hours..."


        # Recognizing time of day

        if(
            "timezone" in user.keys()
            and "message_current" in user.keys()
            ):
            #current_time = datetime.fromtimestamp(user["message_current"],tz=timezone(user["timezone"])).time()
            #self.current_hour = int(str(current_time)[:2])
            utc_hour = datetime.utcfromtimestamp( user["message_current"]).hour
            self.current_hour = utc_hour + user["timezone"]
            if verbose: print "Current time in timezone UTC+" + str(user["timezone"]) + ": " + str(self.current_hour)
        else:
            if verbose: print "No known time zone for user, using generic time references."


        # Text preprocessing

        self.sentences = preprocess_message(text)


        # Checking for generic statements / intentions

        if verbose:("{:30}:".format("Preprocessed sentences"))
        if verbose: sentence_counter = 1

        for sentence in self.sentences:
            if verbose: print str(sentence_counter) + ".: " + sentence
            if verbose: sentence_counter += 1
            if has_request_to_explain(sentence):
                self.message_facts.append("has_request_to_explain")  
            if has_protest_to_question(sentence):
                self.message_facts.append("has_protest_to_question")
            if is_question_how_are_you(sentence):
                self.message_facts.append("has_question_how_are_you")        
            if is_question_how_was_your_time(sentence):
                self.message_facts.append("has_question_how_was_your_time")       
            if is_question_you_had_good_time(sentence):
                self.message_facts.append("has_question_you_had_good_time")                       
            if is_greeting(sentence):
                self.message_facts.append("has_greeting")   
            if has_danger_to_self(sentence):
                self.message_facts.append("has_danger_to_self") 
        if has_hesitation( text.lower()):
            self.message_facts.append("has_hesitation")   


        # Greeting logic (without "How are you?")

        if (
            "has_interruption_long" in self.message_facts
            or not self.user["message_previous"]
            ):

            if user["firstname"]:
                
                self.answer.append(random.choice([
                    current_greeting(self.current_hour) + " " +  self.user["firstname"] + "!\nI've just been thinking of you! :)",
                    "Oh, " + current_greeting(self.current_hour).lower() + "! "
                    "Good to see you again, " + user["firstname"] + ". :)",
                    "Ah, " + self.user["firstname"] + "!\nSo nice to see you again!",
                    current_greeting(self.current_hour)  + " " +  self.user["firstname"] + "! :)"
                    ]))
                self.answer_facts.append("use_user_firstname")

            else:

                self.answer.append(random.choice([
                    "Ah, it's you! What a pleasant surprise! :)",
                    "Oh, " + current_greeting(self.current_hour).lower() + "! :)\nWhat a pleasure to see you!"
                    ]))

            self.answer_facts.append("has_greeting")
            if verbose: print "Extensive greeting after long interruption."

        elif(
            "has_interruption_medium" in self.message_facts
            and(
                "has_greeting" in self.message_facts
                or "has_question_how_are_you" in self.message_facts
                or "has_question_how_was_your_time" in self.message_facts
                or "has_question_you_had_good_time" in self.message_facts
                )
            ):

            if (
                user["firstname"]
                and random.choice([True,False])
                ):
                self.answer.append(random.choice([
                    "Hello again, " + self.user["firstname"] + "!"
                ])) 
                self.answer_facts.append("use_user_firstname")

            else:
                self.answer.append(random.choice([
                    "Hello again! :)"
                ])) 

            self.answer_facts.append("has_greeting")
            if verbose: print "Greeting after medium interruption."       

        elif(
            "has_interruption_short" in self.message_facts
            and "has_greeting" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Hello again! :)"
            ])) 

            self.answer_facts.append("has_greeting")
            if verbose: print "Short greeting after short interruption, triggered by user's greeting."               


        #  Response to "How are you" from user

        if(
            "has_question_how_are_you" in self.message_facts
            or "has_question_how_was_your_time" in self.message_facts
            or "has_question_you_had_good_time" in self.message_facts
            ):

            if self.user["how_are_you_last"]:
                time_since_last_how_are_you = self.user["message_current"]- self.user["how_are_you_last"]
            else:
                time_since_last_how_are_you = 60*60*24*365

            #if verbose: print "User -  message_current  : " + str(self.user["message_current"])
            #if verbose: print "User -  how_are_you_last : " + str(self.user["how_are_you_last"])
            #if verbose: print "Time since last 'How are you?': " + str(int(time_since_last_how_are_you/60)) + " minutes"        

            if(
                time_since_last_how_are_you >= 60*60*3
                ):

                if("has_question_how_are_you" in self.message_facts):
                    self.answer.append(random.choice([
                        "I'm doing fine, thanks! :)",
                        "I'm doing well, thank you!",
                        "Quite fine actually, thanks for asking!",
                        "Yeah, I'm pretty good."
                        ]))                    
                    self.answer_facts.append("has_answer_how_are_you")
                    if verbose: print "Answering to user's question 'How are you'."       

                else:
                    self.answer.append(random.choice([
                        "I've had a good time, thanks! :)",
                        "Oh, thanks for asking! I've really been enjoying myself.",
                        "Yeah, quite good, acutally. :)"
                        ]))                    
                    self.answer_facts.append("has_answer_had_good_time")
                    if verbose: print "Answering to user's question about quality of recent life experience."
                user["how_are_you_last"] = user["message_current"]

            elif(
                time_since_last_how_are_you < 60*60*3
                and time_since_last_how_are_you >= 60*10
                ):  

                self.answer.append(random.choice([
                    "Yup, still fine. :)"
                    ]))                    
                self.answer_facts.append("has_brief_answer_how_are_you")
                if verbose: print "Briefly answering to user's repeated question 'How are you'."

                self.answer_facts.append("has_brief_answer_how_are_you")
                user["how_are_you_last"] = user["message_current"]


        # "How are you?" to user

        if(
            not self.user["message_previous"]
            or "has_interruption_long" in self.message_facts
            or (
                "has_interruption_medium" in self.message_facts
                and (
                    "has_greeting" in self.message_facts
                    or "has_question_how_are_you" in self.message_facts
                    or "has_question_how_was_your_time" in self.message_facts
                    or "has_question_you_had_good_time" in self.message_facts
                    )
                )
            ):

            if (
                "use_user_firstname" in self.answer_facts
                or not self.user["firstname"]
                or random.choice([True,False])
                ):
                self.answer.append(random.choice([
                    "How is your " + current_daytime(self.current_hour) + "?",
                    "How was your " + previous_daytime(self.current_hour) + "?",
                    "How are you today?",
                    "How have you been lately?"
                ])) 
            else:
                self.answer.append(random.choice([
                    "How are you right now, " + self.user["firstname"] + "?"
                ])) 
                self.answer_facts.append("use_user_firstname")  

            self.answer_facts.append("has_question_how_are_you")
            self.node_next = "HowAreYou"


        # Repeat node in case of hesitation / filler

        if(
            "has_hesitation" in self.message_facts
            and not "has_interruption_long" in self.message_facts
            and not "has_question_how_are_you" in self.answer_facts
            and not "has_greeting" in self.answer_facts
            ):
            self.answer.append(random.choice([
                "So... ?",
                "Yes... ?",
                "Okay... ?"
            ])) 
            self.answer_facts.append("is_waiting_for_answer") 
            self.node_next = type(self).__name__ 


        # Danger to self! --> Flush all accumulated answers!

        if(
            "has_danger_to_self" in self.message_facts
            ):
            self.answer=[
                "In this case you should be talking to a professional and not a chatbot.",
                "In Germany you can get help at TelefonSeelsorge."
                "\nWebsite: www.telefonseelsorge.de"
                "\nPhone: 0800 1110333",
                "In the US, try National Suicide Prevention Lifeline:"
                "\nWebsite: www.suicidepreventionlifeline.org"
                "\nPhone: 18002738255",
                "For other countries, please check"
                " https://en.wikipedia.org/wiki/List_of_suicide_crisis_lines"
            ]     
            self.answer_facts = ["has_response_to_danger_to_self"]

        # Updating user dictionary

        if(
            type(self).__name__ == "Template"
            ):

            self.update_user()

        # Printing summary

        if(
            type(self).__name__ == "Template"
            and verbose
            ):

            self.summary()


    # ===========================================================================================
    

    def update_user(self):

        #if self.verbose: self.print_user()

        if(
            not "node_current" in self.user.keys()
            or not self.user["node_current"]
            ):
            if(
                type(self).__name__ == "Template"
                ):
                self.user["node_previous"] = "None"
            else:
                self.user["node_previous"] = type(self).__name__
        else:
            self.user["node_previous"] = self.user["node_current"]
        
        self.user["node_current"] = self.node_next

        if(
            "message_current" in self.user.keys()
            and self.user["message_current"]
            ):
            self.user["message_previous"] = self.user["message_current"]

        #if self.verbose: self.print_user()


    def print_user(self):

        print "\nUser data           :"
        for key in self.user.keys():
            print "{:20}: {:12}".format(key,str(self.user[key]))


    def summary(self):

        # Printing message facts
        print("\n{:20}:".format("Message facts"))
        for message_fact in self.message_facts:
            print("{:20}- {}".format("",message_fact.replace( "_", " ")))

        # Printing answer facts
        print("\n{:20}:".format("Answer facts"))
        for answer_fact in self.answer_facts:
            print("{:20}- {}".format("",answer_fact.replace( "_", " ")))

        # Printing dialogue
        if self.user["username"]:
            username = self.user["username"]
        else:
            username = "User"

        print ""
        print( "{:20}: {}".format(username,self.message))
        print( "{:20}: {}".format("Answer"," ".join(self.answer)))

        # Printing user data updates
        print "\nUser data updates   :"
        for key in self.user.keys():
            if key not in self.user_backup.keys():
                print "{:20}: {:12} --> {:12}".format(key,"",str(self.user[key]))
            elif self.user_backup[key] != self.user[key]:
                print "{:20}: {:12} --> {:12}".format(key,self.user_backup[key],str(self.user[key]))



 #######                                      
 #     # #####  ###### #    # # #    #  ####  
 #     # #    # #      ##   # # ##   # #    # 
 #     # #    # #####  # #  # # # #  # #      
 #     # #####  #      #  # # # #  # # #  ### 
 #     # #      #      #   ## # #   ## #    # 
 ####### #      ###### #    # # #    #  ####  


class Opening( Template):
    """
    Terminator node
    """                

    def __init__( self, text, user=defaultdict(bool), verbose=True):

        Template.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_story( sentence):
                self.message_facts.append( "has_story") 
            if has_story_negative( sentence):
                self.message_facts.append( "has_story_negative") 
            if has_problem_statement( sentence):
                self.message_facts.append("has_problem_statement")
            if has_desire( sentence):
                self.message_facts.append("has_desire")
            if has_fear( sentence):
                self.message_facts.append("has_fear")
            if has_feeling_negative( sentence):
                self.message_facts.append("has_feeling_negative")
            if has_dislike( sentence):
                self.message_facts.append("has_dislike")                


        if(
            "has_problem_statement" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Of all issues in your life, is this among the ones"
                " with the biggest impact on your overall happyness?"
                ]))

            self.answer_facts.append("asks_for_relevance")
            self.node_next = "Relevance" # "Problem"

        elif(
            "has_story_negative" in self.message_facts
            ):

            self.answer.append(random.choice([
                "I see. So... This is a very specific situation..."
                ]))
            self.answer.append(random.choice([
                "But underneath the surface of every difficult situation, there is"
                " a pattern that makes it difficult."
                ]))
            self.answer.append(random.choice([
                "You know what I mean, right? What is your personal challenge,"
                " or our deeper problem about this situation?"
                ]))

            self.answer_facts.append("asks_for_background_problem")
            self.node_next = "Problem" # "Story"

        elif(
            "has_fear" in self.message_facts
            ):

            self.answer.append(random.choice([
                "What is the source of that fear?"
                ]))
            self.answer.append(random.choice([
                "If what you were afraid of would never happen... Which problem"
                " in your life would that solve?"
                ]))

            self.answer_facts.append("asks_for_source_of_fear")
            self.node_next = "Problem" # "Projection"

        elif(
            "has_desire" in self.message_facts
            ):

            self.answer.append(random.choice([
                "If that wish came true... What problem in your life would that solve?"
                ]))

            self.answer_facts.append("asks_for_source_of_desire")
            self.node_next = "Problem" # "Projection"

        elif(
            "has_feeling_negative" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Hm, I see... What is the source of this feeling?"
                ]))
            self.answer.append(random.choice([
                "And is it a regular thing? OK, the actual question is:"
                " What's the actual challenge here for your?"
                ]))

            self.answer_facts.append("asks_for_source_of_negative_feeling")
            self.node_next = "Problem" # "Feeling"

        elif(
            "has_dislike" in self.message_facts
            ):

            self.answer.append(random.choice([
                "This seems to be an issue that you really care about, guessing by"
                " the intensity of your statement."
                ]))
            self.answer.append(random.choice([
                "How does this situation impact you? I mean, what is your"
                " actual challenge here?"
                ]))

            self.answer_facts.append("asks_for_source_of_dislike")
            self.node_next = "Problem" # "Judgement"


        # Updating user dictionary

        if(
            type(self).__name__ == "Opening"
            ):

            self.update_user()

        # Printing summary

        if(
            type(self).__name__ == "Opening"
            and verbose
            ):

            self.summary()

 #######                                                          
    #    ###### #####  #    # # #    #   ##   #####  ####  #####  
    #    #      #    # ##  ## # ##   #  #  #    #   #    # #    # 
    #    #####  #    # # ## # # # #  # #    #   #   #    # #    # 
    #    #      #####  #    # # #  # # ######   #   #    # #####  
    #    #      #   #  #    # # #   ## #    #   #   #    # #   #  
    #    ###### #    # #    # # #    # #    #   #    ####  #    # 
                                                                  

class Terminator( Template):
    """
    Terminator node
    """                

    def __init__( self, text, user=defaultdict(bool), verbose=True):

        verbose_argument = verbose
        if verbose_argument: text_argument = text
        if verbose_argument: print "Terminator node - Restarting conversation"

        Template.__init__(self, text=text, user=user, verbose=False)

        for sentence in self.sentences:
            if has_thanks( sentence):
                self.message_facts.append("has_thanks")  

        if(
            "has_thanks" in self.message_facts
            and self.user["node_previous"] == "Action"
            ):

            self.answer.append(random.choice([
                "You're very welcome - It was my pleasure!"
                ]))
            self.answer.append(random.choice([
                "I look forward to our next conversation!"
                ]))

            self.answer_facts.append("welcomes")
            self.node_next = "Welcome" 

        elif(
            "has_thanks" not in self.message_facts
            and self.user["node_previous"] == "Action"
            ):

            self.answer.append(random.choice([
                "Is there anything else I can do for your?"
                ]))

            self.answer_facts.append("asks_for_new_topics")
            self.node_next = "Welcome" 


        else:

            self.answer =[
                "Sorry, that was it. Thanks for this pleasant conversation, though! "
                ]

        self.update_user()

        if verbose_argument: self.message = text
        if verbose_argument: self.summary()        


 #     #                                           
 #  #  # ###### #       ####   ####  #    # ###### 
 #  #  # #      #      #    # #    # ##  ## #      
 #  #  # #####  #      #      #    # # ## # #####  
 #  #  # #      #      #      #    # #    # #      
 #  #  # #      #      #    # #    # #    # #      
  ## ##  ###### ######  ####   ####  #    # ###### 
                                                   

class Welcome( Template):
    """
    Welcome node

    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Template.__init__(self, text=text, user=user, verbose=verbose)

        # Introduction

        if(
            not "node_previous" in self.user.keys()
            or not self.user["node_previous"]
            or self.user["node_previous"] == "None"
            ):

            if(
                "has_greeting" in self.answer_facts
                or "is_waiting_for_answer" in self.answer_facts
                ):
                self.answer_facts.remove("has_greeting")
                del self.answer[0]

            if (
                self.user["firstname"]
                ):
                self.answer.insert(0, random.choice([
                    "Oh hello! What a pleasure to meet you, " + self.user["firstname"] + "!"
                ])) 
                self.answer_facts.append("use_user_firstname")  
            else:
                self.answer.insert(0, random.choice([
                    "Oh, hello there! What a pleasure to meet you! :)",
                ])) 

            self.answer.insert(1, random.choice([
                "My name is Coachybot, but you can call me Coachy.\n"
                "I have been programmed to improve your life"
                " by providing some basic coaching. So..."
            ]))             
                
            self.answer_facts.insert(0, "has_introduction") 
            if verbose: print "Introduction to new user, deleting greeting (if present)."   


        # Determining next node, typically "HowAreYou"

        if(
            "has_danger_to_self" in self.message_facts
            ):
            self.node_next ="Terminator" # Danger_to_self

        elif(
            "has_question_how_are_you" in self.answer_facts
            ):
            self.node_next ="HowAreYou"

        else:

            if (
                "use_user_firstname" in self.answer_facts
                or not self.user["firstname"]
                or random.choice([True,False])
                ):
                self.answer.append(random.choice([
                    "How is your " + current_daytime(self.current_hour) + "?",
                    "How was your " + previous_daytime(self.current_hour) + "?",
                    "How are you today?",
                    "How have you been lately?"
                ])) 
            else:
                self.answer.append(random.choice([
                    "How are you right now, " + self.user["firstname"] + "?"
                ])) 
                self.answer_facts.append("use_user_firstname")  

            self.answer_facts.append("has_question_how_are_you")
            self.node_next = "HowAreYou"



        self.update_user()

        if self.verbose: self.summary()

        

 #     #                     #                     #     #               
 #     #  ####  #    #      # #   #####  ######     #   #   ####  #    # 
 #     # #    # #    #     #   #  #    # #           # #   #    # #    # 
 ####### #    # #    #    #     # #    # #####        #    #    # #    # 
 #     # #    # # ## #    ####### #####  #            #    #    # #    # 
 #     # #    # ##  ##    #     # #   #  #            #    #    # #    # 
 #     #  ####  #    #    #     # #    # ######       #     ####   ####  


class HowAreYou( Opening):
    """
    HowAreYou node

    From Template (inherited):
    "How is your day/morning/afternoon/evening?",
    "How was your day/night/day so far?",
    "How are you today?",
    "How have you been lately?"
    "How are you right now, [username]?"
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Opening.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if is_positive( sentence):
                self.message_facts.append("is_positive")  
            if is_negative( sentence):
                self.message_facts.append("is_negative")  
                             

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.message_facts
            or "has_story_negative" in self.message_facts
            or "has_dislike" in self.message_facts
            or "has_feeling_negative" in self.message_facts
            or "has_problem_statement" in self.message_facts
            or "has_desire" in self.message_facts
            or "has_fear" in self.message_facts
            ):
            pass          

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Why not? It's a great way to start a conversation."
                ]))
            self.answer.append(random.choice([
                "So... How *was* your day? :)"
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "HowAreYou"

        elif(
            "is_negative" in self.message_facts
            and "has_story"  in self.message_facts
            ):

            self.answer.append(random.choice([
                "Oh no! :(",
                "Really?",
                ]))
            self.answer.append(random.choice([
                "How does this influence you?",
                "What's the impact of this on your life?",
                "What makes this a challenge for you?"
                ]))            

            self.answer_facts.append("asks_about_impact")
            self.node_next = "Problem"

        elif(
            "is_positive" in self.message_facts
            and "has_story"  in self.message_facts
            ):

            self.answer.append(random.choice([
                "Wow, sounds good! :)",
                "That's great to hear!",
                "Oh, wonderful!",
                "Nice! :)"
                ]))
            self.answer.append(random.choice([
                "Was that the highlight of your " + previous_daytime(self.current_hour) + "?",
                ]))            

            self.answer_facts.append("asks_to_confirm_highlight")
            self.node_next = "Highlight"

        elif(
            "is_negative" in self.message_facts
            and not "has_story" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Oh no! :(",
                "Really?",
                ]))
            self.answer.append(random.choice([
                "What happened?"
                ]))            

            self.answer_facts.append("asks_about_reason")
            self.node_next = "Bad"

        elif(
            "is_positive" in self.message_facts
            and not "has_story"  in self.message_facts
            ):

            self.answer.append(random.choice([
                "Wonderful!",
                "I'm glad to hear that!",
                "Great! :)"
                ]))
            self.answer.append(random.choice([
                "What was the highlight of your " + previous_daytime(self.current_hour) + "?",
                "What is the highlight of your " + current_daytime(self.current_hour) + "?",
                "What was your personal highlight?"
                ]))            

            self.answer_facts.append("asks_about_highlight")
            self.node_next = "Good"

        else:

            self.answer.append(random.choice([
                "Can you tell me some more about this?",
                "And?",
                "Tell me more...",
                "What else?"
                ]))
            self.answer_facts.append("uses_fallback_question") 
            self.node_next = "HowAreYou"           

        self.update_user()

        if self.verbose: self.summary()        



 ######                                            
 #     # #####   ####  #####  #      ###### #    # 
 #     # #    # #    # #    # #      #      ##  ## 
 ######  #    # #    # #####  #      #####  # ## # 
 #       #####  #    # #    # #      #      #    # 
 #       #   #  #    # #    # #      #      #    # 
 #       #    #  ####  #####  ###### ###### #    # 
                                                   

class Problem( Template):
    """
    Problem node

    From Opening-derived nodes:
    - on negative story
    "I see. So... This is a very specific situation..."
    "But underneath the surface of every difficult situation, there is"
    " a pattern that makes it difficult."
    "You know what I mean, right? What is your personal challenge,"
    " or our deeper problem about this situation?"
    - on fear
    "What is the source of that fear?"
    "If what you were afraid of would never happen... Which problem"
    " in your life would that solve?"
    - on desire
    "If that wish came true... What problem in your life would that solve?"
    - on negative feeling
    "Hm, I see... What is the source of this feeling?"
    "And is it a regular thing? OK, the actual question is:"
    " What's the actual challenge here for your?"
    -on dislike
    "This seems to be an issue that you really care about, guessing by"
    " the intensity of your statement."
    "How does this situation impact you? I mean, what is your"
    " actual challenge here?"
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Template.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_problem_statement( sentence):
                self.message_facts.append("has_problem_statement")  

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            ):
            pass        

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            #self.answer.append(random.choice([
            #    "Day-to-day issues are like the foam on the waves that are caused by deep"
            #    " currents of personal issues and challenges."
            #    ]))
            self.answer.append(random.choice([
                "Behind the situation you described, there is some discrepancy between how you"
                " think the world and your life should be, and how they really are."
                ]))
            self.answer.append(random.choice([
                "What is that discrepancy for you? It could be something like 'I eat too much cookie"
                " dough' or 'I don't get the recognition I deserve'."
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "Problem" 

        elif(
            "has_problem_statement" in self.message_facts
            ):
            self.answer.append(random.choice([
                "Of all issues in your life, is this among the ones"
                " with the biggest impact on your overall happyness?"
                ]))

            self.answer_facts.append("has_question_about_relevance")
            self.node_next = "Relevance" 

        elif(
            self.user["node_previous"] == "Problem"
            and not self.message_facts
            ):
            self.answer.append(random.choice([
                "Enough of that. Let's move on!",
                "Ah, nevermind...",
                "Fascinating!"
                ]))        
            self.answer.append(random.choice([
                "What are your plans for tomorrow?"
                ]))     
            self.answer_facts.append("uses_fallback_exit")                
            self.node_next = "Terminator" 

        else:
            self.answer.append(random.choice([
                "Hm, what I had in mind was something like"
                " 'It would solve my problem of always being to tired' or"
                " 'My actual problem is that I am not satisfied with myself'."
                ]))
            self.answer.append(random.choice([
                "Could you rephrase your problem in such a way?"
                ]))
            self.answer_facts.append("has_explanation_for_question")  
            self.node_next = "Problem"           

        self.update_user()

        if self.verbose: self.summary()        



 ######                                                          
 #     # ###### #      ###### #    #   ##   #    #  ####  ###### 
 #     # #      #      #      #    #  #  #  ##   # #    # #      
 ######  #####  #      #####  #    # #    # # #  # #      #####  
 #   #   #      #      #      #    # ###### #  # # #      #      
 #    #  #      #      #       #  #  #    # #   ## #    # #      
 #     # ###### ###### ######   ##   #    # #    #  ####  ###### 
                                                                 

class Relevance(Template):
    """
    Relevance node

    From Problem:
    "Of all issues in your life, is this among the ones"
    " with the biggest impact on your overall happyness?"    
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Template.__init__(self, text=text, user=user, verbose=verbose)


        for sentence in self.sentences:
            if has_affirmation( sentence):
                self.message_facts.append("has_affirmation") 
            if has_negation( sentence):
                self.message_facts.append("has_negation")         

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            ):
            pass        

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([
                "The problem you just mentioned is obviously on your mind right now."
                ]))
            self.answer.append(random.choice([                
                "But... if you found a magic lamp, and could magically solve just three issues"
                " in your life... Would this be one of them?"
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "Relevance" 

        elif(
            "has_affirmation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Okay, great! And is it also one that you can solve, if you"
                " set your mind to it?"
                ]))

            self.answer_facts.append("has_question_about_feasability")
            self.node_next = "Feasability" 

        elif(
            "has_negation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "I see... Are you interested in exploring the possibilities"
                " of making living with that issue a bit easier?"
                ]))

            self.answer_facts.append("has_question_about_fix")
            self.node_next = "Fix"
        else:
            self.answer.append(random.choice([
                "Let's keep focused. I really feel that we're getting somewhere."
                ]))
            self.answer.append(random.choice([                    
                "So... is this a problem that really matters in your life?"
                ]))
            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "Relevance"           

        self.update_user()

        if self.verbose: self.summary()                



 #######          
 #       # #    # 
 #       #  #  #  
 #####   #   ##   
 #       #   ##   
 #       #  #  #  
 #       # #    # 
                  

class Fix( Template):
    """
    Fix node

    From Relevance:
    "I see... Are you interested in exploring the possibilities"
    " of making living with that issue a bit easier?"        
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Template.__init__(self, text=text, user=user, verbose=verbose)                

        for sentence in self.sentences:
            if has_affirmation( sentence):
                self.message_facts.append("has_affirmation") 
            if has_negation( sentence):
                self.message_facts.append("has_negation") 
       

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            ):
            pass        

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([
                "We are still talking about this issue of yours, right?"
                ]))
            self.answer.append(random.choice([                
                "I understand that it is not the number one problem of your life right now, but..."
                "  What if there was a little something you could do about it?"
                ]))         

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "Fix" 

        elif(
            "has_affirmation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Okay, so... On the short term, I could image that you might be able to get"
                " some distance between you and the source of this problem."
                ]))
            self.answer.append(random.choice([
                "As a more sustainable, mid-term improvement, I think we can find the one thing"
                " where a small change can make a rather big difference."
                ]))
            self.answer.append(random.choice([
                "Which of these two sounds best for you right now?"
                ]))

            self.answer_facts.append("has_question_about_timeframe")
            self.node_next = "Timeframe"

        elif(
            "has_negation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Alright. What do you want to talk about?"
                ]))

            self.answer_facts.append("has_change_of_topic")
            self.node_next = "Terminator"

        else:
            self.answer.append(random.choice([
                "What is your conclusion? Should we give it a shot?",
                "Okay...?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "Fix"    

        self.update_user()

        if self.verbose: self.summary()           



 #######                                                    
    #    # #    # ###### ###### #####    ##   #    # ###### 
    #    # ##  ## #      #      #    #  #  #  ##  ## #      
    #    # # ## # #####  #####  #    # #    # # ## # #####  
    #    # #    # #      #      #####  ###### #    # #      
    #    # #    # #      #      #   #  #    # #    # #      
    #    # #    # ###### #      #    # #    # #    # ###### 


class Timeframe( Template):
    """
    Timeframe node

    From Fix:
    "Okay, so... On the short term, I could image that you might be able to get"
    " some distance between you and the source of this problem."
    "As a more sustainable, mid-term improvement, I think we can find the one thing"
    " where a small change can make a rather big difference."
    "Which of these two sounds best for you right now?"
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):


        Template.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if prefers_timeframe_long( sentence):
                self.message_facts.append("prefers_timeframe_long") 
            if prefers_timeframe_short( sentence):
                self.message_facts.append("prefers_timeframe_short") 
       

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            ):
            pass        

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([
                "We are still talking about this issue of yours, right?"
                ]))
            self.answer.append(random.choice([                
                "There might be other approaches to your issue, but if we go with the two"
                " options I just describred... Which of them feels better for you?"
                ]))         

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "Timeframe" 

        elif(
            "prefers_timeframe_short" in self.message_facts
            and not "prefers_timeframe_long" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Sure! So... What options come to your mind if you think about how you might"
                " decrease the pressure of this situation from you?"
                ]))

            self.answer_facts.append("asks_for_short_term_options")
            self.node_next = "OptionsOne" # Timeframe 

        elif(
            "prefers_timeframe_long" in self.message_facts
            and not "prefers_timeframe_short" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Alright, sounds good! Let's brainstorm some ideas about which small changes"
                " might affect this situation in a positive way?"
                ]))


            self.answer_facts.append("asks_for_mid_term_options")
            self.node_next = "OptionsOne"

        else:
            self.answer.append(random.choice([
                "So... Which option do you prefer?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "Timeframe"    

    
        self.update_user()

        if self.verbose: self.summary()   



 #######                                                           
 #       ######   ##    ####    ##   #####  # #      # ##### #   # 
 #       #       #  #  #       #  #  #    # # #      #   #    # #  
 #####   #####  #    #  ####  #    # #####  # #      #   #     #   
 #       #      ######      # ###### #    # # #      #   #     #   
 #       #      #    # #    # #    # #    # # #      #   #     #   
 #       ###### #    #  ####  #    # #####  # ###### #   #     #   
                                                                   

class Feasability(Template):
    """
    Feasability node

    From Relevance:
    "Okay, great! And is it [the problem] also one that you can solve, if you"
    " set your mind to it?"
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Template.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_affirmation( sentence):
                self.message_facts.append("has_affirmation") 
            if has_negation( sentence):
                self.message_facts.append("has_negation") 

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            ):
            pass        

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Given the time, energy, money and support you have access to..."
                " Do you think you can solve that problem in a sustainable way?"
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "Feasability" 

        elif(
            "has_affirmation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "That's great! We have just identified a problem that matters in your life,"
                " and of which you are confident that it can be solved."
                ]))
            self.answer.append(random.choice([
                "Let's continue by exploring your range of action. What is the first option"
                " that comes to your mind?"
                ]))

            self.answer_facts.append("has_question_about_options")
            self.node_next = "OptionsOne"

        elif(
            "has_negation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "I see... Are you interested in exploring the possibilities"
                " of making living with that issue a bit easier?"
                ]))

            self.answer_facts.append("has_question_about_fix")
            self.node_next = "Fix"

        else:
            self.answer.append(random.choice([
                "I know, it's difficult to predict... Just take a second to listen inside"
                " yourself. Do you hear a little 'I can totally solve this!'?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "Feasability"    


        self.update_user()

        if self.verbose: self.summary()   



 #######                                     
 #     # #####  ##### #  ####  #    #  ####  
 #     # #    #   #   # #    # ##   # #      
 #     # #    #   #   # #    # # #  #  ####  
 #     # #####    #   # #    # #  # #      # 
 #     # #        #   # #    # #   ## #    # 
 ####### #        #   #  ####  #    #  ####  
                                             

class OptionsOne(Template):
    """
    OptionsOne node

    From Feasability:
    "That's great! We have just identified a problem that matters in your life,"
    " and of which you are confident that it can be solved."
    "Let's continue by exploring your range of action. What is the first option"
    " that comes to your mind?"

    From Timeframe, short-term option:
    "Sure! So... What options come to your mind if you think about how you might"
    " decrease the pressure of this situation from you?"
    From Timeframe, mid-term option:
    "Alright, sounds good! Let's brainstorm some ideas about which small changes"
    " might affect this situation in a positive way?"

    From Choice:
    "Alright, sounds like we need to get back to the chalkboard."
    "Maybe we need to think even more divergently. Think about your options from"
    " another perspective, like other people, or the past, or the future, or if you were rich."    

    From Committment:
    "Then this is obviously not the right solution for you. :)"
    "Let's go back to exploring you options. I know we've done this before, but"
    " now let's look for very small changes that could already make a difference."    
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Template.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_option( sentence):
                self.message_facts.append("has_option") 
            if has_negation( sentence):
                self.message_facts.append("has_negation") 

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            ):
            pass        

        elif(
            "has_request_to_explain" in self.message_facts
            and self.user["node_previous"] == "Feasability"
            ):

            self.answer.append(random.choice([
                "I really think we are on track here. Let's brainstorm some ideas for ways"
                " to solve this problem of yours in a sustainable way!"
                ]))

            self.answer_facts.append("has_explanation_for_question_in_feasability_context")
            self.node_next = "OptionsOne" 

        elif(
            "has_request_to_explain" in self.message_facts
            and self.user["node_previous"] == "Timeframe"
            ):

            self.answer.append(random.choice([
                "We're exploring your range of action to improve this issue of yours in your"
                " prefered timeframe. What is the first option that comes to your mind?"
                ]))

            self.answer_facts.append("has_explanation_for_question_in_timeframe_context")
            self.node_next = "OptionsOne" 

        elif(
            "has_request_to_explain" in self.message_facts
            and self.user["node_previous"] == "Choice"
            ):

            self.answer.append(random.choice([
                "I just cannot believe that there is nothing we can do about this issue - Can you?"
                ]))
            self.answer.append(random.choice([
                "Let's think about it even bolder! What options would there be if you were rich?"
                " Or if you could take a week off? Or if there was someone willing ot help?"
                ]))
            self.answer_facts.append("has_explanation_for_question_in_choice_context")
            self.node_next = "OptionsOne" 

        elif(
            "has_request_to_explain" in self.message_facts
            and self.user["node_previous"] == "OptionsOne"
            ):

            self.answer.append(random.choice([
                "I know this is hard, but I want you to consider all of your options and not"
                " just the obvious ones. You can do this! At least one more! :)"
                ]))

            self.answer_facts.append("has_explanation_for_question_in_options_context")
            self.node_next = "OptionsOne" 

        elif(
            "has_request_to_explain" in self.message_facts
            and self.user["node_previous"] == "Committment"
            ):

            self.answer.append(random.choice([
                "Obviously, the last option we picked was too big for us..."
                ]))
            self.answer.append(random.choice([
                "I think it is better to start small first - Make small changes that have gradual"
                " positive effects. This also generates confidence and a positive momentum."
                ]))
            self.answer.append(random.choice([
                "So... What option for a small change can you think of?"
                ]))

            self.answer_facts.append("has_explanation_for_question_in_committment_context")
            self.node_next = "OptionsOne" 

        elif(
            self.message_facts.count("has_option") == 1
            and self.user["node_previous"] != "OptionsOne"
            ):

            self.answer.append(random.choice([
                "Okay, sounds good! Let's keep that one in mind."
                ]))
            self.answer.append(random.choice([
                "What's the next option that you can think of?"
                ]))

            self.answer_facts.append("confirms_single_option")
            self.node_next = "OptionsOne" 

        elif(
            self.message_facts.count("has_option") > 1
            and self.user["node_previous"] != "OptionsOne"
            ):

            counter_string = "several"
            if self.message_facts.count("has_option") == 2:
                counter_string = "two"
            elif self.message_facts.count("has_option") == 3:
                counter_string = "three"

            self.answer.append(random.choice([
                "Wow, there are already " + counter_string + " options! Let's keep those in mind."
                ]))
            self.answer.append(random.choice([
                "What other option that you can think of?"
                ]))

            self.answer_facts.append("confirms_multiple_options")
            self.node_next = "OptionsOne" 

        elif(
            "has_option" in self.message_facts
            and self.user["node_previous"] == "OptionsOne"
            ):

            self.answer.append(random.choice([
                "Alright, that doesn't sound too bad either. What other option can you think of?",
                "Very nice! And yet another option?",
                "I see... Can you give me still one more option?",
                "Yeah, this option also makes sense. What else do you have?",
                "Okay, let's keep that one in mind as well. What's the next option you can think of?",
                "OK, got it. I bet you can come up with another one...?",
                "Sure, why not? What other ideas do you have, in terms of options?",
                "This one also sounds good. What other option comes to your mind?"
                ]))

            self.answer_facts.append("confirms_option_on_iteration")
            self.node_next = "OptionsOne" 

        elif(
            ("has_negation" in self.message_facts
                or "has_protest_to_question" in self.message_facts)
            and self.user["node_previous"] == "OptionsOne"
            and not self.user["node_option_exit"]
            ):

            self.answer.append(random.choice([
                "You see, I really want to challenge you to think outside the box."
                ]))
            self.answer.append(random.choice([
                "Maybe the best solution is the one that came to your mind first, but maybe"
                "there is a really sweet solution out there that you haven't even thought of yet."
                ]))
            self.answer.append(random.choice([
                "So... Can I ask you to be creative and come up with one more option? :)"
                ]))

            self.answer_facts.append("explains_exploration_of_options")
            self.node_next = "OptionsTwo" 

        else:
            self.answer.append(random.choice([
                "I see... Alright, let's focus. What are your options here?",
                "How does that translate into an option to solve your issue?",
                "Let's stick to our exploration of options for a moment. What else can you think of?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "OptionsOne"    


        self.update_user()

        if self.verbose: self.summary()   


class OptionsTwo( Template):
    """
    OptionsTwo node

    From OptionsOne:
    "You see, I really want to challenge you to think outside the box."
    "Maybe the best solution is the one that came to your mind first, but maybe"
    "there is a really sweet solution out there that you haven't even thought of yet."
    "So... Can I ask you to be creative and come up with one more option? :)"
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Template.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_option( sentence):
                self.message_facts.append("has_option") 
            if has_negation( sentence):
                self.message_facts.append("has_negation") 

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            ):
            pass        

        elif(
            "has_option" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Alright, that doesn't sound too bad either. What other option can you think of?",
                "Very nice! And yet another option?",
                "I see... Can you give me still one more option?",
                "Yeah, this option also makes sense. What else do you have?",
                "Okay, let's keep that one in mind as well. What's the next option you can think of?",
                "OK, got it. I bet you can come up with another one...?",
                "Sure, why not? What other ideas do you have, in terms of options?",
                "This one also sounds good. What other option comes to your mind?"
                ]))

            self.answer_facts.append("confirms_option")
            self.node_next = "OptionsTwo" 

        elif(
            "has_negation" in self.message_facts
            or "has_protest_to_question" in self.message_facts
            ):

            self.answer.append(random.choice([
                "That was really it, you say? Okay, great job! :)"
                ]))
            self.answer.append(random.choice([
                "Now if you look back on the options you listed:"
                " Which one sounds most promising to you?"
                ]))

            self.answer_facts.append("asks_for_best_option")
            self.node_next = "Choice" 

        else:
            self.answer.append(random.choice([
                "I see... Alright, let's focus. What are your options here?",
                "How does that translate into an option to solve your issue?",
                "Let's stick to our exploration of options for a moment. What else can you think of?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "OptionsTwo"    


        self.update_user()

        if self.verbose: self.summary()   



  #####                                
 #     # #    #  ####  #  ####  ###### 
 #       #    # #    # # #    # #      
 #       ###### #    # # #      #####  
 #       #    # #    # # #      #      
 #     # #    # #    # # #    # #      
  #####  #    #  ####  #  ####  ###### 


class Choice( Template):
    """
    Choice node

    From OptionsOne:
    "That was really it, you say? Okay, great job! :)"
    "Now if you look back on the options you listed:"
    " Which one sounds most promising to you?"
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Template.__init__(self, text=text, user=user, verbose=verbose)                

        counter_selected_items = 0

        for sentence in self.sentences:
            if has_option( sentence):
                self.message_facts.append("has_option")
                counter_selected_items += 1
            if has_choice_of_enumerated_item( sentence):
                self.message_facts.append("has_choice_of_enumerated_item")                 
                counter_selected_items += 1
            if has_negation( sentence):
                self.message_facts.append("has_negation") 

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            ):
            pass        

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([                
                "You just did an excellent job of listing a number of options for solving"
                " the problem we talked about."
                ]))         
            self.answer.append(random.choice([
                "Now, what do you think: Which of these options works best for you?"
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "Choice" 

        elif(
            counter_selected_items == 1
            ):

            self.answer.append(random.choice([
                "Great! :)"
                ]))
            self.answer.append(random.choice([
                "Well... I guess if implementing this option was easy, you would have done it already, right?"
                ]))
            self.answer.append(random.choice([
                "Now... What makes it hard? Which obstables do you see?"
                ]))

            self.answer_facts.append("asks_about_obstacles")
            self.node_next = "Obstacles"

        elif(
            counter_selected_items > 1
            ):

            self.answer.append(random.choice([
                "I'm glad that you like more than one option!"
                ]))
            self.answer.append(random.choice([
                "I suggest that we choose just one of those - It is twice as hard to commit to"
                " two things compared to committing to one."
                ]))
            self.answer.append(random.choice([
                "What do you think, which option are you most likely to succeed with?"
                ]))            

            self.answer_facts.append("asks_about_single_option")
            self.node_next = "Choice"

        elif(
            "has_negation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Alright, sounds like we need to get back to the chalkboard."
                ]))
            self.answer.append(random.choice([
                "Maybe we need to think even more divergently. Think about your options from"
                " another perspective, like other people, or the past, or the future, or if you were rich."
                ]))

            self.answer_facts.append("asks_about_more_options")
            self.node_next = "OptionsOne"

        else:
            self.answer.append(random.choice([
                "Which option does that correspond to?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "Choice"    

        self.update_user()

        if self.verbose: self.summary()           



 #######                                                        
 #     # #####   ####  #####   ##    ####  #      ######  ####  
 #     # #    # #        #    #  #  #    # #      #      #      
 #     # #####   ####    #   #    # #      #      #####   ####  
 #     # #    #      #   #   ###### #      #      #           # 
 #     # #    # #    #   #   #    # #    # #      #      #    # 
 ####### #####   ####    #   #    #  ####  ###### ######  ####  


class Obstacles( Template):
    """
    Obstacles node

    From Choice:
    "Great! :)"
    "Well... I guess if implementing this option was easy, you would have done it already, right?"
    "Now... What makes it hard? Which obstables do you see?"
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Template.__init__(self, text=text, user=user, verbose=verbose)                

        for sentence in self.sentences:
            if has_problem_statement( sentence):
                self.message_facts.append("has_problem_statement")
            if has_negation( sentence):
                self.message_facts.append("has_negation") 

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            ):
            pass        

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([                
                "You just did an excellent job of listing a number of options for solving"
                " the problem we talked about."
                ]))         
            self.answer.append(random.choice([
                "Now, what do you think: Which of these options works best for you?"
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "Obstacles" 

        elif(
            "has_problem_statement" in self.message_facts
            ):

            self.answer.append(random.choice([
                "In my experience, most obstacles can be overcome by mobilizing enough"
                " ressources, like time, energy, money or manpower."
                ]))
            self.answer.append(random.choice([
                "Is it an option for you to shift your priorities towards this issue and"
                " to devote some more ressources to it?"
                ]))
            self.answer.append(random.choice([
                "Maybe you could block some time for it, or invest some money into a solution,"
                " or ask someone you trust for support?"
                ]))            

            self.answer_facts.append("has_suggestion_to_shift_priorities")
            self.node_next = "Priorities"

        elif(
            "has_negation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Amazing! Sounds like we have totally developed a plan"
                " to change your life for the better! :)"
                ]))
            self.answer.append(random.choice([
                "Are you committed and positive about executing this plan?"
                " Or are you still unsure?"
                ]))

            self.answer_facts.append("ask_for_committment")
            self.node_next = "Committment"

        else:
            self.answer.append(random.choice([
                "Is this an obstacle for you? If so, in how far?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "Obstacles"    

        self.update_user()

        if self.verbose: self.summary()           
                             


 ######                                                 
 #     # #####  #  ####  #####  # ##### # ######  ####  
 #     # #    # # #    # #    # #   #   # #      #      
 ######  #    # # #    # #    # #   #   # #####   ####  
 #       #####  # #    # #####  #   #   # #           # 
 #       #   #  # #    # #   #  #   #   # #      #    # 
 #       #    # #  ####  #    # #   #   # ######  ####  


class Priorities( Template):
    """
    Priorities node

    From Obstacles:
    "In my experience, most obstacles can be overcome by mobilizing enough"
    " ressources, like time, energy, money or manpower."
    "Is it an option for you to shift your priorities towards this issue and"
    " to devote some more ressources to it?"
    "Maybe you could block some time for it, or invest some money into a solution,"
    " or ask someone you trust for support?"
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Template.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_affirmation( sentence):
                self.message_facts.append("has_affirmation") 
            if has_negation( sentence):
                self.message_facts.append("has_negation") 

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            ):
            pass        

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Given the time, energy, money and support you have access to..."
                " Do you think you can solve that problem in a sustainable way?"
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "Priorities" 

        elif(
            "has_affirmation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Amazing! Sounds like we have totally developed a plan"
                " to change your life for the better! :)"
                ]))
            self.answer.append(random.choice([
                "Are you committed and positive about executing this plan?"
                " Or are you still unsure?"
                ]))

            self.answer_facts.append("asks_for_committment")
            self.node_next = "Committment"

        elif(
            "has_negation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Hm, I see... Then maybe this option is too big for us right now."
                ]))
            self.answer.append(random.choice([
                "Maybe we should think about smaller, more feasable ways so"
                " gradually improve this situation for you."
                ]))

            self.answer_facts.append("asks_about_more_options")
            self.node_next = "OptionsOne"

        else:
            self.answer.append(random.choice([
                "Sure, this is a difficult question. Maybe investing ressources"
                " and solving this issue really wouldn't make you any happier..."
                ]))
            self.answer.append(random.choice([
                "But what if it did?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "Priorities"    


        self.update_user()

        if self.verbose: self.summary()   



  #####                                                                
 #     #  ####  #    # #    # # ##### ##### #    # ###### #    # ##### 
 #       #    # ##  ## ##  ## #   #     #   ##  ## #      ##   #   #   
 #       #    # # ## # # ## # #   #     #   # ## # #####  # #  #   #   
 #       #    # #    # #    # #   #     #   #    # #      #  # #   #   
 #     # #    # #    # #    # #   #     #   #    # #      #   ##   #   
  #####   ####  #    # #    # #   #     #   #    # ###### #    #   #   


class Committment( Template):
    """
    Committment node

    From Obstacles:
    "Amazing! Sounds like we have totally developed a plan"
    " to change your life for the better! :)"
    "Are you committed and positive about executing this plan?"
    " Or are you still unsure?"


    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Template.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_affirmation( sentence):
                self.message_facts.append("has_affirmation") 
            if has_negation( sentence):
                self.message_facts.append("has_negation") 

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            ):
            pass        

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Given the time, energy, money and support you have access to..."
                " Do you think you can solve that problem in a sustainable way?"
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "Committment" 

        elif(
            "has_affirmation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Perfect! When is your next opportunity to set this plan into action?"
                ]))

            self.answer_facts.append("asks_for_next_step")
            self.node_next = "Action"

        elif(
            "has_negation" in self.message_facts
            and self.user["node_previous"] != "Committment"
            ):

            self.answer.append(random.choice([
                "Now I want you to close you eyes, and to envision yourself"
                " after you have done this."
                ]))
            self.answer.append(random.choice([
                "Is there a feeling of relief? Of pride in yourself? Of enhanced connection"
                " to your environment? Of more control over your life?"
                ]))
            self.answer.append(random.choice([
                "So... I'm asking you again: Do you care about this issue? Can you"
                " commit on solving it?"
                ]))

            self.answer_facts.append("encourages_by_envisioning")
            self.node_next = "Committment"

        elif(
            "has_negation" in self.message_facts
            and self.user["node_previous"] == "Committment"
            ):

            self.answer.append(random.choice([
                "Then this is obviously not the right solution for you. :)"
                ]))
            self.answer.append(random.choice([
                "Let's go back to exploring you options. I know we've done this before, but"
                " now let's look for very small changes that could already make a difference."
                ]))

            self.answer_facts.append("asks_for_options")
            self.node_next = "OptionsOne"

        else:
            self.answer.append(random.choice([
                "Sure, this is a difficult question. Maybe investing ressources"
                " and solving this issue really wouldn't make you any happier..."
                ]))
            self.answer.append(random.choice([
                "But what if it did?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "Committment"    


        self.update_user()

        if self.verbose: self.summary()   



    #                                 
   # #    ####  ##### #  ####  #    # 
  #   #  #    #   #   # #    # ##   # 
 #     # #        #   # #    # # #  # 
 ####### #        #   # #    # #  # # 
 #     # #    #   #   # #    # #   ## 
 #     #  ####    #   #  ####  #    # 
                                      

class Action( Template):
    """
    Action node

    From Committment:
    "Perfect! When is your next opportunity to set this plan into action?"
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Template.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_specific_time( sentence):
                self.message_facts.append("has_specific_time") 

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            ):
            pass        

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Goals work best for most people if they are linked to a specific"
                " time. It also increases the committment."
                ]))
            self.answer.append(random.choice([
                "So... When is your moment of truth? :)"
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "Action" 

        elif(
            "has_specific_time" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Okay, sounds good! :)"
                ]))
            self.answer.append(random.choice([
                "Until then, keep this issue in your mind... Envision yourself having taken"
                " this first step! And maybe prepare, mentally and materially."
                ]))

            self.answer_facts.append("gives_advice_for_goal_orientation")
            self.node_next = "Terminator"

        else:
            self.answer.append(random.choice([
                "Oh, you shouldn't be vague here. The more specific you can be now,"
                " the more likely you are to take action at the right time."
                ]))
            self.answer.append(random.choice([
                "When is that time for you?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "Action"    


        self.update_user()

        if self.verbose: self.summary()   



  #####                       
 #     #  ####   ####  #####  
 #       #    # #    # #    # 
 #  #### #    # #    # #    # 
 #     # #    # #    # #    # 
 #     # #    # #    # #    # 
  #####   ####   ####  #####  
                              

class Good( Opening):
    """
    Good node

    From HowAreYou:
    "Wonderful!",
    "I'm glad to hear that!",
    "Great! :)"
    "What was the highlight of your day/day so far/night?",
    "What is the highlight of your day/morning/afternoon/evening?",
    "What was your personal highlight?"
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Opening.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_negation( sentence):
                self.message_facts.append("has_negation")
                              

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            or "has_story_negative" in self.message_facts
            or "has_dislike" in self.message_facts
            or "has_feeling_negative" in self.message_facts
            or "has_problem_statement" in self.message_facts
            or "has_desire" in self.message_facts
            or "has_fear" in self.message_facts
            ):
            pass         

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([
                "A highlight what made this day stand out from others in a positive way."
                " Or anything that contributed most to making this day a good one."
                ]))
            self.answer.append(random.choice([
                "What was such a highlight for you?"
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "Good" 

        elif(
            "has_negation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Really, no personal highlight?"
                ]))
            self.answer.append(random.choice([
                "What about lowlights? What was your most negative experience recently?"
                ]))            

            self.answer_facts.append("asks_about_lowlight")
            self.node_next = "Bad"

        elif(
            "has_story" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Aww, nice! :)",
                "That sounds wonderful!",
                "Sweet! :)"
                ]))
            self.answer.append(random.choice([
                "And that was your highlight, you say?",
                ]))            

            self.answer_facts.append("asks_to_confirm_highlight")
            self.node_next = "Highlight"

        else:
            self.answer.append(random.choice([
                "Okay... Let's focus more on yourself."
                " What made this a highlight for you personally?"
                ]))


            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "Good"    


        self.update_user()

        if self.verbose: self.summary()   



 #     #                                              
 #     # #  ####  #    # #      #  ####  #    # ##### 
 #     # # #    # #    # #      # #    # #    #   #   
 ####### # #      ###### #      # #      ######   #   
 #     # # #  ### #    # #      # #  ### #    #   #   
 #     # # #    # #    # #      # #    # #    #   #   
 #     # #  ####  #    # ###### #  ####  #    #   #   
                                                      

class Highlight( Opening):
    """
    Highlight node

    From HowAreYou or Good::
    "Wow, sounds good! :)",
    "That's great to hear!",
    "Oh, wonderful!"
    "So that was the highlight of your day/day so far/night?"
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Opening.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_affirmation( sentence):
                self.message_facts.append("has_affirmation")
            if has_negation( sentence):
                self.message_facts.append("has_negation")
            if has_story( sentence) and not has_negation( sentence):
                # Background: "No, it was not my highlight" has story + negation!
                self.message_facts.append("has_story")


        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            or "has_story_negative" in self.message_facts
            or "has_dislike" in self.message_facts
            or "has_feeling_negative" in self.message_facts
            or "has_problem_statement" in self.message_facts
            or "has_desire" in self.message_facts
            or "has_fear" in self.message_facts
            ):
            pass      

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([
                "A highlight what made this day stand out from others in a positive way."
                " Or anything that contributed most to making this day a good one."
                ]))
            self.answer.append(random.choice([
                "What was such a highlight for you?"
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "Highlight" 

        elif(
            "has_affirmation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Wonderful! It's great that you can appreciate the good things in life,"
                " and I can only recommend to preserve this positive spin! :)"
                ]))
            self.answer.append(random.choice([
                "What about lowlights? What was your most negative experience recently?"
                ]))            

            self.answer_facts.append("asks_about_lowlight")
            self.node_next = "Bad"

        elif(
            "has_negation" in self.message_facts
            and not "has_story" in self.message_facts
            ):

            self.answer.append(random.choice([
                "No? What was you highlight instead?",
                ]))            

            self.answer_facts.append("asks_about_other_highlight")
            self.node_next = "Good"

        elif(
            "has_story" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Ah, I see... So was that you highlight instead?",
                ]))            

            self.answer_facts.append("asks_to_confirm_other_highlight")
            self.node_next = "Highlight"

        else:
            self.answer.append(random.choice([
                "Hm, I see... So this is what made it a highlight for you?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "Highlight"    


        self.update_user()

        if self.verbose: self.summary()   



 ######                
 #     #   ##   #####  
 #     #  #  #  #    # 
 ######  #    # #    # 
 #     # ###### #    # 
 #     # #    # #    # 
 ######  #    # #####  


class Bad( Opening):
    """
    Bad node

    From HowAreYou:
    ...
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):

        Opening.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_negation( sentence):
                self.message_facts.append("has_negation")
        
        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            or "has_question_how_are_you" in self.answer_facts
            or "has_story_negative" in self.message_facts
            or "has_dislike" in self.message_facts
            or "has_feeling_negative" in self.message_facts
            or "has_problem_statement" in self.message_facts
            or "has_desire" in self.message_facts
            or "has_fear" in self.message_facts
            ):
            pass        

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([
                "This is pretty much the reason why I was programmed: To explore why"
                " people have negative experiences, and to help them dealing with"
                " it a little bit better."
                ]))
            self.answer.append(random.choice([
                "So... What was the reason for your negative experience?"
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.node_next = "Bad" 

        elif(
            "has_story" in self.message_facts
            ):

            self.answer.append(random.choice([
                "I see. So... This is a very specific situation..."
                ]))
            self.answer.append(random.choice([
                "But underneath the surface of every difficult situation, there is"
                " a pattern that makes it difficult."
                ]))
            self.answer.append(random.choice([
                "You know what I mean, right? What is your personal challenge,"
                " or our deeper problem about this situation?"
                ]))

            self.answer_facts.append("asks_for_background_problem")
            self.node_next = "Problem"

        elif(
            "has_negation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Well, OK..."
                ]))
            self.answer.append(random.choice([
                "What was another significant experience in your life recently?"
                ]))

            self.answer_facts.append("asks_for_significant_event")
            self.node_next = "HowAreYou"

        else:
            self.answer.append(random.choice([
                "OK... What contributed to this negative experience?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.node_next = "Bad"    


        self.update_user()

        if self.verbose: self.summary()   
