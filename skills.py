import re
from regex import sub as sub2

from datetime import datetime
from pytz import timezone

from ngrams import corrections, Pw

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
vader = SentimentIntensityAnalyzer()

firstnames = nltk.corpus.names

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

def capitalize_sentence(sentence):
    sentence = sentence[:1].upper() + sentence[1:]
    sentence = re.sub(r"(^|\W)i($|\W)",r"\1I\2",sentence)

    names = extract_named_entities(sentence.title())
    for name in names:
        sentence = re.sub(name.lower(),name,sentence)

    for token in nltk.tokenize.word_tokenize(sentence)[1:]:
            if re.match(r"[A-Z]\w*",token):
                if Pw(token.lower())>1e-06 and token not in firstnames.words():
                    sentence = re.sub(token,token.lower(),sentence)

    return sentence

def capitalize_fragment(sentence):
    sentence = re.sub(r"(^|\W)i($|\W)",r"\1I\2",sentence)

    names = extract_named_entities(sentence.title())
    for name in names:
        sentence = re.sub(name.lower(),name,sentence)

    for token in nltk.tokenize.word_tokenize(sentence):
        if re.match(r"[A-Z]\w*",token):
            if Pw(token.lower())>1e-06 and token not in firstnames.words():
                sentence = re.sub(token,token.lower(),sentence)

    return sentence



  #####                                #    ######                
 #     #  ####   ####  #####          #     #     #   ##   #####  
 #       #    # #    # #    #        #      #     #  #  #  #    # 
 #  #### #    # #    # #    #       #       ######  #    # #    # 
 #     # #    # #    # #    #      #        #     # ###### #    # 
 #     # #    # #    # #    #     #         #     # #    # #    # 
  #####   ####   ####  #####     #          ######  #    # #####  
                                                                  

intensifiers = "|".join([
    r"(pretty( much)?",
    r"quite",
    r"very",
    r"absolutely",
    r"total?ly",
    r"real?ly",
    r"somewhat",
    r"kind of",
    r"perfectly",
    r"positively",
    r"definitely",
    r"completely",
    r"propably",
    r"just",
    r"rather",
    r"almost",
    r"entirely",
    r"fully",
    r"highly",
    r"a bit)"
    ])   

goods = "|".join([
    r"(good",
    r"better",
    r"best",
    r"finer?",
    r"nicer?",
    r"lovel(y|ier)",
    r"great(er)?",
    r"amazing",
    r"super",
    r"smashing",
    r"fantastic",
    r"stunning",
    r"groovy",
    r"wonderful?l",
    r"superb",
    r"marvel?lous",
    r"neat",
    r"terrific",
    r"swell",
    r"dandy",
    r"tremendous",
    r"excellent",
    r"dope",
    r"well",
    r"elat(ed|ing)",
    r"enthusiastic",
    r"looking forward to",
    r"engag(ed|ing)",
    r"thrill(ed|ing)",
    r"excit(ed|ing)",
    r"happ(y|ier)",
    r"joyful",
    r"joyous",
    r"delight(ed|ing)",
    r"curious",
    r"eager",
    r"ok",
    r"alright)"
    ])                                                                 

bads = "|".join([
    r"(bad",
    r"terrible",
    r"awful",
    r"mad",
    r"horrible",
    r"horrid",
    r"sad",
    r"blue",
    r"down",
    r"unhappy",
    r"unwell",
    r"miserable",
    r"dissatisfied",
    r"unsatisfied",
    r"sick",
    r"ill",
    r"tired",
    r"jealous",
    r"envious",
    r"afraid",
    r"scared",
    r"converned",
    r"worried",
    r"uneasy",
    r"so-so",
    r"medium",
    r"negative",
    r"troubled)"
    ])      

def is_good(sentence):
    if(
        (
            re.search(goods,sentence)
            and not has_negation(sentence)
            )or(
            re.search(bads,sentence)
            and has_negation(sentence)            
            )
        ):
        return True
    else:
        return False

