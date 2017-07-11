import re
from regex import sub as sub2

from datetime import datetime
from pytz import timezone

from ngrams import corrections
import nltk

# ===========================================================================================


 #     #                                                                          
 ##    #  ####  #####  #    #   ##   #      # ######   ##   ##### #  ####  #    # 
 # #   # #    # #    # ##  ##  #  #  #      #     #   #  #    #   # #    # ##   # 
 #  #  # #    # #    # # ## # #    # #      #    #   #    #   #   # #    # # #  # 
 #   # # #    # #####  #    # ###### #      #   #    ######   #   # #    # #  # # 
 #    ## #    # #   #  #    # #    # #      #  #     #    #   #   # #    # #   ## 
 #     #  ####  #    # #    # #    # ###### # ###### #    #   #   #  ####  #    # 
                                                                                  

sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

def preprocess_message(statement):
    sentences = sentence_tokenizer.tokenize(statement)
    return [
        cleanup_sentence(
            remove_fluff(
                    corrections(
                            expand_contractions(
                                    sentence.lower()
                                    ))))
        for sentence 
        in sentences
        ]

def stemmer(word,pos):
    if pos=="NOUN" and  word[-1]=="s":
        return word[:-1]
    elif pos=="VERB" and  word[-1]=="s":
        return word[:-1]
    elif pos=="VERB" and  word[-2:]=="ed" and word[-3]!="e":
        return word[:-2]+"ing"
    else:
        return word

 ######                                                           
 #     # ###### ###### #      ######  ####  ##### #  ####  #    # 
 #     # #      #      #      #      #    #   #   # #    # ##   # 
 ######  #####  #####  #      #####  #        #   # #    # # #  # 
 #   #   #      #      #      #      #        #   # #    # #  # # 
 #    #  #      #      #      #      #    #   #   # #    # #   ## 
 #     # ###### #      ###### ######  ####    #   #  ####  #    # 
                                                                  

temporal = "|".join([
    r"(today",
    r"right now",
    r"currently",
    r"now",
    r"recently",
    r"previously",
    r"lately",
    r"these days",
    r"this \w+",
    r"sometimes",
    r"every now and then)"
    ])

statements_about_self = [
    re.compile(r"^" + temporal + r"?\W*i am "),
    re.compile(r"^" + temporal + r"?\W*i was "),
    re.compile(r"^" + temporal + r"?\W*i will "),
    re.compile(r"^" + temporal + r"?\W*i have "),
    re.compile(r"^" + temporal + r"?\W*i had "),
    re.compile(r"^" + temporal + r"?\W*i got "),
    re.compile(r"^" + temporal + r"?\W*i do "),
    re.compile(r"^" + temporal + r"?\W*i did "),
    re.compile(r"^" + temporal + r"?\W*i can "),
    re.compile(r"^" + temporal + r"?\W*i could "),
    re.compile(r"^" + temporal + r"?\W*i feel "),
    re.compile(r"^" + temporal + r"?\W*i felt "),
    re.compile(r"^" + temporal + r"?\W*i hope "),
    re.compile(r"^" + temporal + r"?\W*i hoped "),
    re.compile(r"^" + temporal + r"?\W*i wish "),
    re.compile(r"^" + temporal + r"?\W*i wished ")     
]

def is_statement_about_self(sentence, statements_about_self=statements_about_self):
    if any(statement.search(sentence) for statement in statements_about_self):
        return True
    else:
        return False

pronoun_reflections = [
    (r"(^|\W)i(\W|$)", r"\1YOU\2"),
    (r"(^|\W)me(\W|$)", r"\1YOU\2"),
    (r"(^|\W)mine(\W|$)", r"\1YOURS\2"),
    (r"(^|\W)my(\W|$)", r"\1YOUR\2"),
    (r"(^|\W)myself(\W|$)", r"\1MYSELF\2"),    
    (r"(^|\W)you(\W|$)", r"\1I\2"),
    (r"(^|\W)your(\W|$)", r"\1MY\2"),
    (r"(^|\W)yours(\W|$)", r"\1MINE\2")
    ]

