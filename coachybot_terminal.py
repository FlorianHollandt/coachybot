from time import sleep
import random

from datetime import datetime

from node_objects import *


epoch = datetime.utcfromtimestamp(0)
def epoch_timestamp(dt):
    return (dt - epoch).total_seconds() * 1000.0

typing_ms_per_character_min = 25
typing_ms_per_character_max = 40      

def main( username="User"):

    user = {
        "timezone"         : 2,
        "firstname"        : username,
        "node_current"     : "Welcome",
        "message_first"    : epoch_timestamp(datetime.now())/1000,
        "message_current"  : epoch_timestamp(datetime.now())/1000
    }

    node_main = Welcome("", user, verbose=False)
    answer    = node_main.answer
    next_node = node_main.node_next
    user      = node_main.user

    for line in answer:
        type_time = random.randint( typing_ms_per_character_min, typing_ms_per_character_max)*len(line)
        sleep( type_time/1000. )        
        print "{:12}: ".format("Coachybot") + line
        sleep( random.randint( 450, 550)/1000. )

    while True:    
        message = raw_input("{:12}: ".format(user["firstname"]))
        system_time = epoch_timestamp(datetime.now())/1000
     
        if message in ["quit", "exit", "q"]:
            break

        user.update({
            "message_current"     : system_time
            })
     
        node_main = eval(user["node_current"])(message, user, verbose=False)
        answer    = node_main.answer
        next_node = node_main.node_next
        user      = node_main.user

        for line in answer:
            type_time = random.randint( typing_ms_per_character_min, typing_ms_per_character_max)*len(line)
            sleep( type_time/1000. )
            print "{:12}: ".format("Coachybot") + line
            sleep( random.randint( 450, 550)/1000. )

if __name__ == "__main__":
    main()