def is_bad(sentence):
    if(
        (
            re.search(bads,sentence)
            and not has_negation(sentence)
            )or(
            re.search(goods,sentence)
            and has_negation(sentence)            
            )
        ):
        return True
    else:
        return False


                                                                         


 ######                                            
 #     # #####   ####  #####  #      ###### #    # 
 #     # #    # #    # #    # #      #      ##  ## 
 ######  #    # #    # #####  #      #####  # ## # 
 #       #####  #    # #    # #      #      #    # 
 #       #   #  #    # #    # #      #      #    #
 #       #    #  ####  #####  ###### ###### #    # 
                   

problem_grammar = nltk.CFG.fromstring(r"""
  problem -> subject VP | subject modifier VP
  VP -> verb_group
  VP -> verb_group object_clause
  VP -> verb_group quantifier_j object_clause
  VP -> verb_group quantifier_r 
  VP -> verb_group modifier_r quantifier_r
  PP -> P object
  verb_group -> verb_simple 
  verb_group -> moderator verb_simple
  verb_group -> verb_aux verb_gerund
  verb_group -> verb_aux modifier verb_gerund
  verb_group -> verb_aux moderator verb_gerund
  verb_group -> verb_aux moderator modifier verb_gerund
  verb_group -> verb_aux verb_simple
  verb_group -> verb_aux modifier verb_simple
  verb_group -> verb_aux moderator verb_simple
  verb_group -> verb_aux moderator modifier verb_simple  
  verb_group -> verb_aux "to" verb_simple
  verb_group -> "do" modifier verb_aux "to" verb_simple
  verb_group -> verb_aux
  verb_simple -> "drink" 
  verb_gerund -> "drinking"
  verb_aux -> "have" verb_pastprog
  verb_aux -> "have" modifier verb_pastprog
  verb_aux -> "am" | "do" | "have" 
  verb_aux -> "use" | "fail" | "can" | "want" | "get"
  verb_pastprog -> "been" | "done"
  subject ->  "i"
  object_simple ->  "milk" 
  object_np -> determiner object_simple
  object_clause -> object_simple | object_np 
  object_clause -> comparison_base object_simple "than" comparison
  object_clause -> comparison_base preposition object_np "than" comparison  
  object_clause -> quantifier_j object_simple
  object_clause -> modifier_r quantifier_j object_simple
  object_clause -> quantifier_j preposition object_np
  object_clause -> modifier_r quantifier_j preposition object_np  
  determiner -> "a" | "an" | "the" | "this" | "these" | "those" | "that"
  determiner ->  "my" | "our" | "his" | "her" | "its" | "our" | "their"
  preposition -> "of" | "from" 
  modifier -> negation | temporal | negation temporal
  modifier_r -> "much" | "way" | "far" | "by" "far" | "a" "lot" | "a" "bit"
  negation -> "no" | "not" | "never"
  temporal -> "always" | "sometimes" | "often"
  quantifier_j -> "a" "lot" "of" | "a" "lot"| "enough"
  quantifier_j -> "too" "much" | "too" "many"
  quantifier_j -> "too" "few" | "too" "little" 
  quantifier_r -> "too" adverb | "too" "little" | "too" "much" | 
  quantifier_r -> comparison_base adverb "than" comparison
  quantifier_r -> comparison_base "than" comparison 
  adverb -> "seldom" | "often" 
  comparison -> "i" "should"
  comparison_base -> "more" | "less" | modifier_r "more" | modifier_r "less"
  moderator -> "kind" "of" | "somehow"
  """)

problem_parser = nltk.RecursiveDescentParser( problem_grammar)

def matches_problem_grammar(sentence):
    sentence = re.sub( r"(\.|\,|\!|\?|\;|\:)", "", sentence)
    return False
    # work in progress

def extract_defined_problem( sentence):
    return sentence 
    # work in progress     

problems = "|".join([
    "(problems?",
    "issues?",
    "topics?",
    "somethings?",
    "itch(es)?",
    "irritations?",
    "troubles?",
    "challenges?",
    "topics?",
    "fears?",
    "pains?)"
    ])

problem_keywords = "|".join([
    "(too much",
    "too many",
    "too often",
    "too little",
    "too few",
    "too seldom",
    "not get",
    "being",
    "lack of",
    "need",
    "satisf",
    "unhealthy",
    "stress",
    "pressure",
    "struggle",
    "barely"
    "hardly",
    "pain",
    "alone",
    "awkward",
    "deserve",
    "more (\w+ )than",
    "less (\w+ )than",
    "survive",
    "enough)"
    ])

