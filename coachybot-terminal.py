#from time import sleep, tzname

from datetime import datetime

from node_objects import *


epoch = datetime.utcfromtimestamp(0)
def epoch_timestamp(dt):
    return (dt - epoch).total_seconds() * 1000.0

def main():

    user = {
        "timezone"         : "Europe/Berlin",   # TODO: Use timezone as offset from UTC        
        "firstname"        : "User" ,           # TODO: Use getpass(?) to access actual username
        "node_current"     : "Welcome",
        "message_first"    : epoch_timestamp(datetime.now())/1000,
        "message_current"  : epoch_timestamp(datetime.now())/1000
    }

    node_main = Welcome("", user, verbose=False)
    answer    = node_main.answer
    next_node = node_main.next_node
    user      = node_main.user

    for line in answer:
        print "{:12}: ".format("Coachybot") + line

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
        next_node = node_main.next_node
        user      = node_main.user

        for line in answer:
            print "{:12}: ".format("Coachybot") + line

if __name__ == "__main__":
    main()