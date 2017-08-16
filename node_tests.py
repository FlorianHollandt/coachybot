import unittest
import inspect

from datetime import datetime

from node_objects import Template
from node_objects import Opening
from node_objects import Welcome
from node_objects import HowAreYou
from node_objects import Terminator
from node_objects import Problem
from node_objects import Relevance
from node_objects import Feasability
from node_objects import Fix
from node_objects import Timeframe
from node_objects import OptionsOne
from node_objects import OptionsTwo
from node_objects import Choice
from node_objects import Obstacles
from node_objects import Priorities
from node_objects import Committment
from node_objects import Action
from node_objects import Good
from node_objects import Highlight
from node_objects import Bad

# -------------------------------------------------------------------------------------------

 #######                                                 
    #    ###### #    # #####  #        ##   ##### ###### 
    #    #      ##  ## #    # #       #  #    #   #      
    #    #####  # ## # #    # #      #    #   #   #####  
    #    #      #    # #####  #      ######   #   #      
    #    #      #    # #      #      #    #   #   #      
    #    ###### #    # #      ###### #    #   #   ###### 


class Test_Template(unittest.TestCase):
 
    def test_is_class( self):
        self.failUnless( isinstance( Template, object))
 
    def test_is_instance( self):
        test_node = Template( ".", verbose=False)
        self.failUnless( isinstance( test_node,Template))

    def test_has_method_summary( self):
        self.failUnless(
            "summary" in dir(Template)
            and inspect.ismethod(Template.summary))

    def test_expects_string_as_first_argument( self):
        with self.assertRaises( TypeError):
            test_node = Template( ["."], verbose=False)

    def test_expects_dict_as_second_argument( self):
        with self.assertRaises( TypeError):
            test_node = Template( ".", ("foo", "bar"), verbose=False)

    def test_expects_numeric_timestamp( self):
        with self.assertRaises( TypeError):
            test_node = Template( ".", {"timezone", "Berlin/Europe"}, verbose=False)

    def test_returns_answer_and_next_node_and_user( self):
        test_node = Template( ".", dict(), verbose=False)
        self.failUnless( 
            isinstance(test_node.answer, list) 
            and isinstance(test_node.next_node, str)
            and isinstance(test_node.user, dict) 
            )

    def test_has_optional_user_argument( self):
        test_node = Template( ".", verbose=False)
        self.failUnless( 
            isinstance(test_node.answer, list) 
            and isinstance(test_node.next_node, str)
            and isinstance(test_node.user, dict) 
            )

    def test_evaluate_keeps_unused_user_data_intact( self):
        test_user_before = {
            "foo" : "bar"
        }
        test_node = Template( ".", test_user_before, verbose=False)
        self.assertEqual(test_user_before["foo"], test_node.user["foo"])

    def test_silently_convert_user_dict_to_defaultdict( self):
        test_user = {
            "foo" : "bar"
        }
        test_node = Template( ".", test_user, verbose=False)
        self.failUnless(
        	test_node.user["foo"] == "bar"
        	and type(test_node.user).__name__ == "defaultdict")

    def test_returns_how_are_you_node( self):
        test_node = Template( ".", verbose=False)
        self.assertEqual( test_node.next_node, "HowAreYou")

    # This is a valid test, but it clutters the test output...
    #
    #def test_accepts_optional_verbose_argument( self):
    #    test_node = Template( ".", verbose=True)
    #    self.failUnless( test_node.verbose)

    def test_has_attribute_message_facts( self):
        test_node = Template( ".", verbose=False)
        self.failUnless("message_facts" in dir(test_node))

    def test_recognize_long_interruption( self):
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }
        test_node = Template( ".", test_user, verbose=False)
        self.failUnless( 
            "has_interruption_long" in test_node.message_facts
            and "has_interruption_medium" not in test_node.message_facts
            and "has_interruption_short" not in test_node.message_facts)

    def test_recognize_medium_interruption( self):
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501246800, # Friday, July 28, 2017 1:00:00 PM
        }
        test_node = Template( ".", test_user, verbose=False)
        self.failUnless( 
            "has_interruption_medium" in test_node.message_facts
            and "has_interruption_long" not in test_node.message_facts
            and "has_interruption_short" not in test_node.message_facts)

    def test_recognize_short_interruption( self):
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501232400, # Friday, July 28, 2017 9:00:00 AM
        }
        test_node = Template( ".", test_user, verbose=False)
        self.failUnless( 
            "has_interruption_short" in test_node.message_facts
            and "has_interruption_long" not in test_node.message_facts
            and "has_interruption_medium" not in test_node.message_facts)

    def test_recognize_morning_in_berlin( self):
        test_user = {
            "message_current"  : 1501221600, # Friday, July 28, 2017 8:00:00 AM GMT+02:00
            "timezone"         : 2
        }
        test_node = Template( ".", test_user, verbose=False)
        self.assertEqual(test_node.current_hour, 8)

    def test_recognize_time_without_timezone( self):
        test_user = {
            "message_current"  : 1501221600, # Friday, July 28, 2017 8:00:00 AM GMT+02:00
        }
        test_node = Template( ".", test_user, verbose=False)
        self.failUnless(test_node.current_hour is None)    

    def test_update_user_dictionary_nodes_empty( self):
        test_node = Template( ".", dict(), verbose=False)
        self.failUnless(
            test_node.user["node_previous"] == "None"
            and test_node.user["node_current"] == "HowAreYou")

    def test_update_user_dictionary_node_previous( self):
        test_user = {
            "node_current"  : "foo"
        }        
        test_node = Template( ".", test_user, verbose=False)
        self.assertEqual( test_node.user["node_previous"], "foo")

    def test_preprocessing_split_sentences( self):
        message = "Hey there! How are you?"
        test_node = Template( message, verbose=False)
        self.failUnless(len(test_node.sentences) == 2)

    def test_recognize_request_to_explain( self):
        message = "Why would you ask that?"
        test_node = Template( message, verbose=False)
        self.failUnless("has_request_to_explain"  in test_node.message_facts)        

    def test_recognize_protest( self):
        message = "Sorry, but that is none of you business!!!"
        test_node = Template( message, verbose=False)
        self.failUnless("has_protest_to_question"  in test_node.message_facts)      

    def test_recognize_greeting_with_how_are_you( self):
        message = "Hello, little robot! How are you doing?"
        test_node = Template( message, verbose=False)
        self.failUnless(
        	"has_greeting"  in test_node.message_facts
        	and "has_question_how_are_you"  in test_node.message_facts)

    def test_perform_greeting_after_long_interruption( self):
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }
        test_node = Template( ".", test_user, verbose=False)
        self.failUnless( 
            "has_greeting" in test_node.answer_facts)   

    def test_use_user_firstname_in_greeting( self):
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
            "firstname"        : "John"
        }
        test_node = Template( ".", test_user, verbose=False)
        self.failUnless( 
            "has_greeting" in test_node.answer_facts
            and "use_user_firstname" in test_node.answer_facts)     

    def test_perform_greeting_after_medium_interruption_with_greeting( self):
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501243200, # Friday, July 28, 2017 12:00:00 PM
            "firstname"        : "John"
        }
        message = "Hello! Still there? :)"
        test_node = Template( message, test_user, verbose=False)
        self.failUnless( 
            "has_greeting" in test_node.answer_facts)   

    def test_perform_no_greeting_after_medium_interruption_without_greeting( self):
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501243200, # Friday, July 28, 2017 12:00:00 PM
            "firstname"        : "John"
        }
        message = "Sorry, there was work to be done..."
        test_node = Template( message, test_user, verbose=False)
        self.failUnless( 
            "has_greeting" not in test_node.answer_facts
            and not test_node.next_node == "HowAreYou")         

    def test_perform_no_greeting_after_short_interruption_without_user_greeting( self):
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501232400, # Friday, July 28, 2017 9:00:00 AM
            "firstname"        : "John"
        }
        test_node = Template( ".", test_user, verbose=False)
        self.failUnless( 
            "has_greeting" not in test_node.answer_facts
            and not test_node.next_node == "HowAreYou")  

    def test_perform_greeting_after_short_interruption_with_user_greeting( self):
        message = "Hello, little robot! :)"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501232400, # Friday, July 28, 2017 9:00:00 AM
            "firstname"        : "John"
        }
        test_node = Template( message, test_user, verbose=False)
        self.failUnless( 
            "has_greeting" in test_node.answer_facts
            and not test_node.next_node == "HowAreYou")     

    def test_respond_to_first_time_how_are_you( self):
        message = "Hey there, how are you doing? :)"
        test_node = Template( message, "dev_standard_user", verbose=False)
        self.failUnless( 
            "has_question_how_are_you" in test_node.message_facts
            and "has_answer_how_are_you" in test_node.answer_facts)                      

    def test_respond_to_first_time_how_was_your_time( self):
        message = "By the way... Did you have a great day, too? :)"
        test_node = Template( message, "dev_standard_user", verbose=False)
        self.failUnless( 
            "has_question_you_had_good_time" in test_node.message_facts
            and "has_answer_had_good_time" in test_node.answer_facts)   

    def test_respond_to_recent_repetition_of_how_are_you( self):
        message = "How are you again?"
        test_user = {
            "how_are_you_last" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200, # Friday, July 28, 2017 7:00:00 AM
            "firstname"        : "Mary"
        }
        test_node = Template( message, test_user, verbose=False)
        self.failUnless( 
            "has_question_how_are_you" in test_node.message_facts
            and "has_brief_answer_how_are_you" in test_node.answer_facts)              

    def test_ask_how_are_you_at_first_time( self):
        message = "Oh, hello there! ;)"
        test_user = {
            "firstname"        : "Mary"
        }
        test_node = Template( message, test_user, verbose=False)
        self.failUnless( 
            "has_greeting" in test_node.message_facts
            and "has_greeting" in test_node.answer_facts
            and "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")  

    def test_ask_how_are_you_after_long_interruption_with_timezone( self):
        message = "Hello there, little robot!"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
            "timezone"         : 2,        
            "firstname"        : "Peter"
        }
        test_node = Template( message, test_user, verbose=False)
        self.failUnless( 
            "has_greeting" in test_node.message_facts
            and "has_greeting" in test_node.answer_facts
            and "has_interruption_long" in test_node.message_facts
            and "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")          

    def test_ask_how_are_you_after_medium_interruption_with_greeting( self):
        message = "Why, hello! So good to see YOU again!"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501243200, # Friday, July 28, 2017 12:00:00 PM
            "timezone"         : 2,        
            "firstname"        : "Peter"
        }
        test_node = Template( message, test_user, verbose=False)
        self.failUnless( 
            "has_greeting" in test_node.message_facts
            and "has_greeting" in test_node.answer_facts
            and "has_interruption_medium" in test_node.message_facts
            and "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")  

    def test_not_ask_how_are_you_after_medium_interruption_without_greeting( self):
        message = "Sorry, I just got distracted from our conversation..."
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501243200, # Friday, July 28, 2017 12:00:00 PM
            "timezone"         : 2,        
            "firstname"        : "Peter"
        }
        test_node = Template( message, test_user, verbose=False)
        self.failUnless( 
            "has_interruption_medium" in test_node.message_facts
            and "has_question_how_are_you" not in test_node.answer_facts)          

    def test_previous_node_none_if_no_current_node( self):
        test_node = Template( ".", dict(), verbose=False)
        self.failUnless( 
            test_node.user["node_previous"] == "None")   

    def test_next_node_how_are_you_if_no_current_node( self):
        test_node = Template( ".", dict(), verbose=False)
        self.failUnless( 
            test_node.user["node_current"] == "HowAreYou"
            and test_node.next_node == "HowAreYou")   

    def test_recognize_danger_to_self( self):
        message = "I am going to kill myself anyway..."
        test_node = Template( message, "dev_standard_user", verbose=False)
        self.failUnless( 
            "has_danger_to_self" in test_node.message_facts
            and "has_response_to_danger_to_self" in test_node.answer_facts)   

    def test_repeat_node_in_case_of_filler( self):
        message = "Well..."
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200  # Friday, July 28, 2017 7:00:00 AM          
        }                
        test_node = Template( message, test_user, verbose=False)
        self.failUnless(
            "has_hesitation" in test_node.message_facts
            and "is_waiting_for_answer" in test_node.answer_facts
            and test_node.next_node == "Template")            



 #######                                      
 #     # #####  ###### #    # # #    #  ####  
 #     # #    # #      ##   # # ##   # #    # 
 #     # #    # #####  # #  # # # #  # #      
 #     # #####  #      #  # # # #  # # #  ### 
 #     # #      #      #   ## # #   ## #    # 
 ####### #      ###### #    # # #    #  ####  
                                              