problem_patterns = [
r".*(my|the) (\w|\s|\-|\,)?" \
    + problems \
    + r" (is|are|would be|might be)"\
    + "(?! not)( that( i))? ([^\.\!\?$]+)",
r".* (is|are|would be|might be)(?! not) "\
    + "(my|the|an?|one of my) (\w|\s|\-|\,)?" \
    + problems \
    + r"( for me)?(\,|\.|\-|\!|\?|$)",
r"(it (would|might|could|will)"\
    + "(( \w+)?( allow| enable| empower) me to)?"\
    + "( (solve|reduce|improve|increase)) )?"\
    + "(my|the|an?|one of my)( \w+)? "\
    + problems\
    + "\,? (of|that|the|in|not)"
    ]

problem_antipatterns = [
r".*(my|the) (\w|\s|\-|\,)*" \
    + problems \
    + r" (is|are|would be|might be)( that( i))? (not|never) ([^\.\!\?$]+)",
r".* (is|are|would be|might be) (not|never) (my|the|an?|one of my) (\w|\s|\-|\,)*" \
    + problems \
    + r"( for me)?(\,|\.|\-|\!|\?|$)"
    ]    

def has_problem_statement( sentence):
    if(
        any( re.search( antipattern, sentence) for antipattern in problem_antipatterns)
        ):
        return False
    elif(
        (
            any( re.search( pattern, sentence) for pattern in problem_patterns)
            or re.search( problem_keywords, sentence)
        )
        and not re.search( r"you", sentence)
        ):
        return True
    else:
        return False

                                             


 #     #                                                    
 #     # ######  ####  # #####   ##   ##### #  ####  #    # 
 #     # #      #      #   #    #  #    #   # #    # ##   # 
 ####### #####   ####  #   #   #    #   #   # #    # # #  # 
 #     # #           # #   #   ######   #   # #    # #  # # 
 #     # #      #    # #   #   #    #   #   # #    # #   ## 
 #     # ######  ####  #   #   #    #   #   #  ####  #    # 
                                                            

def has_hesitation( sentence):
    if(
        re.search( r"^(\W)*(u+m+|e+r+|h+m+|so+|well)?(\W)*"
            r"(actually|"
            r"((" + intensifiers + r" )?" + goods + r") question|"
            r"let me think)?"
            r"(\W)*$", sentence)
        ):
        return True
    else:
        return False                                                            

 ######                                
 #     # ######  ####  # #####  ###### 
 #     # #      #      # #    # #      
 #     # #####   ####  # #    # #####  
 #     # #           # # #####  #      
 #     # #      #    # # #   #  #      
 ######  ######  ####  # #    # ###### 
                                       

desires = "|".join([
    r"(i (\w+ )?wish",
    r"if only",
    r"my (\w+ )?goal is (that|for|to|when|.w+ing)",
    r"i (\w+ )?hope(?! for)",
    r"it would (\w+ )?be (\w+ )?"+goods +r" (if|when))",
    ])

def has_desire(sentence):
    desire_match = re.search( desires + r"(\s|\.|\,)(?!you)", sentence)
    if desire_match:
        if not has_negation( desire_match.group(0)):
            return True
    else:
        return False



 ######                                                         #####                       
 #     #   ##   #    #  ####  ###### #####     #####  ####     #     # ###### #      ###### 
 #     #  #  #  ##   # #    # #      #    #      #   #    #    #       #      #      #      
 #     # #    # # #  # #      #####  #    #      #   #    #     #####  #####  #      #####  
 #     # ###### #  # # #  ### #      #####       #   #    #          # #      #      #      
 #     # #    # #   ## #    # #      #   #       #   #    #    #     # #      #      #      
 ######  #    # #    #  ####  ###### #    #      #    ####      #####  ###### ###### #      
                                                                                            

hurts = "|".join([
    r"(kill",
    r"hang",
    r"cut",
    r"harm",
    r"electrocute",
    r"burn",
    r"to death", 
    r"hurt",   
    r"drown)",
    ])