def perform_open_reflection(statement):
    reflections_open = [
        (r"^" + temporal + r"?(\W?)i am\W([^\.\,\!]+)(?:.*)", r'are you |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i was\W([^\.\,\!]+)(?:.*)", r'were you |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i will\W([^\.\,\!]+)(?:.*)", r'will you |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i have got\W([^\.\,\!]+)(?:.*)", r'do you have |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i have had\W([^\.\,\!]+)(?:.*)", r'did you have |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i have\W([^\.\,\!]+)(?:.*)", r'have you |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i had\W([^\.\,\!]+)(?:.*)", r'did you have |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i got\W([^\.\,\!]+)(?:.*)", r'did you get |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i do\W([^\.\,\!]+)(?:.*)", r'do you |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i did\W([^\.\,\!]+)(?:.*)", r'did you |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i can\W([^\.\,\!]+)(?:.*)", r'can you |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i could\W([^\.\,\!]+)(?:.*)", r'could you |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i feel\W([^\.\,\!]+)(?:.*)", r'do you feel |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i felt\W([^\.\,\!]+)(?:.*)", r'did you feel |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i hope\W([^\.\,\!]+)(?:.*)", r'do you hope |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i hoped\W([^\.\,\!]+)(?:.*)", r'did you hope |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i wish\W([^\.\,\!]+)(?:.*)", r'do you wish |||\3\2\1'),
        (r"^" + temporal + r"?(\W?)i wished\W([^\.\,\!]+)(?:.*)", r'did you wish |||\3\2\1')
    ]
    for (before, after) in reflections_open:
        if re.search(before,statement):
            reflection = sub2(before,after,statement)
            break
    introduction,content = reflection.split("|||")
    for (before, after) in pronoun_reflections:
        content = re.sub(before, after, content) 
    return introduction + content.lower()

  #####                                             
 #     # #####  ###### ###### ##### # #    #  ####  
 #       #    # #      #        #   # ##   # #    # 
 #  #### #    # #####  #####    #   # # #  # #      
 #     # #####  #      #        #   # #  # # #  ### 
 #     # #   #  #      #        #   # #   ## #    # 
  #####  #    # ###### ######   #   # #    #  ####  
                                                    

def current_greeting(current_hour):
    if current_hour < 11:
        return "Good morning"
    elif current_hour >= 18:   
        return "Good evening"
    elif current_hour >= 14 and current_hour < 18:   
        return "Good afternoon"
    else:
        return "Hello" 

def current_daytime(current_hour):
    if current_hour < 11:
        return "morning"
    elif current_hour >= 18:   
        return "evening"
    elif current_hour >= 14 and current_hour < 18:   
        return "afternoon"
    else:
        return "day" 

def previous_daytime(current_hour):
    if current_hour < 10:
        return "night"
    elif current_hour >= 10 and current_hour < 18:   
        return "day so far"
    else:
        return "day" 

def next_daytime(current_hour):
    if current_hour < 5:
        return "night"
    elif current_hour >= 5 or current_hour < 10:
        return "start into the day"
    elif current_hour >= 15 and current_hour < 20:   
        return "evening"
    elif current_hour >= 20:   
        return "night"
    else:
        return "day"         

greetings = [
    re.compile(r'^good morning'),
    re.compile(r'^good afternoon'),
    re.compile(r'^good evening'),
    re.compile(r'^hello'),
    re.compile(r'^hi\W*'),
    re.compile(r'^howdy'),
    re.compile(r'^hey\W+((there)|((\s|\w)*coachy)|((\s|\w)*bot))'),
    re.compile(r'^hey\s*[youm]*\s+\w+[\.\!]+')   
]

def is_greeting(sentence, greetings=greetings):
    if any(greeting.search(sentence) for greeting in greetings):
        return True
    else:
        return False

how_are_yous = [
    re.compile('(?:^|,|;|-\s*)how are you[\s\,]?\w*'),
    re.compile('[^,;]how is it going[\s\,]?\w*'),    
    re.compile('[^,;]what is up[\s\,]?\w*')    
]

def is_how_are_you(sentence, how_are_yous=how_are_yous):
    if any(how_are_you.match(sentence) for how_are_you in how_are_yous):
        return True
    else:
        return False


 #######                             
 #       #      #    # ###### ###### 
 #       #      #    # #      #      
 #####   #      #    # #####  #####  
 #       #      #    # #      #      
 #       #      #    # #      #      
 #       ######  ####  #      #      

fluffs = [
    #re.compile(r"^[\s\.\,\;\-\!\?]"), 
    re.compile(r"(?:^|\W)(?::|;|=|B|8)(?:-|\^)?(?:\)|\(|D|P|\||\[|\]|>|\$|3)+(?:$|\W)"), 
    re.compile(r"^well\W"), 
    re.compile(r"^so\W"), 
    re.compile(r"^alright\W"), 
    re.compile(r"^anyways?\W"), 
    re.compile(r"^lol\w?\W"), 
    re.compile(r"^wo+w\W"), 
    re.compile(r"^cool[\.\,\!]+"),         
    re.compile(r"^sorry[\.\,\!]+"),         
    re.compile(r"^great[\.\,\!]+"),         
    re.compile(r"finally"), 
    re.compile(r"honestly"),
    re.compile(r"actually"),
    re.compile(r"quite"),    
    re.compile(r"really"),    
    re.compile(r"literally"),    
    re.compile(r"certainly"),    
    re.compile(r"in fact"),
    re.compile(r"just")
]

def contains_fluff(text, fluffs=fluffs):
    "Remove words that don't contribute to the meaning of a statement." 
    # Create a regular expression  from the fluff list
    if any(fluff.search(text) for fluff in fluffs):
        return True
    else:
        return False  

def remove_fluff(text, fluffs=fluffs):
    "Remove words that don't contribute to the meaning of a statement." 
    while any(fluff.search(text) for fluff in fluffs):
        for fluff in fluffs:
            text = fluff.sub('', text)
    return text   

def cleanup_sentence(text):
    corrections = [
        (r"^\W", r""), 
        (r"\s$", r""),          
        (r"\;" , ","),
        (r"\s{2,}" , " "),
        (r"\.{2,}" , " "),
        (r"[\!\?]+\?[\!\?]*" , "?"),
        (r"[\!\?]*\?[\!\?]+" , "?")        
    ]
    while any(re.search(before,text) for (before,after) in corrections):
        for (before, after) in corrections:
            text = re.sub(before, after, text)
    return text

  #####                                                                        
 #     #  ####  #    # ##### #####    ##    ####  ##### #  ####  #    #  ####  
 #       #    # ##   #   #   #    #  #  #  #    #   #   # #    # ##   # #      
 #       #    # # #  #   #   #    # #    # #        #   # #    # # #  #  ####  
 #       #    # #  # #   #   #####  ###### #        #   # #    # #  # #      # 
 #     # #    # #   ##   #   #   #  #    # #    #   #   # #    # #   ## #    # 
  #####   ####  #    #   #   #    # #    #  ####    #   #  ####  #    #  ####  
                                                                               

def expand_contractions(text):
    "Replace contractions of pronoun and auxiliary verb with their expanded versions." 
    contractions = [
        (r"ain't", "is not"),
        (r"aren't", "are not"),
        (r"can't", "can not"),
        (r"cant", "can not"),
        (r"can't've", "can not have"),
        (r"'cause", "because"),
        (r"could've", "could have"),
        (r"couldn't", "could not"),
        (r"couldn't've", "could not have"),
        (r"didn't", "did not"),
        (r"didnt", "did not"),
        (r"doesn't", "does not"),
        (r"doesnt", "does not"),
        (r"don't", "do not"),
        (r"dont", "do not"),
        (r"gonna", "going to"),
        (r"hadn't", "had not"),
        (r"hadn't've", "had not have"),
        (r"hasn't", "has not"),
        (r"hasnt", "has not"),
        (r"haven't", "have not"),
        (r"havent", "have not"),
        (r"he'd", "he would"),
        (r"he'd've", "he would have"),
        (r"he'll", "he will"),
        (r"he'll've", "he will have"),
        (r"he's", "he is"),
        (r"hes", "he is"),
        (r"here's", "here is"),
        (r"heres", "here is"),
        (r"how'd", "how did"),
        (r"how'd'y", "how do you"),
        (r"how'll", "how will"),
        (r"how's", "how is"),
        (r"hows", "how is"),
        (r"how're", "how are"),
        (r"howre", "how are"),
        (r"i'd", "i would"),
        (r"i'd've", "i would have"),
        (r"i'll", "i will"),
        (r"i'll've", "i will have"),
        (r"i'm", "i am"),
        (r"im", "i am"),
        (r"ima", "i am going to"),        
        (r"i've", "i have"),     
        (r"ive", "i have"),     
        (r"isn't", "is not"),
        (r"isnt", "is not"),
        (r"it'd", "it would"),
        (r"it'd've", "it would have"),
        (r"it'll", "it will"),
        (r"it'll've", "it will have"),
        (r"it's", "it is"),
        (r"let's", "let us"),
        (r"lets", "let us"),
        (r"ma'am", "madam"),
        (r"mayn't", "may not"),
        (r"might've", "might have"),
        (r"mightn't", "might not"),
        (r"mightn't've", "might not have"),
        (r"must've", "must have"),
        (r"mustn't", "must not"),
        (r"mustn't've", "must not have"),
        (r"needn't", "need not"),
        (r"needn't've", "need not have"),
        (r"o'clock", "of the clock"),
        (r"oughtn't", "ought not"),
        (r"oughtn't've", "ought not have"),
        (r"shan't", "shall not"),
        (r"sha'n't", "shall not"),
        (r"shan't've", "shall not have"),
        (r"she'd", "she would"),
        (r"she'd've", "she would have"),
        (r"she'll", "she will"),
        (r"she'll've", "she will have"),
        (r"she's", "she is"),
        (r"shes", "she is"),
        (r"should've", "should have"),
        (r"shouldn't", "should not"),
        (r"shouldnt", "should not"),
        (r"shouldn't've", "should not have"),
        (r"so've", "so have"),
        (r"so's", "so is"),
        (r"that'd", "that would"),
        (r"that'd've", "that would have"),
        (r"that's", "that is"),
        (r"thats", "that is"),
        (r"there'd", "there would"),
        (r"there'd've", "there would have"),
        (r"there's", "there is"),
        (r"theres", "there is"),
        (r"they'd", "they would"),
        (r"they'd've", "they would have"),
        (r"they'll", "they will"),
        (r"they'll've", "they will have"),
        (r"they're", "they are"),
        (r"theyre", "they are"),
        (r"they've", "they have"),
        (r"theyve", "they have"),
        (r"to've", "to have"),
        (r"wanna", "want to"),
        (r"wasn't", "was not"),
        (r"wasnt", "was not"),
        (r"we'd", "we would"),
        (r"we'd've", "we would have"),
        (r"we'll", "we will"),
        (r"we'll've", "we will have"),
        (r"we're", "we are"),
        (r"we've", "we have"),
        (r"weve", "we have"),
        (r"weren't", "were not"),
        (r"what'll", "what will"),
        (r"what'll've", "what will have"),
        (r"what're", "what are"),
        (r"what's", "what is"),
        (r"whats", "what is"),
        (r"what've", "what have"),
        (r"when's", "when is"),
        (r"when've", "when have"),
        (r"where'd", "where did"),
        (r"where's", "where is"),
        (r"wheres", "where is"),
        (r"where've", "where have"),
        (r"who'll", "who will"),
        (r"who'll've", "who will have"),
        (r"who's", "who is"),
        (r"whos", "who is"),
        (r"who've", "who have"),
        (r"why's", "why is"),
        (r"why've", "why have"),
        (r"will've", "will have"),
        (r"won't", "will not"),
        (r"wont", "will not"),
        (r"won't've", "will not have"),
        (r"would've", "would have"),
        (r"wouldn't", "would not"),
        (r"wouldn't've", "would not have"),
        (r"ya", "you"),
        (r"y'all", "you all"),
        (r"y'all'd", "you all would"),
        (r"y'all'd've", "you all would have"),
        (r"y'all're", "you all are"),
        (r"y'all've", "you all have"),
        (r"you'd", "you would"),
        (r"youd", "you would"),
        (r"you'd've", "you would have"),
        (r"you'll", "you will"),
        (r"youll", "you will"),
        (r"you'll've", "you will have"),
        (r"you're", "you are"),
        (r"youre", "you are"),
        (r"you've", "you have"),
        (r"youve", "you have")
    ]
    # Create a regular expression  from the dictionary keys
    for (before, after) in contractions:
        text = re.sub(r"(^|\W)"+before+r"($|\W)", r"\1"+after+r"\2", text)
    return text


