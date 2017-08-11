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


        # Instance attributes

        self.message       = text
        self.message_facts = []
        self.answer        = []
        self.answer_facts  = []
        self.current_hour  = None
        self.next_node     = "Terminator"
        self.user          = user
        self.user_backup   = user_backup
        self.verbose       = verbose
     

        # Recognizing disruptions

        if all(key in user.keys() for key in ("message_current", "message_previous")):
            time_since_last_message = user["message_current"] - user["message_previous"]
            if(
                time_since_last_message >= 11*60*60
                ):
                self.message_facts.append("interruption_long")
                if verbose: print "Long interruption of more than 11 hours..."
            elif(
                time_since_last_message < 11*60*60
                and time_since_last_message >= 5*60*60
                ):
                self.message_facts.append("interruption_medium")
                if verbose: print "Medium interruption of more than 5 hours..."
            elif(
                time_since_last_message < 5*60*60
                and time_since_last_message >= 2*60*60
                ):
                self.message_facts.append("interruption_short")      
                if verbose: print "Short interruption of more than 2 hours..."


        # Recognizing time of day

        if all(key in user.keys() for key in ("message_current", "timezone")):
            current_time = datetime.fromtimestamp(user["message_current"],tz=timezone(user["timezone"])).time()
            self.current_hour = int(str(current_time)[:2])
            if verbose: print "Current time in " + user["timezone"] + ": " + str(self.current_hour)
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
            "interruption_long" in self.message_facts
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
            "interruption_medium" in self.message_facts
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
            "interruption_short" in self.message_facts
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
            or "interruption_long" in self.message_facts
            or (
                "interruption_medium" in self.message_facts
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


        # Repeat node in case of hesitation / filler

        if(
            "has_hesitation" in self.message_facts
            and not "interruption_long" in self.message_facts
            and not "has_question_how_are_you" in self.answer_facts
            and not "has_greeting" in self.answer_facts
            ):
            self.answer.append(random.choice([
                "So... ?",
                "Yes... ?",
                "Okay... ?"
            ])) 
            self.answer_facts.append("is_waiting_for_answer") 
            self.next_node = type(self).__name__ 


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
        
        self.user["node_current"] = self.next_node

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
    #    ###### #####  #    # # #    #   ##   #####  ####  #####  
    #    #      #    # ##  ## # ##   #  #  #    #   #    # #    # 
    #    #####  #    # # ## # # # #  # #    #   #   #    # #    # 
    #    #      #####  #    # # #  # # ######   #   #    # #####  
    #    #      #   #  #    # # #   ## #    #   #   #    # #   #  
    #    ###### #    # #    # # #    # #    #   #    ####  #    # 
                                                                  

class Terminator(Template):
    """
    Welcome node
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):
        """
        Evaluates user input under consideration of the user history.

        Arguments:
            - text            Mandatory                    A string, can contain several sentences
            - user            Optional (empty dict)        A dictionary of facts about the user and their history
            - verbose         Optional (True)              A flag to hide or display state information
        """

        verbose_argument = verbose
        if verbose_argument: text_argument = text
        if verbose_argument: print "Terminator node - Restarting conversation"

        Template.__init__(self, text=".", user=user, verbose=False)


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
                                                   

class Welcome(Template):
    """
    Welcome node
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):
        """
        Evaluates user input under consideration of the user history.

        Arguments:
            - text            Mandatory                    A string, can contain several sentences
            - user            Optional (empty dict)        A dictionary of facts about the user and their history
            - verbose         Optional (True)              A flag to hide or display state information
        """

        Template.__init__(self, text=text, user=user, verbose=verbose)

        # Introduction

        if(
            not "node_previous" in self.user.keys()
            or not self.user["node_previous"]
            or self.user["node_previous"] == "None"
            ):

            if(
                "has_greeting" in self.answer_facts
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


        # Determining next node, typically "How_are_you"

        if(
            "has_danger_to_self" in self.message_facts
            ):
            self.next_node ="Terminator" # Danger_to_self
        elif(
            "has_question_how_are_you" in self.answer_facts
            ):
            self.next_node ="How_are_you"


        self.update_user()

        if self.verbose: self.summary()

        

 #     #                     #                     #     #               
 #     #  ####  #    #      # #   #####  ######     #   #   ####  #    # 
 #     # #    # #    #     #   #  #    # #           # #   #    # #    # 
 ####### #    # #    #    #     # #    # #####        #    #    # #    # 
 #     # #    # # ## #    ####### #####  #            #    #    # #    # 
 #     # #    # ##  ##    #     # #   #  #            #    #    # #    # 
 #     #  ####  #    #    #     # #    # ######       #     ####   ####  


class How_are_you(Template):
    """
    How_are_you node
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):
        """
        Evaluates user input under consideration of the user history.

        Arguments:
            - text            Mandatory                    A string, can contain several sentences
            - user            Optional (empty dict)        A dictionary of facts about the user and their history
            - verbose         Optional (True)              A flag to hide or display state information
        """

        Template.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_desire( sentence):
                self.message_facts.append("has_desire")  

        if(
            "has_danger_to_self" in self.message_facts
            ):
            self.next_node ="Terminator" # Danger_to_self            ):

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Oh, that's a great way to start a conversation, right?"
                "\nWhat would you rather talk about?"
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.next_node = "Terminator" #"How_are_you"

        elif(
            "has_desire" in self.message_facts
            ):

            self.answer.append(random.choice([
                "If that wish came true... What problem in your life would that solve?"
                ]))

            self.answer_facts.append("is_questioning_desire")
            self.next_node = "Problem" #"Goal"

        elif(
            not self.message_facts
            and self.user["node_previous"] == "How_are_you"
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
            self.next_node = "Terminator" 

        else:

            self.answer.append(random.choice([
                "Can you tell me some more about this?"
                ]))
            self.answer_facts.append("uses_fallback_question") 
            self.next_node = "How_are_you"           

        self.update_user()

        if self.verbose: self.summary()        



 ######                                            
 #     # #####   ####  #####  #      ###### #    # 
 #     # #    # #    # #    # #      #      ##  ## 
 ######  #    # #    # #####  #      #####  # ## # 
 #       #####  #    # #    # #      #      #    # 
 #       #   #  #    # #    # #      #      #    # 
 #       #    #  ####  #####  ###### ###### #    # 
                                                   

class Problem(Template):
    """
    Problem node
    """                

    def __init__(self, text, user=defaultdict(bool), verbose=True):
        """
        Evaluates user input under consideration of the user history.

        Arguments:
            - text            Mandatory                    A string, can contain several sentences
            - user            Optional (empty dict)        A dictionary of facts about the user and their history
            - verbose         Optional (True)              A flag to hide or display state information
        """

        Template.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_problem_statement( sentence):
                self.message_facts.append("has_problem_statement")  

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
            ):
            pass        

        elif(
            "has_request_to_explain" in self.message_facts
            ):

            self.answer.append(random.choice([
                "That's what wishes and goals are about, right?"
                " There's something in life that is not quite right."
                " What's that something for you?"
                ]))

            self.answer_facts.append("has_explanation_for_question")
            self.next_node = "Problem" 

        elif(
            "has_problem_statement" in self.message_facts
            ):
            self.answer.append(random.choice([
                "Of all issues in your life, is this among the ones"
                " with the biggest impact on your overall happyness?"
                ]))

            self.answer_facts.append("has_question_about_relevance")
            self.next_node = "Relevance" 

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
            self.next_node = "Terminator" 

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
            self.next_node = "Problem"           

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
        """
        Evaluates user input under consideration of the user history.

        Arguments:
            - text            Mandatory                    A string, can contain several sentences
            - user            Optional (empty dict)        A dictionary of facts about the user and their history
            - verbose         Optional (True)              A flag to hide or display state information
        """

        Template.__init__(self, text=text, user=user, verbose=verbose)


        for sentence in self.sentences:
            if has_affirmation( sentence):
                self.message_facts.append("has_affirmation") 
            if has_negation( sentence):
                self.message_facts.append("has_negation")         

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
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
            self.next_node = "Relevance" 

        elif(
            "has_affirmation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Okay, great! And is it also one that you can solve, if you"
                " set your mind to it?"
                ]))

            self.answer_facts.append("has_question_about_feasability")
            self.next_node = "Feasability" 

        elif(
            "has_negation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "I see... Are you interested in exploring the possibilities"
                " of making living with that issue a bit easier?"
                ]))

            self.answer_facts.append("has_question_about_fix")
            self.next_node = "Fix"
        else:
            self.answer.append(random.choice([
                "Let's keep focused. I really feel that we're getting somewhere."
                ]))
            self.answer.append(random.choice([                    
                "So... is this a problem that really matters in your life?"
                ]))
            self.answer_facts.append("uses_fallback_repetition")  
            self.next_node = "Relevance"           

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
        """
        Evaluates user input under consideration of the user history.

        Arguments:
            - text            Mandatory                    A string, can contain several sentences
            - user            Optional (empty dict)        A dictionary of facts about the user and their history
            - verbose         Optional (True)              A flag to hide or display state information
        """

        Template.__init__(self, text=text, user=user, verbose=verbose)                

        for sentence in self.sentences:
            if has_affirmation( sentence):
                self.message_facts.append("has_affirmation") 
            if has_negation( sentence):
                self.message_facts.append("has_negation") 
       

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
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
            self.next_node = "Fix" 

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
            self.next_node = "Terminator" # Timeframe 

        elif(
            "has_negation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Alright. What do you want to talk about?"
                ]))

            self.answer_facts.append("has_change_of_topic")
            self.next_node = "Terminator"

        else:
            self.answer.append(random.choice([
                "What is your conclusion? Should we give it a shot?",
                "Okay...?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.next_node = "Fix"    

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
        """
        Evaluates user input under consideration of the user history.

        Arguments:
            - text            Mandatory                    A string, can contain several sentences
            - user            Optional (empty dict)        A dictionary of facts about the user and their history
            - verbose         Optional (True)              A flag to hide or display state information
        """

        Template.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if prefers_timeframe_long( sentence):
                self.message_facts.append("prefers_timeframe_long") 
            if prefers_timeframe_short( sentence):
                self.message_facts.append("prefers_timeframe_short") 
       

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
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
            self.next_node = "Timeframe" 

        elif(
            "prefers_timeframe_short" in self.message_facts
            and not "prefers_timeframe_long" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Sure! So... What options come to your mind if you think about how you might"
                " decrease the pressure of this situation from you?"
                ]))

            self.answer_facts.append("asks_for_short_term_options")
            self.next_node = "Options" # Timeframe 

        elif(
            "prefers_timeframe_long" in self.message_facts
            and not "prefers_timeframe_short" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Alright, sounds good! Let's brainstorm some ideas about which small changes"
                " miht affect this situation in a positive way?"
                ]))


            self.answer_facts.append("asks_for_mid_term_options")
            self.next_node = "Options"

        else:
            self.answer.append(random.choice([
                "So... Which option do you prefer?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.next_node = "Timeframe"    

    
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
        """
        Evaluates user input under consideration of the user history.

        Arguments:
            - text            Mandatory                    A string, can contain several sentences
            - user            Optional (empty dict)        A dictionary of facts about the user and their history
            - verbose         Optional (True)              A flag to hide or display state information
        """

        Template.__init__(self, text=text, user=user, verbose=verbose)

        for sentence in self.sentences:
            if has_affirmation( sentence):
                self.message_facts.append("has_affirmation") 
            if has_negation( sentence):
                self.message_facts.append("has_negation") 

        if(     # Standard cases
            "has_danger_to_self" in self.message_facts
            or "has_hesitation" in self.message_facts
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
            self.next_node = "Feasability" 

        elif(
            "has_affirmation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "That's great! So... What are your options?"
                ]))

            self.answer_facts.append("has_question_about_options")
            self.next_node = "Options"

        elif( # Needs work!
            "has_negation" in self.message_facts
            ):

            self.answer.append(random.choice([
                "Ah, nevermind! Let's talk about something else then."
                ]))

            self.answer_facts.append("has_change_of_topic")
            self.next_node = "Terminator"

        else:
            self.answer.append(random.choice([
                "I know, it's difficult to predict... Just take a second to listen inside"
                " yourself. Do you hear a little 'I can totally solve this!'?"
                ]))

            self.answer_facts.append("uses_fallback_repetition")  
            self.next_node = "Feasability"    


        self.update_user()

        if self.verbose: self.summary()   