intentions_self = "|".join([
    r"(i am (\w+ )?going to",
    r"i (\w+ )?will",
    r"i (\w|\s)*plan(ing)? to",
    r"i (\w|\s)*inten(d|t)(ing)? to",    
    r"i (\w|\s)*prepar(e|ing) to",
    r"i (\w+ )?want to",
    r"i (\w|\s)*think(ing)? about",    
    r"i am (\w+ )about to)",
    ])

def has_danger_to_self(sentence):
    intention_match = re.search( intentions_self+r"(.*)", sentence)
    desire_match =  re.search( desires+r"(.*)", sentence)
    if intention_match:
        if(
            not has_negation( intention_match.group(1))
            and re.search( hurts, intention_match.group(len(intention_match.groups())))
            and re.search(  r"\W(me|myself)(\W|$)", intention_match.group(len(intention_match.groups())))
            ):
            return True
        else:
            return False
    elif desire_match:
        if(
            not has_negation( desire_match.group(1))
            and (
                (
                    re.search(  r"\W(dead|die)(\W|$)", desire_match.group(len(desire_match.groups())))
                    and re.search(  r"\W(i)\W", desire_match.group(len(desire_match.groups())))
                    )
                or(
                    re.search( hurts, desire_match.group( len( desire_match.groups())))
                    and re.search(  r"\W(me|myself)(\W|$)", desire_match.group( len( desire_match.groups())))
                    )
                )
            ):
            return True
        else:
            return False
    else:
        return False


       #                                                        
       # #    # #####   ####  ###### #    # ###### #    # ##### 
       # #    # #    # #    # #      ##  ## #      ##   #   #   
       # #    # #    # #      #####  # ## # #####  # #  #   #   
 #     # #    # #    # #  ### #      #    # #      #  # #   #   
 #     # #    # #    # #    # #      #    # #      #   ##   #   
  #####   ####  #####   ####  ###### #    # ###### #    #   #   
                                                                
judgement_grammar = """
        S_and_V: {((((<PRP\$>|<DT>)? (<R.*>|<J.*>)*)? <NN>? (<NNS>|<NN>))|<PRP>) (<VBZ>|<VBP>|<VBD>) <VBN>?}
        Object : {<DT>* (<R.*>|<J.*>|<VBG> )* (<NNS>|<NN>)* (<CC> <DT>* (<R.*>|<J.*>|<VBG> )* (<NNS>|<NN>)*)? <.>}  
        Judgement : {<.*>* <S_and_V> <Object>}
    """
judgement_chunker = nltk.RegexpParser(judgement_grammar)

def is_judgement_positive(sentence):
    return_value = False
    equivalence = False    
    sentence = re.sub(r"(\,)",r"",sentence)
    sentence_pos = nltk.pos_tag(nltk.word_tokenize(sentence))
    tree = judgement_chunker.parse(sentence_pos)
    if unicode("Judgement") in [subtree.label() for subtree in tree.subtrees()]:
        for subtree in tree.subtrees():
            if subtree.label() == unicode("Object"):
                vader_score = vader.polarity_scores("You are " + " ".join([word for (word,tag) in subtree.leaves()]))
            if subtree.label() == unicode("S_and_V"):
                if re.search(r"(is|are|was|were|has been|have been)",sentence):
                    equivalence = True
        if (
            vader_score["pos"] >= max(vader_score["neg"],vader_score["neu"])
            and equivalence
        ):
            return_value = True
    return return_value

def is_judgement_negative(sentence):
    return_value = False
    equivalence = False
    sentence = re.sub(r"(\,)",r"",sentence)    
    sentence_pos = nltk.pos_tag(nltk.word_tokenize(sentence))
    tree = judgement_chunker.parse(sentence_pos)
    if unicode("Judgement") in [subtree.label() for subtree in tree.subtrees()]:
        for subtree in tree.subtrees():
            if subtree.label() == unicode("Object"):
                vader_score = vader.polarity_scores("You are " + " ".join([word for (word,tag) in subtree.leaves()]))
            if subtree.label() == unicode("S_and_V"):
                if re.search(r"(is|are|was|were|has been|have been)",sentence):
                    equivalence = True
        if (
            vader_score["neg"] >= max(vader_score["neu"],vader_score["pos"])
            and equivalence
        ):
            return_value = True
    if re.search(r"(suck|full of .*shit|nothing but .*shit)",sentence):
        return_value = True
    return return_value



  #####                                             
 #     #  ####  #    # ###### #      #  ####  ##### 
 #       #    # ##   # #      #      # #    #   #   
 #       #    # # #  # #####  #      # #        #   
 #       #    # #  # # #      #      # #        #   
 #     # #    # #   ## #      #      # #    #   #   
  #####   ####  #    # #      ###### #  ####    #   
                                                    