class Test_Opening_template( unittest.TestCase):
 
    def test_is_class( self):
        self.failUnless( isinstance( Opening, object))
 
    def test_is_instance( self):
        test_node = Opening( ".", verbose=False)
        self.failUnless( isinstance( test_node, Opening))

    def test_has_method_summary( self):
        self.failUnless(
            "summary" in dir(Opening)
            and inspect.ismethod(Opening.summary))

    def test_class_parent_is_Template( self):
        test_node = Opening( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")

    # -------- Inherited bahavior from Template ---------------------

    def test_respond_to_request_to_explain( self):
        message = "Why do you want to know how my day was???"
        test_node = HowAreYou( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    # -------- Node-specific behavior -------------------------------

    def test_recognizes_story( self):
        message = "i drank an entire bottle of gin."
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200  # Friday, July 28, 2017 7:00:00 AM          
        }          
        test_node = Opening( message, test_user, verbose=False)
        self.failUnless( 
            "has_story" in test_node.message_facts
            and test_node.next_node == "Terminator")

    def test_respond_to_negative_story( self):
        message = "i failed my driving test! :'("
        test_node = Opening( message, "dev_standard_user", verbose=False)
        self.failUnless( 
            "has_story_negative" in test_node.message_facts
            and "asks_for_background_problem" in test_node.answer_facts
            and test_node.next_node == "Problem")

    def test_respond_to_dislike( self):
        message = "i hate driving in the city!"
        test_node = Opening( message, "dev_standard_user", verbose=False)
        self.failUnless( 
            "has_dislike" in test_node.message_facts
            and "asks_for_source_of_dislike" in test_node.answer_facts
            and test_node.next_node == "Problem")

    def test_respond_to_negative_feeling( self):
        message = "i am so unbelievably disappointed of myself!"
        test_node = Opening( message, "dev_standard_user", verbose=False)
        self.failUnless( 
            "has_feeling_negative" in test_node.message_facts
            and "asks_for_source_of_negative_feeling" in test_node.answer_facts
            and test_node.next_node == "Problem")

    def test_respond_to_problem_statement( self):
        message = "i spend too much time on netflix instead of learning."
        test_node = Opening( message, "dev_standard_user", verbose=False)
        self.failUnless( 
            "has_problem_statement" in test_node.message_facts
            and "asks_for_relevance" in test_node.answer_facts
            and test_node.next_node == "Relevance")

    def test_respond_to_desire( self):
        message = "i wish i had learned to drive a car when i was younger"
        test_node = Opening( message, "dev_standard_user", verbose=False)
        self.failUnless( 
            "has_desire" in test_node.message_facts
            and "asks_for_source_of_desire" in test_node.answer_facts
            and test_node.next_node == "Problem")

    def test_respond_to_fear( self):
        message = "i am so afraid of failing this test!"
        test_node = Opening( message, "dev_standard_user", verbose=False)
        self.failUnless( 
            "has_fear" in test_node.message_facts
            and "asks_for_source_of_fear" in test_node.answer_facts
            and test_node.next_node == "Problem")

 #######                                                          
    #    ###### #####  #    # # #    #   ##   #####  ####  #####  
    #    #      #    # ##  ## # ##   #  #  #    #   #    # #    # 
    #    #####  #    # # ## # # # #  # #    #   #   #    # #    # 
    #    #      #####  #    # # #  # # ######   #   #    # #####  
    #    #      #   #  #    # # #   ## #    #   #   #    # #   #  
    #    ###### #    # #    # # #    # #    #   #    ####  #    # 
                                                                  

class Test_Terminator(unittest.TestCase):

    def test_class_parent_is_Template( self):
        test_node = Terminator( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")

    def test_respond_to_thank_you( self):
        message = "Thank you, Coachybot!"
        test_user = {
            "node_previous"    : "Action"          
        }        
        test_node = Terminator( message, test_user, verbose=False)
        self.failUnless(
            "has_thanks" in test_node.message_facts
            and "welcomes"  in test_node.answer_facts
            and test_node.next_node == "Welcome")

    def test_terminate_action_path( self):
        message = "Alright, let's see how that goes."
        test_user = {
            "node_previous"    : "Action"          
        }        
        test_node = Terminator( message, test_user, verbose=False)
        self.failUnless(
            "asks_for_new_topics"  in test_node.answer_facts
            and test_node.next_node == "Welcome")

 #     #                                           
 #  #  # ###### #       ####   ####  #    # ###### 
 #  #  # #      #      #    # #    # ##  ## #      
 #  #  # #####  #      #      #    # # ## # #####  
 #  #  # #      #      #      #    # #    # #      
 #  #  # #      #      #    # #    # #    # #      
  ## ##  ###### ######  ####   ####  #    # ###### 


class Test_Welcome( unittest.TestCase):

    def test_class_parent_is_Template( self):
        test_node = Welcome( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")

    def test_previous_node_is_welcome( self):
        test_node = Welcome( ".", dict(), verbose=False)
        self.failUnless( 
            test_node.user["node_previous"] == "Welcome")   

    # -------- Node-specific behavior -------------------------------

    def test_perform_introduction_at_first_contact( self):
        test_node = Welcome( ".", dict(), verbose=False)
        self.failUnless(
            "has_introduction" in test_node.answer_facts)        

    def test_perform_no_greeting_at_first_contact( self):
        test_node = Welcome( ".", dict(), verbose=False)
        self.failUnless(
            "has_greeting" not in test_node.answer_facts)   
  
    def test_respond_to_how_are_you_at_first_contact( self):
        message = "How are you? :)"
        test_node = Welcome( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_answer_how_are_you" in test_node.answer_facts)   

    def test_next_node_is_how_are_you_by_default( self):
        test_node = Welcome( ".", dict(), verbose=False)
        self.failUnless(
            "HowAreYou" in test_node.next_node
            and test_node.user["node_current"] == "HowAreYou"
            and test_node.user["node_previous"] == "Welcome")   

    def test_realistic_data( self):
        message = "Hello! Anyone there? :)"
        test_user = {
            "message_current"  : 1501243200, # Friday, July 28, 2017 12:00:00 PM
            "timezone"         : 2,        
            "firstname"        : "Magda",
            "username"         : "test_magda", 
            "node_current"     : "Welcome",           
        }
        test_node = Welcome( message, test_user, verbose=False)        
        self.failUnless(
            "HowAreYou" in test_node.next_node
            and "has_introduction" in test_node.answer_facts
            and "has_greeting" not in test_node.answer_facts
            and "has_question_how_are_you" in test_node.answer_facts
            and test_node.user["node_current"] == "HowAreYou"
            and test_node.user["node_previous"] == "Welcome"
            and test_node.user["message_previous"] == 1501243200)   

    def test_realistic_data_without_greeting( self):
        message = "So... what is this about?"
        test_user = {
            "message_current"  : 1501243200, # Friday, July 28, 2017 12:00:00 PM
            "timezone"         : 2,        
            "firstname"        : "Magda",
            "username"         : "test_magda", 
            "node_current"     : "Welcome",           
        }
        test_node = Welcome( message, test_user, verbose=False)        
        self.failUnless(
            "HowAreYou" in test_node.next_node
            and "has_introduction" in test_node.answer_facts
            and "has_greeting" not in test_node.answer_facts
            and "has_question_how_are_you" in test_node.answer_facts
            and test_node.user["node_current"] == "HowAreYou"
            and test_node.user["node_previous"] == "Welcome"
            and test_node.user["message_previous"] == 1501243200) 



 #     #                     #                     #     #               
 #     #  ####  #    #      # #   #####  ######     #   #   ####  #    # 
 #     # #    # #    #     #   #  #    # #           # #   #    # #    # 
 ####### #    # #    #    #     # #    # #####        #    #    # #    # 
 #     # #    # # ## #    ####### #####  #            #    #    # #    # 
 #     # #    # ##  ##    #     # #   #  #            #    #    # #    # 
 #     #  ####  #    #    #     # #    # ######       #     ####   ####  


class Test_HowAreYou(unittest.TestCase):

    def test_class_parent_is_Opening( self):
        test_node = HowAreYou( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Opening")

    # -------- Inherited bahavior from Template ---------------------

    def test_respond_to_request_to_explain( self):
        message = "Why do you want to know how my day was???"
        test_node = HowAreYou( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    def test_realistic_data_recognize_danger_to_self( self): # General Template response
        test_user = {
            "message_current"  : 1501243200, # Friday, July 28, 2017 12:00:00 PM
            "timezone"         : 2,        
            "firstname"        : "Magda",
            "username"         : "test_magda", 
            "node_current"     : "HowAreYou",           
        }
        message = "I am going to kill myself anyway..."
        test_node = HowAreYou( message, test_user, verbose=False)
        self.failUnless( 
            "has_danger_to_self" in test_node.message_facts
            and "has_response_to_danger_to_self" in test_node.answer_facts)   

    def test_use_fallback_question( self): # Standard behavior with node-specific text
        message = "Lorem ipsum dolor sit amet..."
        test_node = HowAreYou( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "uses_fallback_question" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    def test_repeat_at_first_fallback( self): # Standard behavior with node-specific text
        message = "Lorem ipsum dolor sit amet..."
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200, # Friday, July 28, 2017 7:00:00 AM       
            "node_previous"    : "Welcome",  
            "node_current"     : "HowAreYou"           
        }        
        test_node = HowAreYou( message, test_user, verbose=False)
        self.failUnless(
            "uses_fallback_question" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    # -------- Inherited bahavior from Opening ----------------------

    def test_respond_to_desire( self):
        message = "I wish I would wake up and this was all a dream!"
        test_node = HowAreYou( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_desire" in test_node.message_facts
            and "asks_for_source_of_desire" in test_node.answer_facts
            and test_node.next_node == "Problem")

    def test_respond_to_fear( self):
        message = "I'm afraid to loose a good friend because of this boy thing."
        test_node = HowAreYou( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_fear" in test_node.message_facts
            and "asks_for_source_of_fear" in test_node.answer_facts
            and test_node.next_node == "Problem")

    def test_respond_to_dislike( self):
        message = "I hate to be the one who has to apologize!"
        test_node = HowAreYou( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_dislike" in test_node.message_facts
            and "asks_for_source_of_dislike" in test_node.answer_facts
            and test_node.next_node == "Problem")

    def test_respond_to_negative_feeling( self):
        message = "I am so incredibly sad and disappointed about this situation!"
        test_node = HowAreYou( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_feeling_negative" in test_node.message_facts
            and "asks_for_source_of_negative_feeling" in test_node.answer_facts
            and test_node.next_node == "Problem")

    def test_respond_to_negative_story( self):
        message = "I forgot my wallet at work and had to go all the way back!"
        test_node = HowAreYou( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_story_negative" in test_node.message_facts
            and "asks_for_background_problem" in test_node.answer_facts
            and test_node.next_node == "Problem")

    def test_respond_to_problem_statement( self):
        message = "This is just too much for me to handle."
        test_node = HowAreYou( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_problem_statement" in test_node.message_facts
            and "asks_for_relevance" in test_node.answer_facts
            and test_node.next_node == "Relevance")


    # -------- Node-specific behavior -------------------------------

    # def test_exit_at_second_fallback( self): # Node-specific behavior
    #     message = "Lorem ipsum dolor sit amet..."
    #     test_user = {
    #         "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
    #         "message_current"  : 1501225200, # Friday, July 28, 2017 7:00:00 AM       
    #         "node_previous"    : "HowAreYou",  
    #         "node_current"     : "HowAreYou"           
    #     }        
    #     test_node = HowAreYou( message, test_user, verbose=False)
    #     self.failUnless(
    #         "uses_fallback_exit" in test_node.answer_facts
    #         and test_node.next_node == "Terminator")

    def test_respond_to_plain_positive_answer( self):
        message = "Quite good."
        test_node = HowAreYou( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "is_positive" in test_node.message_facts
            and "has_story" not  in test_node.message_facts
            and "asks_about_highlight" in test_node.answer_facts
            and test_node.next_node == "Good")

    def test_respond_to_positive_answer_with_story( self): 
        message = "Excellent! Tom invited me for dinner! :)"
        test_node = HowAreYou( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "is_positive" in test_node.message_facts
            and "has_story" in test_node.message_facts
            and "asks_to_confirm_highlight" in test_node.answer_facts
            and test_node.next_node == "Highlight")

    def test_respond_to_plain_negative_answer( self): 
        message = "Not so good, acutally..."
        test_node = HowAreYou( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "is_negative" in test_node.message_facts
            and "asks_about_reason" in test_node.answer_facts
            and test_node.next_node == "Bad")

    def test_respond_to_negative_answer_with_story( self): 
        message = "Horrible! I had a fight with my best friend..."
        test_node = HowAreYou( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "is_negative" in test_node.message_facts
            and "has_story" in test_node.message_facts
            and "asks_about_impact" in test_node.answer_facts
            and test_node.next_node == "Problem")

 ######                                            
 #     # #####   ####  #####  #      ###### #    # 
 #     # #    # #    # #    # #      #      ##  ## 
 ######  #    # #    # #####  #      #####  # ## # 
 #       #####  #    # #    # #      #      #    # 
 #       #   #  #    # #    # #      #      #    # 
 #       #    #  ####  #####  ###### ###### #    # 


class Test_Problem( unittest.TestCase):

    def test_class_parent_is_Template( self):
        test_node = Problem( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")

    # -------- Inherited bahavior from Template ---------------------

    # TODO: Explain in context of previous node
    def test_respond_to_request_to_explain( self):
        message = "What exactly do you mean?"
        test_node = Problem( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts)

    def test_repeat_at_fallback( self):
        message = "Well... I just want to be happy, that's all!"
        test_node = Problem( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "Problem")

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = Problem( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    # -------- Node-specific behavior -------------------------------

    def test_respond_to_problem_statement( self):
        message = "the general problem of not having a girlfriend, of course!"
        test_node = Problem( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_problem_statement" in test_node.message_facts
            and "has_question_about_relevance" in test_node.answer_facts
            and test_node.next_node == "Relevance")

    # These are good ideas for the next extension
    #
    # def test_exit_on_iterated_protest( self):
    #     message = "Fuck this stupid questioning about options!"
    #     test_user = {
    #         "node_previous" : "Problem"
    #     }
    #     test_node = Problem( message, test_user, verbose=False)
    #     self.failUnless(
    #         "has_protest_to_question" in test_node.message_facts
    #         and "asks_for_significant_event" in test_node.answer_facts
    #         and test_node.next_node == "HowAreYou")

    # def test_repeat_on_initial_protest( self):
    #     message = "Fuck this stupid questioning about options!"
    #     test_user = {
    #         "node_previous" : "Bad"
    #     }
    #     test_node = Problem( message, test_user, verbose=False)
    #     self.failUnless(
    #         "has_protest_to_question" in test_node.message_facts
    #         and "explains_definition_of_problem" in test_node.answer_facts
    #         and test_node.next_node == "Problem")

    # def test_exit_on_iterated_negation( self):
    #     message = "What? No."
    #     test_user = {
    #         "node_previous" : "Problem"
    #     }
    #     test_node = Problem( message, test_user, verbose=False)
    #     self.failUnless(
    #         "has_negation" in test_node.message_facts
    #         and "asks_for_significant_event" in test_node.answer_facts
    #         and test_node.next_node == "HowAreYou")


 ######                                                          
 #     # ###### #      ###### #    #   ##   #    #  ####  ###### 
 #     # #      #      #      #    #  #  #  ##   # #    # #      
 ######  #####  #      #####  #    # #    # # #  # #      #####  
 #   #   #      #      #      #    # ###### #  # # #      #      
 #    #  #      #      #       #  #  #    # #   ## #    # #      
 #     # ###### ###### ######   ##   #    # #    #  ####  ###### 


class Test_Relevance(unittest.TestCase):

    def test_class_parent_is_Template( self):
        test_node = Relevance( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")
 
    def test_respond_to_request_to_explain( self):
        message = "What do you mean?"
        test_node = Relevance( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "Relevance")        

    def test_repeat_at_fallback( self):
        message = "Blah blah blah..."
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200 # Friday, July 28, 2017 7:00:00 AM               
        }        
        test_node = Relevance( message, test_user, verbose=False)
        self.failUnless(
            "uses_fallback_repetition" in test_node.answer_facts
            and test_node.next_node == "Relevance")   

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = Relevance( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    def test_respond_to_affirmation( self):
        message = "Well... I would say so, sure."
        test_node = Relevance( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_affirmation" in test_node.message_facts
            and "has_question_about_feasability"  in test_node.answer_facts
            and test_node.next_node == "Feasability")

    def test_respond_to_negation( self):
        message = "Nah, not really.."
        test_node = Relevance( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "has_question_about_fix"  in test_node.answer_facts
            and test_node.next_node == "Fix")



 #######          
 #       # #    # 
 #       #  #  #  
 #####   #   ##   
 #       #   ##   
 #       #  #  #  
 #       # #    # 


class Test_Fix( unittest.TestCase):

    def test_class_parent_is_Template( self):
        test_node = Fix( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")
 
    def test_respond_to_request_to_explain( self):
        message = "Sorry?"
        test_node = Fix( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "Fix")        

    def test_repeat_at_fallback( self):
        message = "Lorem ipsum dolor sit amet..."
        test_node = Fix( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "uses_fallback_repetition" in test_node.answer_facts
            and test_node.next_node == "Fix")  

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = Fix( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    def test_respond_to_negation( self):
        message = "I dont think so."
        test_node = Fix( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "has_change_of_topic"  in test_node.answer_facts
            and test_node.next_node == "Terminator")                    

    def test_respond_to_affirmation( self):
        message = "Well... Sounds quite okay to me."
        test_node = Fix( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_affirmation" in test_node.message_facts
            and "has_question_about_timeframe"  in test_node.answer_facts
            and test_node.next_node == "Timeframe")                    



 #######                                                    
    #    # #    # ###### ###### #####    ##   #    # ###### 
    #    # ##  ## #      #      #    #  #  #  ##  ## #      
    #    # # ## # #####  #####  #    # #    # # ## # #####  
    #    # #    # #      #      #####  ###### #    # #      
    #    # #    # #      #      #   #  #    # #    # #      
    #    # #    # ###### #      #    # #    # #    # ###### 


class Test_Timeframe( unittest.TestCase):

    def test_class_parent_is_Template( self):
        test_node = Timeframe( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")
 
    def test_respond_to_request_to_explain( self):
        message = "Sorry?"
        test_node = Timeframe( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "Timeframe")        

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = Timeframe( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    def test_recognize_preference_for_short_term_solution( self):
        message = "I guess the quick solution would be best for me right now."
        test_node = Timeframe( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "prefers_timeframe_short" in test_node.message_facts
            and "asks_for_short_term_options" in test_node.answer_facts
            and test_node.next_node == "OptionsOne")        

    def test_recognize_preference_for_long_term_solution( self):
        message = "Both would be good, but I'd rather pursue the sustainable one."
        test_node = Timeframe( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "prefers_timeframe_long" in test_node.message_facts
            and "asks_for_mid_term_options" in test_node.answer_facts
            and test_node.next_node == "OptionsOne")
        
    def test_ignore_if_no_preference_for_timeframe( self):
        message = "the quick solution is good, and the sustainable one  as well."
        test_node = Timeframe( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "prefers_timeframe_long" in test_node.message_facts
            and "prefers_timeframe_short" in test_node.message_facts
            and "uses_fallback_repetition" in test_node.answer_facts
            and test_node.next_node == "Timeframe")        



 #######                                                           
 #       ######   ##    ####    ##   #####  # #      # ##### #   # 
 #       #       #  #  #       #  #  #    # # #      #   #    # #  
 #####   #####  #    #  ####  #    # #####  # #      #   #     #   
 #       #      ######      # ###### #    # # #      #   #     #   
 #       #      #    # #    # #    # #    # # #      #   #     #   
 #       ###### #    #  ####  #    # #####  # ###### #   #     #   
                                                                   

class Test_Feasability(unittest.TestCase):

    def test_class_parent_is_Template( self):
        test_node = Feasability( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")
 
    def test_respond_to_request_to_explain( self):
        message = "What?"
        test_node = Feasability( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "Feasability")        

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = Feasability( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    def test_respond_to_affirmation( self):
        message = "Sure!"
        test_node = Feasability( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_affirmation" in test_node.message_facts
            and "has_question_about_options"  in test_node.answer_facts
            and test_node.next_node == "OptionsOne")                    

    def test_respond_to_negation( self):
        message = "Probably not."
        test_node = Feasability( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "has_question_about_fix"  in test_node.answer_facts
            and test_node.next_node == "Fix")



 #######                                     
 #     # #####  ##### #  ####  #    #  ####  
 #     # #    #   #   # #    # ##   # #      
 #     # #    #   #   # #    # # #  #  ####  
 #     # #####    #   # #    # #  # #      # 
 #     # #        #   # #    # #   ## #    # 
 ####### #        #   #  ####  #    #  ####  
                                             

class Test_OptionsOne( unittest.TestCase):

    def Template( self):
        test_node = OptionsOne( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")
 
    # -------- Inherited bahavior from Template ---------------------

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = OptionsOne( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    def test_use_fallback_repetition( self):
        message = "Gumba lumba wumbaba!"
        test_node = OptionsOne( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "uses_fallback_repetition" in test_node.answer_facts
            and test_node.next_node == "OptionsOne")

    # -------- Node-specific behavior -------------------------------

    def test_respond_to_request_to_explain_in_feasability_context( self):
        message = "What?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200, # Friday, July 28, 2017 7:00:00 AM          
            "node_previous"    : "Feasability"
        }                
        test_node = OptionsOne( message, test_user, verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question_in_feasability_context" in test_node.answer_facts
            and test_node.next_node == "OptionsOne")        

    def test_respond_to_request_to_explain_in_timeframe_context( self):
        message = "What?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200, # Friday, July 28, 2017 7:00:00 AM          
            "node_previous"    : "Timeframe"
        }                
        test_node = OptionsOne( message, test_user, verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question_in_timeframe_context" in test_node.answer_facts
            and test_node.next_node == "OptionsOne")

    def test_respond_to_request_to_explain_in_options_context( self):
        message = "What?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200, # Friday, July 28, 2017 7:00:00 AM          
            "node_previous"    : "OptionsOne"
        }                
        test_node = OptionsOne( message, test_user, verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question_in_options_context" in test_node.answer_facts
            and test_node.next_node == "OptionsOne")

    def test_respond_to_request_to_explain_in_choice_context( self):
        message = "Sorry?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200, # Friday, July 28, 2017 7:00:00 AM          
            "node_previous"    : "Choice"
        }                
        test_node = OptionsOne( message, test_user, verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question_in_choice_context" in test_node.answer_facts
            and test_node.next_node == "OptionsOne")

    def test_respond_to_request_to_explain_in_committment_context( self):
        message = "Sorry?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200, # Friday, July 28, 2017 7:00:00 AM          
            "node_previous"    : "Committment"
        }                
        test_node = OptionsOne( message, test_user, verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question_in_committment_context" in test_node.answer_facts
            and test_node.next_node == "OptionsOne")

    def test_respond_to_single_option( self):
        message = "I could go to the gym once a week."
        test_node = OptionsOne( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_option" in test_node.message_facts
            and "confirms_single_option" in test_node.answer_facts
            and test_node.next_node == "OptionsOne")

    def test_respond_to_multiple_options( self):
        message = "I might ask to be on the Big Data project. Or even apply for a different job..."
        test_node = OptionsOne( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_option" in test_node.message_facts
            and "confirms_multiple_options" in test_node.answer_facts
            and test_node.next_node == "OptionsOne")

    def test_respond_to_option_on_iteration( self):
        message = "Meeting more of my old friends would also be good for me."
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200, # Friday, July 28, 2017 7:00:00 AM                          
            "node_previous"    : "OptionsOne"
        }            
        test_node = OptionsOne( message, test_user, verbose=False)
        self.failUnless(
            "has_option" in test_node.message_facts
            and "confirms_option_on_iteration" in test_node.answer_facts
            and test_node.next_node == "OptionsOne")

    def test_explain_after_negation_on_iteration( self):
        message = "I really can't think of anything else."
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200, # Friday, July 28, 2017 7:00:00 AM                          
            "node_previous"    : "OptionsOne"
        }            
        test_node = OptionsOne( message, test_user, verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "explains_exploration_of_options" in test_node.answer_facts
            and test_node.next_node == "OptionsTwo")

    def test_repeat_after_initial_negation( self):
        message = "Nothing really..."
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200, # Friday, July 28, 2017 7:00:00 AM                          
            "node_previous"    : "Feasability"
        }        
        test_node = OptionsOne( message, test_user, verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "uses_fallback_repetition" in test_node.answer_facts
            and test_node.next_node == "OptionsOne")

    def test_explain_after_protest_on_iteration( self):
        message = "Fuck this stupid questioning about options!"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200, # Friday, July 28, 2017 7:00:00 AM                          
            "node_previous"    : "OptionsOne"
        }            
        test_node = OptionsOne( message, test_user, verbose=False)
        self.failUnless(
            "has_protest_to_question" in test_node.message_facts
            and "explains_exploration_of_options" in test_node.answer_facts
            and test_node.next_node == "OptionsTwo")


class Test_OptionsTwo( unittest.TestCase):

    def Template( self):
        test_node = OptionsTwo( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")

    # -------- Inherited bahavior from Template ---------------------
 
    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = OptionsTwo( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    def test_use_fallback_repetition( self):
        message = "Gumba lumba wumbaba!"
        test_node = OptionsTwo( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "uses_fallback_repetition" in test_node.answer_facts
            and test_node.next_node == "OptionsTwo")

    # -------- Node-specific behavior -------------------------------

    def test_respond_to_option( self):
        message = "I could go to the gym once a week."
        test_node = OptionsTwo( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_option" in test_node.message_facts
            and "confirms_option" in test_node.answer_facts
            and test_node.next_node == "OptionsTwo")

    def test_exit_on_negation( self):
        message = "Sorry, but really no more option comes to my mind."
        test_node = OptionsTwo( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "asks_for_best_option" in test_node.answer_facts
            and test_node.next_node == "Choice")

  #####                                
 #     # #    #  ####  #  ####  ###### 
 #       #    # #    # # #    # #      
 #       ###### #    # # #      #####  
 #       #    # #    # # #      #      
 #     # #    # #    # # #    # #      
  #####  #    #  ####  #  ####  ###### 


class Test_Choice( unittest.TestCase):

    def test_class_parent_is_Template( self):
        test_node = Choice( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")

    def test_respond_to_request_to_explain( self):
        message = "What?"
        test_node = Choice( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "Choice")        

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = Choice( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    def test_accept_choice_of_single_option( self):
        message = "The last one sounded quite exciting!"
        test_node = Choice( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_choice_of_enumerated_item" in test_node.message_facts
            and "asks_about_obstacles" in test_node.answer_facts
            and test_node.next_node == "Obstacles")        

    def test_reject_choice_of_multiple_options( self):
        message = "The second one sounded good. But I also like the last one."
        test_node = Choice( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_choice_of_enumerated_item" in test_node.message_facts
            and "asks_about_single_option" in test_node.answer_facts
            and test_node.next_node == "Choice")
                                       
    def test_redirect_to_options_if_none_selected( self):
        message = "I don't know, neither of them sound realistic."
        test_node = Choice( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "asks_about_more_options" in test_node.answer_facts
            and test_node.next_node == "OptionsOne")                                       



 #######                                                        
 #     # #####   ####  #####   ##    ####  #      ######  ####  
 #     # #    # #        #    #  #  #    # #      #      #      
 #     # #####   ####    #   #    # #      #      #####   ####  
 #     # #    #      #   #   ###### #      #      #           # 
 #     # #    # #    #   #   #    # #    # #      #      #    # 
 ####### #####   ####    #   #    #  ####  ###### ######  ####  
                                                                

class Test_Obstacles( unittest.TestCase):

    def test_class_parent_is_Template( self):
        test_node = Obstacles( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")
 
    def test_respond_to_request_to_explain( self):
        message = "What?"
        test_node = Obstacles( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "Obstacles")        

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = Obstacles( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    def test_respond_to_problem_statement( self):
        message = "I don't have time to deal with this!"
        test_node = Obstacles( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_problem_statement" in test_node.message_facts
            and "has_suggestion_to_shift_priorities" in test_node.answer_facts
            and test_node.next_node == "Priorities")

    def test_respond_to_negation( self):
        message = "No, I could actually start doing this right now."
        test_node = Obstacles( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "ask_for_committment" in test_node.answer_facts
            and test_node.next_node == "Committment")   



 ######                                                 
 #     # #####  #  ####  #####  # ##### # ######  ####  
 #     # #    # # #    # #    # #   #   # #      #      
 ######  #    # # #    # #    # #   #   # #####   ####  
 #       #####  # #    # #####  #   #   # #           # 
 #       #   #  # #    # #   #  #   #   # #      #    # 
 #       #    # #  ####  #    # #   #   # ######  ####  

                           
class Test_Priorities( unittest.TestCase):

    def test_class_parent_is_Template( self):
        test_node = Priorities( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")

    def test_respond_to_request_to_explain( self):
        message = "What?"
        test_node = Priorities( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "Priorities")        

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = Priorities( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    def test_respond_to_affirmation( self):
        message = "Well... Probably yes."
        test_node = Priorities( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_affirmation" in test_node.message_facts
            and "asks_for_committment"  in test_node.answer_facts
            and test_node.next_node == "Committment")                    

    def test_respond_to_negation( self):
        message = "Quite certainly not!"
        test_node = Priorities( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "asks_about_more_options"  in test_node.answer_facts
            and test_node.next_node == "OptionsOne")

                             

  #####                                                                
 #     #  ####  #    # #    # # ##### ##### #    # ###### #    # ##### 
 #       #    # ##  ## ##  ## #   #     #   ##  ## #      ##   #   #   
 #       #    # # ## # # ## # #   #     #   # ## # #####  # #  #   #   
 #       #    # #    # #    # #   #     #   #    # #      #  # #   #   
 #     # #    # #    # #    # #   #     #   #    # #      #   ##   #   
  #####   ####  #    # #    # #   #     #   #    # ###### #    #   #   


class Test_Committment( unittest.TestCase):

    def test_class_parent_is_Template( self):
        test_node = Committment( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")
 
    def test_respond_to_request_to_explain( self):
        message = "What?"
        test_node = Committment( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "Committment")        

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = Committment( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    def test_respond_to_affirmation( self):
        message = "Absolutely!"
        test_node = Committment( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_affirmation" in test_node.message_facts
            and "asks_for_next_step"  in test_node.answer_facts
            and test_node.next_node == "Action")                    

    def test_respond_to_negation_first_time( self):
        message = "Well... Somehow not really."
        test_node = Committment( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "encourages_by_envisioning"  in test_node.answer_facts
            and test_node.next_node == "Committment")

    def test_respond_to_negation_second_time( self):
        message = "No, still not."
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501225200, # Friday, July 28, 2017 7:00:00 AM
            "node_previous"    : "Committment"          
        }        
        test_node = Committment( message, test_user, verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "asks_for_options"  in test_node.answer_facts
            and test_node.next_node == "OptionsOne")



    #                                 
   # #    ####  ##### #  ####  #    # 
  #   #  #    #   #   # #    # ##   # 
 #     # #        #   # #    # # #  # 
 ####### #        #   # #    # #  # # 
 #     # #    #   #   # #    # #   ## 
 #     #  ####    #   #  ####  #    # 
                                      

class Test_Action( unittest.TestCase):

    def Template( self):
        test_node = Action( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Template")
 
    def test_respond_to_request_to_explain( self):
        message = "What?"
        test_node = Action( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "Action")        

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = Action( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    def test_respond_to_specific_time( self):
        message = "Right tomorrow morning."
        test_node = Action( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_specific_time" in test_node.message_facts
            and "gives_advice_for_goal_orientation"  in test_node.answer_facts
            and test_node.next_node == "Terminator")                    



  #####                       
 #     #  ####   ####  #####  
 #       #    # #    # #    # 
 #  #### #    # #    # #    # 
 #     # #    # #    # #    # 
 #     # #    # #    # #    # 
  #####   ####   ####  #####  
                              

class Test_Good( unittest.TestCase):

    def test_class_parent_is_Opening( self):
        test_node = Good( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Opening")

    # -------- Inherited bahavior from Template ---------------------
 
    def test_respond_to_request_to_explain( self):
        message = "What do you mean?"
        test_node = Good( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "Good")        

    def test_repeat_at_fallback( self):
        message = "Gobbledigook!"
        test_node = Good( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "uses_fallback_repetition" in test_node.answer_facts
            and test_node.next_node == "Good")

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = Good( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    # -------- Inherited bahavior from Opening ----------------------

    def test_respond_to_negative_story( self):
        message = "In fact, I was too late for training..."
        test_node = Good( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_story_negative" in test_node.message_facts
            and "asks_for_background_problem" in test_node.answer_facts
            and test_node.next_node == "Problem")

    def test_respond_to_problem_statement( self):
        message = "I have too much stress to enjoy any highlights"
        test_node = Good( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_problem_statement" in test_node.message_facts
            and "asks_for_relevance"  in test_node.answer_facts
            and test_node.next_node == "Relevance")      

    # -------- Node-specific behavior -------------------------------

    def test_respond_to_story( self):
        message = "I looked at myself in the mirror! :D"
        test_node = Good( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_story" in test_node.message_facts
            and "asks_to_confirm_highlight"  in test_node.answer_facts
            and test_node.next_node == "Highlight")                    

    def test_respond_to_negation( self):
        message = "I didn't have any particular highlight..."
        test_node = Good( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "asks_about_lowlight"  in test_node.answer_facts
            and test_node.next_node == "Bad")                   


 #     #                                              
 #     # #  ####  #    # #      #  ####  #    # ##### 
 #     # # #    # #    # #      # #    # #    #   #   
 ####### # #      ###### #      # #      ######   #   
 #     # # #  ### #    # #      # #  ### #    #   #   
 #     # # #    # #    # #      # #    # #    #   #   
 #     # #  ####  #    # ###### #  ####  #    #   #   
                                                      

class Test_Highlight( unittest.TestCase):

    def test_class_parent_is_Opening( self):
        test_node = Highlight( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Opening")
 
    # -------- Inherited bahavior from Template ---------------------

    def test_respond_to_request_to_explain( self):
        message = "What do you mean?"
        test_node = Highlight( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "Highlight")        

    def test_repeat_at_fallback( self):
        message = "Yadda yadda..."
        test_node = Highlight( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "uses_fallback_repetition" in test_node.answer_facts
            and test_node.next_node == "Highlight")

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = Highlight( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    # -------- Node-specific behavior -------------------------------

    def test_respond_to_affirmation( self):
        message = "Yes, that was my highlight. :)"
        test_node = Highlight( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_affirmation" in test_node.message_facts
            and "asks_about_lowlight"  in test_node.answer_facts
            and test_node.next_node == "Bad")                    

    def test_respond_to_plain_negation( self):
        #message = "Well... No, not my absolute highlight." <- TODO
        message = "No, not really."
        test_node = Highlight( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "asks_about_other_highlight"  in test_node.answer_facts
            and test_node.next_node == "Good")

    def test_respond_to_negation_with_story( self):
        message = "No. My highlight was that I found 5 Euros on the street!"
        test_node = Highlight( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "has_story" in test_node.message_facts
            and "asks_to_confirm_other_highlight"  in test_node.answer_facts
            and test_node.next_node == "Highlight")

    def test_respond_to_plain_story( self):
        message = "Well... My actual highlight was meeting my friend for coffee."
        test_node = Highlight( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_story" in test_node.message_facts
            and "asks_to_confirm_other_highlight"  in test_node.answer_facts
            and test_node.next_node == "Highlight")



 ######                
 #     #   ##   #####  
 #     #  #  #  #    # 
 ######  #    # #    # 
 #     # ###### #    # 
 #     # #    # #    # 
 ######  #    # #####  


class Test_Bad( unittest.TestCase):   

    def test_class_parent_is_Opening( self):
        test_node = Bad( ".", verbose=False)
        self.failUnless( 
            test_node.__class__.__bases__[0].__name__ == "Opening")

    # -------- Inherited bahavior from Template ---------------------

    def test_respond_to_request_to_explain( self):
        message = "What do you mean?"
        test_node = Bad( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_request_to_explain" in test_node.message_facts
            and "has_explanation_for_question" in test_node.answer_facts
            and test_node.next_node == "Bad")        

    def test_repeat_at_fallback( self):
        message = "Yadda yadda..."
        test_node = Bad( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "uses_fallback_repetition" in test_node.answer_facts
            and test_node.next_node == "Bad")

    def test_return_to_how_are_you_after_long_interruption( self):
        message = "What did we just talk about?"
        test_user = {
            "message_previous" : 1501221600, # Friday, July 28, 2017 6:00:00 AM
            "message_current"  : 1501264800, # Friday, July 28, 2017 6:00:00 PM
        }        
        test_node = Bad( message, test_user, verbose=False)
        self.failUnless(
            "has_question_how_are_you" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")

    # -------- Inherited bahavior from Opening ----------------------

    def test_respond_to_negative_story( self):
        message = "I lost my wallet! :("
        test_node = Bad( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_story_negative" in test_node.message_facts
            and "asks_for_background_problem"  in test_node.answer_facts
            and test_node.next_node == "Problem")                    

    def test_respond_to_problem_statement( self):
        message = "I did not have enough time for my girlfriend today."
        test_node = Bad( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_problem_statement" in test_node.message_facts
            and "asks_for_relevance"  in test_node.answer_facts
            and test_node.next_node == "Relevance")

    def test_respond_to_dislike( self):
        message = "i hate this town!"
        test_node = Bad( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_dislike" in test_node.message_facts
            and "asks_for_source_of_dislike"  in test_node.answer_facts
            and test_node.next_node == "Problem")                    

    def test_respond_to_negative_feeling( self):
        message = "i am so incredibly tired!"
        test_node = Bad( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_feeling_negative" in test_node.message_facts
            and "asks_for_source_of_negative_feeling"  in test_node.answer_facts
            and test_node.next_node == "Problem")                       

    def test_respond_to_desire( self):
        message = "if only i was twenty years younger..."
        test_node = Bad( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_desire" in test_node.message_facts
            and "asks_for_source_of_desire"  in test_node.answer_facts
            and test_node.next_node == "Problem")

    def test_respond_to_fear( self):
        message = "i am afraid to fail the driver license test."
        test_node = Bad( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_fear" in test_node.message_facts
            and "asks_for_source_of_fear"  in test_node.answer_facts
            and test_node.next_node == "Problem")

    # -------- Node-specific behavior -------------------------------

    def test_respond_to_story( self):
        message = "I forgot to water the plants and now they are all dead! :("
        test_node = Bad( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_story" in test_node.message_facts
            and "asks_for_background_problem" in test_node.answer_facts
            and test_node.next_node == "Problem")

    def test_respond_to_negation( self):
        message = "Nothing..."
        test_node = Bad( message, "dev_standard_user", verbose=False)
        self.failUnless(
            "has_negation" in test_node.message_facts
            and "asks_for_significant_event" in test_node.answer_facts
            and test_node.next_node == "HowAreYou")


# ===========================================================================================

if __name__ == '__main__':
    unittest.main()        