import unittest
import inspect

from skills import *

class Test_Skills( unittest.TestCase):

	def test_current_daytime_if_none( self):
		self.failUnless( current_daytime( None)=="day")

	def test_previous_daytime_if_none( self):
		self.failUnless( previous_daytime( None)=="day")

	def test_next_daytime_if_none( self):
		self.failUnless( next_daytime( None)=="day")

	def test_current_greeting_if_none( self):
		self.failUnless( current_greeting( None)=="Hello")				

	def test_current_daytime_if_morning( self):
		self.failUnless( current_daytime( 9)=="morning")

	def test_questions_how_are_you_positive( self):
		messages = [
		"how are you?",
		"hey, how are you doing?",
		"how is it going?",
		"anyway, how is it going?",
		"how are you right now?",
		"how do you do?"
		]
		self.failUnless( all( has_question_how_are_you( message) for message in messages))

	def test_questions_how_are_you_negative( self):
		messages = [
		"how are you doing this trick?",
		"I do not care about how you are doing!",
		"how are you going to explain this?",
		"how is the fit going?",
		"what is up there on the tree?"
		]
		self.failUnless( not any( has_question_how_are_you( message) for message in messages))

	def test_questions_how_was_your_time_positive( self):
		messages = [
		"how was your day?",
		"hey, how was your weekend, little robot?",
		"how has your summer been lately?"
		"so... how was your day so far?"
		]
		self.failUnless( all( has_question_how_was_your_time( message) for message in messages))

	def test_questions_how_was_your_time_negative( self):
		messages = [
		"how was your visit from your uncle?",
		"how was your weekly training?",
		"how has your lunch been?"
		]
		self.failUnless( not any( has_question_how_was_your_time( message) for message in messages))

	def test_questions_you_had_good_time_positive( self):
		messages = [
		"did you have a good time lately?",
		"did you have a good night?",
		"tell me... have you had a lovely summer so far?",
		"did you have some good time today?"
		"and did you have a good time?"
		]
		self.failUnless( all( has_question_you_had_good_time( message) for message in messages))

	def test_questions_you_had_good_time_negative( self):
		messages = [
		"did you have a good daycare when you were young?",
		"did you have some great experiences today?",
		"have you had a good nights sleep?",
		"when did you have a good time?",
		"how did you have a good time?",
		"but... why did you have a good time?",
		"who did you have a good time with?",
		"what did you have a good time for?"
		]
		self.failUnless( not any( has_question_you_had_good_time( message) for message in messages))		

	def test_greeting_positive( self):
		messages = [
		"oh, hello there!",
		"good morning, little robot!",
		"hi!",
		"hey there!",
		"howdy, cowboy!"
		]
		self.failUnless( all( has_greeting( message) for message in messages))

	def test_greeting_negative( self):
		messages = [
		"i did not even say hello to this person.",
		"hit the road, jack!",
		"it has been hellofa day!",
		"a good evening with my friends would be fine.",
		"and then i said 'howdy, cowboy!'.",
		"but... why did you have a good time?",
		"hey, stop talking like a robot!",
		"hey there, what are you doing this for?",
		"hey there, what do you thin you are doing?"
		]
		self.failUnless( not any( has_greeting( message) for message in messages))

	def test_desire_positive( self):
		messages = [
		"i wish i was rich.",
		"if only i were better looking...",
		"my goal is to be the richest man on earth.",		
		"i hope to be the best looking man at the party.",
		"i hope i get promoted this year!",
		"i hope ben will not be at the party.",
		"it would be best if we had a cat.",
		"i wish someone would have helped me."
		]
		self.failUnless( all( has_desire( message) for message in messages))

	def test_desire_negative( self):
		messages = [
		"my wishes and desires are nobody's business!",
		"i hope for rain.",
		"it would not be good if there would be even more rain.",
		"i wished to get a doll and i did not get one.",
		"i wish you would just shut up!",
		"i hope you understand me!"
		]
		self.failUnless( not any( has_desire( message) for message in messages))

	def test_danger_to_self_positive( self):
		messages = [
		"i am going to kill myself.",
		"tonight i will drink myself to death.",
		"i will be burning myself.",	
		"i totally intent to burn myself!.",	
		"i am about to hurt myself and noone cares!"	
		"next i will cut myself with this razor.",
		"i am seriously thinking about killing myself!",
		"i plan to drown myself in the river.",
		"i wish i was dead!",
		"if only i would die as soon as possible!"
		"sometimes i think it would be best if i would just kill myself.",
		"oh, i wish i could simply kill myself"
		]
		self.failUnless( all( has_danger_to_self( message) for message in messages))

	def test_danger_to_self_negative( self):
		messages = [
		"i am not going to kill myself!",
		"i have cut myself while slicing tomatoes.",
		"soemone told me to go kill myself!",
		"i am going to hurt this monster!",
		"today i will kill megamind once and for all!",
		"i wish all the nazis were dead!"	
		]
		self.failUnless( not any( has_danger_to_self( message) for message in messages))

	def test_request_to_explain_positive( self):
		messages = [
		"what do you even mean?",
		"i do not understand what you mean",
		"sorry, but i do not get your meaning",
		"what are you talking about?",
		"why would you ask that?",
		"what is the purpose of this question?",
		"what are you even asking about?",
		"why?",
		"this question does not even make sense.",
		"sorry?",
		"what are you asking this for?",
		"what do you ask this for?",
		"what is this about?",
		"what exactly to you mean?"
		]
		self.failUnless( all( has_request_to_explain( message) for message in messages))

	def test_request_to_explain_negative( self):
		messages = [
		"this is a mean question.",
		"oh, i see what you are getting at...",
		"do not ask me about the meaning of life!",
		"what about some chill?",
		"that is a great question!",
		"someone else would not understand your question"
		]
		self.failUnless( not any( has_request_to_explain( message) for message in messages))

	def test_hesitation_positive( self):
		messages = [
		"hmm...",
		"ummm",
		"er...",
		"erm",
		":)",
		"let me think...",
		"good question!",
		"pretty good question!",
		"so...",
		"well, actually...",
		"well...",
		"..."
		]
		self.failUnless( all( has_hesitation( message) for message in messages))

	def test_hesitation_negative( self):
		messages = [
		"well, yes",
		"quite well",
		"i think so.",
		"hmm... alright."
		]
		self.failUnless( not any( has_hesitation( message) for message in messages))		

	def test_problem_definition_positive( self):
		messages = [
		"my problem is that i drink too much coffee.",
		"that would be lack of exercise",
		"i definitely have an unhealthy lifestyle",
		"i would say that i kind of behave awkward.",
		"i do not get the recognition i deserve",
		"i never feel satisfied with myself",
		"i just feel so alone.",
		"i would say that i drink way too much alkohol",
		"my problem is that i just can not stand up for myself",
		"always wanting some more is my problem",
		"being stupid, i guess.",
		"it would solve my old problem of feeling inadequate.",
		"the problem that i am bad at math.",
		"it might reduce my fear of intimacy.",
		"i do not have time to deal with this!",
		"the general problem of not having a girlfriend",
		"i have too much stress to deal with anything..."
		]
		self.failUnless( all( has_problem_statement( message) for message in messages))

	def test_problem_definition_negative( self):
		messages = [
		"i do not have an actual problem",
		"my problem is not that i am too kind...",
		"being generous is not my biggest challenge.",
		"yes, there is something...",
		"alkohol!",
		"you are my problem!",
		"my real problem are your stupid questions!",
		"it is complicated...",
		"there are just so many problems in my life!",
		"nothing"
		]
		self.failUnless( not any( has_problem_statement( message) for message in messages))		

	def test_affirmation_positive( self):
		messages = [
		"yes.",
		"sure",
		"certainly...",
		"why not?",
		"quite so!",
		"i think so.",
		"sounds good!",
		"i would say so.",
		"that is true.",
		"hmmm... alright."
		]
		self.failUnless( all( has_affirmation( message) for message in messages))

	def test_affirmation_negative( self):
		messages = [
		"i am not sure...",
		"maybe yes, maybe not",
		"yesterday i heard something different.",
		"whatever!",
		"if you say so..."
		]
		self.failUnless( not any( has_affirmation( message) for message in messages))		

	def test_recognize_timeframe_short_positive( self):
		messages = [
		"the first option sounds better right now.",
		"i would go for the short-term solution.",
		"the quick fix sounds better for me.",
		"i prefer option a"
		]
		self.failUnless( all( prefers_timeframe_short( message) for message in messages)
			and not any( prefers_timeframe_long( message) for message in messages))

	def test_recognize_timeframe_long_positive( self):
		messages = [
		"the sustainable one, of course.",
		"the first option is good, but the second one is better.",
		"i would prefer the long-term one.",
		"the mid-term solution"
		]
		self.failUnless( all( prefers_timeframe_long( message) for message in messages)
			and not any( prefers_timeframe_short( message) for message in messages))			

	def test_option_positive( self):
		messages = [
		"i might go swimming every now and then.",
		"jogging would help to staying in shape.",
		"asking my boss to get a raise",
		"getting a raise",
		"i can drink less alcohol",
		"or go to bed earlier",
		"and meet my friends more often.",
		"to be more open and positive would also be great.",
		"i know i should stick to the things i start.",
		"being a more helpful colleague.",
		"haha, just ignoring it.",
		"doing what i think is best, no matter what everyone says."
		]
		self.failUnless( all( has_option( message) for message in messages))

	def test_options_negative( self):
		messages = [
		"i am not sure...",
		"i can not think of anything.",
		"nothing comes to my mind",
		"nothing really",
		"it is too late for me to fix this.",
		"it does not matter what i do."
		]
		self.failUnless( not any( has_option( message) for message in messages))		

	def test_choose_numerated_item_positive( self):
		messages = [
		"i like the first one",
		"option three sounded good!",
		"i would go for the last one",
		"for me it was option a.",
		"no one but the second",
		"number one",
		"number three was okay, but the others sucked.",	
		]
		self.failUnless( all( has_choice_of_enumerated_item( message) for message in messages))

	def test_choose_numerated_item_negative( self):
		messages = [
		"neither one",
		"none of them was any good",
		"all those options are stupid"
		]
		self.failUnless( not any( has_choice_of_enumerated_item( message) for message in messages))		


	def test_thanks_positive( self):
		messages = [
		"thanks a lot, coachybot!",
		"thank you"
		]
		self.failUnless( all( has_thanks( message) for message in messages))

	def test_thanks_negative( self):
		messages = [
		"alright",
		"hm, sounds good"
		]
		self.failUnless( not any( has_thanks( message) for message in messages))		

	def test_story_positive( self):
		messages = [
		"i was doing my weekly jogging and swimming tour.",
		"ben and i were at a concert",
		"i got my wisdom tooth removed",
		"my neighbor broke his leg, and i had to take him to the hospital",
		"my friend's cat is very ill.",
		"our kitchen stove was on fire",
		"we almost had a car accident!",
		"the police was investigating a murder near our house.",
		"a friend of mine won in the lottery!",
		"i did not meet any fiends this weekend."
		]
		self.failUnless( all( has_story( message) for message in messages))

	def test_story_negative( self):
		messages = [
		"a neighbor fell down the stairs and broke his leg",
		"trump is about to start a nuclear war",
		"it rained like hell for three days",
		"facebook changed their terms and conditions again!",
		"the carrots are growing nicely!",
		"how am i suppoed to sleep with all this noise?"
		]
		self.failUnless( not any( has_story( message) for message in messages))		

	def test_negative_story_positive( self):
		messages = [
		"i was too late for dancing class!",
		"we went to lisas place, but she forgot her keys",
		"i have misplaced my boyfriend's passwort!",
		"me and lisa both failed at our tests.",
		"my neighbor broke his leg, and i had to take him to the hospital",
		"looks like james lost my keys!"
		]
		self.failUnless( all( has_story_negative( message) for message in messages))

	def test_negative_story_negative( self):
		messages = [
		"a neighbor was too late for ice cream.",
		"someone lost his wallet.",
		"looks like james lost bob's keys!",
		"i was doing my weekly jogging and swimming tour.",
		"ben and i were at a concert",
		"i got my wisdom tooth removed",
		"my friend's cat is very ill.",
		"our kitchen stove was on fire",
		"we almost had a car accident!",
		"the police was investigating a murder near our house.",
		"a friend of mine won in the lottery!",
		"i did not meet any fiends this weekend."
		]
		self.failUnless( not any( has_story_negative( message) for message in messages))		

	def test_fear_positive( self):
		messages = [
		"i am afraid of a nuclear war.",
		"i fear that this will not end well for everybody",
		"my fear is that everybody will just look for themselves.",
		"i am very concerned about the environment!",
		"i am frightened of spiders.",
		"the recent developments scare me.",
		"i am absolutely terrified of low-flying airplanes.",
		"i am scared of flocks of birds."
		]
		self.failUnless( all( has_fear( message) for message in messages))

	def test_fear_negative( self):
		messages = [
		"everybody is afraid of a nuclear war",
		"my friends are afraid of a zombie apocalypse.",
		"nobody scares me",
		"i am not afraid of conflict.",
		"some people are afraid that i might run away."
		]
		self.failUnless( not any( has_fear( message) for message in messages))		

	def test_negative_feeling_positive( self):
		messages = [
		"i am so incredibly hungry!",
		"just tired...",
		"i am really exhausted...",
		"so angry!",
		"i hurt my ankle!",
		"i am so lonesome i could die",
		"i feel so powerless...",
		"completely upset!",
		"somehow i am confused",
		"i am totally annoyed by the weather!",
		"i am disappointed in everyone!"
		]
		self.failUnless( all( has_feeling_negative( message) for message in messages))

	def test_negative_feeling_negative( self):
		messages = [
		"i am not hungry at all",
		"i am too excited to go to bed",
		"who made my cat angry?",
		"john is so upset..."
		#"i love angry birds!"
		]
		self.failUnless( not any( has_feeling_negative( message) for message in messages))		

	def test_dislike_positive( self):
		messages = [
		"i hate hyenas!",
		"i just can not stand peanuts",
		"i totally dislike ducks",
		"i detest the taste of snails!",
		"the spice girls are getting on my nerves.",
		"i have had enough of justin bieber",
		"mice are creeping me out!"
		]
		self.failUnless( all( has_dislike( message) for message in messages))

	def test_dislike_negative( self):
		messages = [
		"haters hate potaters",
		"i am getting on everyones' nerves",
		"john dislikes me",
		"mice are creepy!"
		"some people dislike cherries, but i ilke them."
		]
		self.failUnless( not any( has_dislike( message) for message in messages))		

	# Currently unused

	# def test_negative_judgement_positive( self):
	# 	messages = [
	# 	"the weather is so horrible.",
	# 	"all my teachers are stupid...",
	# 	"my neighbor is an idiot",
	# 	"these construction workers are so annoying...",
	# 	"sentiment analysis is totally useless..."
	# 	]
	# 	self.failUnless( all( has_judgement_negative( message) for message in messages))

	# def test_negative_judgement_negative( self):
	# 	messages = [
	# 	"the weather is so cold...",
	# 	"all my teachers are married.",
	# 	"all our neighbor are pet holders.",
	# 	"these construction workers are working hard.",
	# 	"sentiment analysis is seldom useful."
	# 	]
	# 	self.failUnless( not any( has_judgement_negative( message) for message in messages))		

# ===========================================================================================

if __name__ == '__main__':
    unittest.main()