conflicts = "|".join([
    r"(trouble",
    r"problem",
    r"conflict",
    r"fight",
    r"disagreement",
    r"struggle",
    r"dispute",
    r"argument",
    r"battle",
    r"quarrel",
    r"dispute",
    r"controvery",
    r"clash",
    r"collision",
    r"(?:^|\s)issue)"
])

def has_conflict(sentence):
    if re.search(conflicts,sentence) and not has_negation(sentence):
        return True
    else:
        return False

 ######                                                    
 #     #   ##   ##### #  ####  #    #   ##   #      ###### 
 #     #  #  #    #   # #    # ##   #  #  #  #      #      
 ######  #    #   #   # #    # # #  # #    # #      #####  
 #   #   ######   #   # #    # #  # # ###### #      #      
 #    #  #    #   #   # #    # #   ## #    # #      #      
 #     # #    #   #   #  ####  #    # #    # ###### ###### 
    
rationale_pattern = re.compile(r"(?:.*)because\W([^\.\,\;\!\?]+)")

def has_rationale(sentence):
    if rationale_pattern.search(sentence):
        return True
    else:
        return False


def reflect_rationale(sentence):
    reason = rationale_pattern.search(sentence).group(1)
    return capitalize_fragment(
        perform_pronoun_reflection(
            reason))


 #     #                                #######                                      
 ##    #   ##   #    # ###### #####     #       #    # ##### # ##### # ######  ####  
 # #   #  #  #  ##  ## #      #    #    #       ##   #   #   #   #   # #      #      
 #  #  # #    # # ## # #####  #    #    #####   # #  #   #   #   #   # #####   ####  
 #   # # ###### #    # #      #    #    #       #  # #   #   #   #   # #           # 
 #    ## #    # #    # #      #    #    #       #   ##   #   #   #   # #      #    # 
 #     # #    # #    # ###### #####     ####### #    #   #   #   #   # ######  ####  
                                                                                     
                                                                
def extract_persons(text):
    target = re.compile(r"(PERSON")#|ORGANIZATION|FACILITY)")
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)
    persons = []
    for subtree in sentt.subtrees(filter=lambda t: target.match(t.label())):
        name = ' '.join([leaf[0] for leaf in subtree.leaves()])
        for i in range(len((persons))):
            if re.search(persons[i],name):
                persons[i] = re.sub(persons[i],name,persons[i])
        if not any(re.search(name,person) for person in persons):
            persons.append(name)            

    return (persons)


def extract_named_entities(text):
    target = re.compile(r"(PERSON|ORGANIZATION|GPE|LOCATION)")
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)
    entities = []
    for subtree in sentt.subtrees(filter=lambda t: target.match(t.label())):
        name = ' '.join([leaf[0] for leaf in subtree.leaves()])
        if name not in entities:
            entities.append(name)            

    return (entities)


 ######                                          
 #     # #####   ####  ##### ######  ####  ##### 
 #     # #    # #    #   #   #      #        #   
 ######  #    # #    #   #   #####   ####    #   
 #       #####  #    #   #   #           #   #   
 #       #   #  #    #   #   #      #    #   #   
 #       #    #  ####    #   ######  ####    #   
                                                 

def has_protest_to_question(sentence):
    if(
        re.search(r"no[^\.\,\;(is)]+you[^\.\,\;]+(busines|concern)",sentence)
        or re.search(r"mind[^\.\,\;(is)]+own[^\.\,\;]+busines",sentence)
        or re.search(r"(never|no)[^\.\,\;(is)]+mind",sentence)
        or re.search(r"no[^\.\,\;]+((talk[^\.\,\;]+about)|discuss)",sentence)        
        ):
        return True
    else:
        return False                                                 


  #####                                                    
 #     # #    # ######  ####  ##### #  ####  #    #  ####  
 #     # #    # #      #        #   # #    # ##   # #      
 #     # #    # #####   ####    #   # #    # # #  #  ####  
 #   # # #    # #           #   #   # #    # #  # #      # 
 #    #  #    # #      #    #   #   # #    # #   ## #    # 
  #### #  ####  ######  ####    #   #  ####  #    #  ####  
                                                           

def has_request_to_explain(sentence):
    if(
        ( # why are you asking this? / why would you want to know this?
            re.search(r"(why|(what.*(for|reason|purpose)))", sentence)
            and
            re.search(r"(ask|know|question|curious|nosy|inquisitive)", sentence)
            )
        or( # in how far is that relevant?
            re.search(r"(why|(how(\w|\s)+(is|be)))", sentence)
            and
            re.search(r"(important|relevant|interesting|fascinating)", sentence)
            )
        or( # what do you mean / i do not get your point?
            re.search(r"(what|((^|\W)i\W).*(not.*(get|understand|follow)))", sentence)
            and(
                re.search(r"(talk|question|this)(\w|\s)+about", sentence)
                or
                re.search(r"you.*(point|mean|ask|question)", sentence)
                )
            )        
        or(
            re.search(r"(question|ask)", sentence)
            and
            re.search(r"(you|this).*(has|make)", sentence)
            and
            re.search(r"no(\w|\s)+(sense)", sentence)
            ) 
        or(
            re.search(r"why\?", sentence)
            )        
        or(
            re.search(r"sorry\?", sentence)
            )             
        ):
        return True
    else:
        return False



  #####                                                   
 #     # #    #   ##   #    # ##### # ##### # ##### #   # 
 #     # #    #  #  #  ##   #   #   #   #   #   #    # #  
 #     # #    # #    # # #  #   #   #   #   #   #     #   
 #   # # #    # ###### #  # #   #   #   #   #   #     #   
 #    #  #    # #    # #   ##   #   #   #   #   #     #   
  #### #  ####  #    # #    #   #   #   #   #   #     #   
                                                          

quantifier_much = "|".join([
    r"(a [^\.\;]*lot",
    r"lots",
    r"enough",
    r"(?:^|\s)sufficient",
    r"great [^\.\;]*deal of",
    r"some",
    r"extensively",
    r"several",
    r"a few",
    r"a [^\.\;]*couple of",
    r"a [^\.\;]*bit of",
    r"several",
    r"multiple",
    r"various",
    r"fold",
    r"numerous",
    r"plent[iy]",
    r"copious",
    r"abundant",
    r"ample",
    r"any",
    r"many",
    r"much)"
    ])   

quantifier_insufficient = "|".join([
    r"(insufficient",
    r"lack of",
    r"lacked",
    r"defici",
    r"(?<!a\s)few",     # match only if not preceded by "a "
    r"(?<!a\s)little",
    r"scant",
    r"miss)"
    ])   

def has_quantifier_much(sentence):
    if re.search(r"not[^\.\;]+" + quantifier_much,sentence):
        return False
    if re.search(quantifier_much,sentence):
        return True
    elif re.search(r"no[^\.\;]+(complain|lack|miss|defici|insufficient)",sentence):
        return True
    else:
        return False

def has_quantifier_insufficient(sentence):
    if re.search(r"no[^\.\;]+" + quantifier_insufficient,sentence):
        return False
    if re.search(quantifier_insufficient,sentence):
        return True        
    elif re.search(r"not[^\.\;]+"+quantifier_much,sentence):
        return True
    else:
        return False

def has_quantifier_excessive(sentence):
    if re.search(r"(too much|overmuch)",sentence):
        return True
    else:
        return False


 #     #                        #    #     #        
  #   #  ######  ####          #     ##    #  ####  
   # #   #      #             #      # #   # #    # 
    #    #####   ####        #       #  #  # #    # 
    #    #           #      #        #   # # #    # 
    #    #      #    #     #         #    ## #    # 
    #    ######  ####     #          #     #  ####  
                                                    
# Maybe intensifiers can be viewed as a subset of affirmations?
affirmations = "|".join([
    r"(yes",
    r"yeah",
    r"aye",
    r"absolutely",
    r"total?ly",
    r"certainly",
    r"probably",
    r"definitely",
    r"maybe",
    r"right",
    r"correct",
    r"true",
    r"possible",
    r"possibly",
    r"sure",
    r"almost",
    r"entirely",
    r"fully",
    r"highly",
    r"ok",
    r"okay",
    r"agree",
    r"alright)"
    ])   

negations_short = "|".join([
    r"(no",
    r"not",
    r"nay",
    r"nope)"
    ])   

negations_pronoun = "|".join([
    r"(never",
    r"no?one",
    r"nobody",
    r"nowhere",
    r"nothing)"
    ])   

negations_adjective = "|".join([
    r"(impossible",
    r"wrong",
    r"false",
    r"bullshit",
    r"incorrect)"
    ])   

negations = r"(("+negations_short+r"(\W|$))|" + negations_pronoun + "|" + negations_adjective + ")"

def has_negation(sentence):
    if re.search( negations_short + r"[^\.\,\;(is)]+" + negations_adjective,sentence):
        return False
    elif re.search( negations,sentence):
        return True
    else:
        return False

def has_affirmation( sentence):
    if(
        re.search( affirmations+r"(\W|$)",sentence) 
        and not has_negation( sentence)
        ):
        return True
    elif(
        re.search( r"why not(\?|\!)", sentence)
        or re.search( intensifiers + r" so(\W|$)", sentence)
        or (
            re.search( r"(\W|^)i (.* )?(think|say|hope) so(\W|$)", sentence)
            and not has_negation(sentence)
            )
        ):
        return True
    else:
        return False


def has_elaboration(sentences):
    text = "".join(sentences)
    for pattern in [goods,bads,intensifiers,affirmations,negations]:
        text=re.sub(pattern,"",text)

    if len(text) > 20:
        return True
    else:
        return False


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

  #####                                             
 #     # #####  ###### ###### ##### # #    #  ####  
 #       #    # #      #        #   # ##   # #    # 
 #  #### #    # #####  #####    #   # # #  # #      
 #     # #####  #      #        #   # #  # # #  ### 
 #     # #   #  #      #        #   # #   ## #    # 
  #####  #    # ###### ######   #   # #    #  ####  
                                                    

def current_greeting(current_hour):
    if not isinstance(current_hour, int):
        return "Hello" 
    elif current_hour < 11:
        return "Good morning"
    elif current_hour >= 18:   
        return "Good evening"
    elif current_hour >= 14 and current_hour < 18:   
        return "Good afternoon"
    else:
        return "Hello" 

def current_daytime(current_hour):
    if not isinstance(current_hour, int):
        return "day" 
    elif current_hour < 11:
        return "morning"
    elif current_hour >= 18:   
        return "evening"
    elif current_hour >= 14 and current_hour < 18:   
        return "afternoon"
    else:
        return "day" 

def previous_daytime(current_hour):
    if not isinstance(current_hour, int):
        return "day" 
    elif current_hour < 10:
        return "night"
    elif current_hour >= 10 and current_hour < 18:   
        return "day so far"
    else:
        return "day" 

def next_daytime(current_hour):
    if not isinstance(current_hour, int):
        return "day" 
    elif current_hour < 5:
        return "night"
    elif current_hour >= 5 or current_hour < 10:
        return "start into the day"
    elif current_hour >= 15 and current_hour < 20:   
        return "evening"
    elif current_hour >= 20:   
        return "night"
    else:
        return "day"         


greeting = r"^(" + "|".join([r"^(oh\,? ",
    r"hey [\w\s-]+\,?",
    r"hey\,? ",
    r"why\, ",
    r"\w+ \w+\, ",
    r"oh [\w\s-]+\,)"
    ]) + "?" + "|".join([
    r"(good morning",
    r"good afternoon",
    r"good evening",
    r"h[ea]llo",
    r"hi",
    r"howdy",
    r"salut",
    r"servus",
    r"ahoi)"
    ]) + r"($|\,| |\.|\!|\;))|(hey there!)"


def is_greeting(sentence):
    if re.search( greeting, sentence):
        return True
    else:
        return False

temporal_general = "|".join([
    r"(today",
    r"yesterday",
    r"right now",
    r"currently",
    r"now",
    r"recently",
    r"previously",
    r"lately",
    r"sometimes",
    r"every now and then)"
    ])

temporal_units = "|".join([
    r"(days?",
    r"weeks?",
    r"weekend",
    r"morning",
    r"evening",
    r"night",
    r"time",
    r"\w+day",
    r"hours?",
    r"january",
    r"february",
    r"march",
    r"april",
    r"mai",
    r"june",
    r"july",
    r"august",
    r"september",
    r"ocotber",
    r"november",
    r"december",
    r"spring",
    r"winter",
    r"summer",
    r"fall",
    r"autumn",
    r"years?)",
])

how_are_you = r"(^|([\,\;\.\!]\s))" + "|".join([
    r"(how are you( doing| feeling)?",
    r"how is it going",   
    r"how do you (do|feel)",        
    r"what is up)"    
]) + r"(\s(this|these|those|lately|recently|today|now|again|right now)\s?)?" + temporal_units + r"?(\,[\s\w]+)?\?"

how_was_your_time = r"(^|([\,\;\.\!]\s))" + "|".join([
    r"(how (is|was|were) your",
    r"how (has|have) your)",
]) + r"\s(last|current|recent|previous)?\s?" + temporal_units + r"\s?(been)?\s?(so far|lately|recently)?(\,[\s\w]+)?\?"

you_had_good_time = r"(?<!(why  |how  |who  |what |when ))" + "|".join([r"(did you have",
    "have you had)"]) + r"\s" + "|".join([
    r"(a",
    r"some",
    r"a few)" ]) + "\s" + intensifiers + r"?\s?" + goods + r"\s" + temporal_units + r"((\s|\,)[\,\s\w]+)?\?"

def is_question_how_are_you(sentence):
    if re.search( how_are_you, sentence):
        return True
    else:
        return False

def is_question_how_was_your_time(sentence):
    if re.search( how_was_your_time, sentence):
        return True
    else:
        return False

def is_question_you_had_good_time(sentence):
    sentence = sentence.replace( "why did", "why  did")
    sentence = sentence.replace( "how did", "how  did")
    sentence = sentence.replace( "who did", "who  did")
    if re.search( you_had_good_time, sentence):
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
    #re.compile(r"^alright\W"), 
    re.compile(r"^anyways?\W"), 
    re.compile(r"^lol\w?\W"), 
    re.compile(r"^wo+w\W"), 
    re.compile(r"^cool[\.\,\!]+"),         
    re.compile(r"^sorry[\.\,\!]+"),         
    #re.compile(r"^great[\.\,\!]+"),         
    re.compile(r"final?ly"), 
    re.compile(r"honestly"),
    re.compile(r"actually"),
    re.compile(r"quite"),    
    re.compile(r"really"),    
    re.compile(r"literal?ly"),    
    re.compile(r"certainly"),    
    re.compile(r"in fact"),    
    re.compile(r"somehow"),        
    re.compile(r"basical?ly")
    #re.compile(r"just")
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
        (r"1", "one"),    
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


 # #    # ##### #####   ####  #####  #    #  ####  ##### #  ####  #    # 
 # ##   #   #   #    # #    # #    # #    # #    #   #   # #    # ##   # 
 # # #  #   #   #    # #    # #    # #    # #        #   # #    # # #  # 
 # #  # #   #   #####  #    # #    # #    # #        #   # #    # #  # # 
 # #   ##   #   #   #  #    # #    # #    # #    #   #   # #    # #   ## 
 # #    #   #   #    #  ####  #####   ####   ####    #   #  ####  #    # 

# simple_sentence_grammar = """
#         noun_phrase: {((((<PRP\$>|<DT>)? (<R.*>|<J.*>)*)? <NN>? (<NNS>|<NN>))|<PRP>)}
#         subject_and_verb : {<noun_phrase> (<R.*> )*(<VBZ>|<VBP>|<VBD>)}  
#     """
# simple_sentence_chunker = nltk.RegexpParser(simple_sentence_grammar)                                                                         

# introductions = "|".join([
#     "(say",
#     "guess",
#     "think)"
#     ]) + r"(\,? that)?"

# def has_introduction( sentence):
#     return_value = False
#     intro_match = re.search( r"(.*) " + introductions + r" (.*)", sentence)
#     if intro_match:
#         if(
#             re.search( r"i ", intro_match.group(1))
#             and not re.search( r"not ", intro_match.group(1))
#             ):
#             return_value = True
#     return return_value

