import os 
import sys
import json

from flask import Flask, request
import requests


# http://patorjk.com/software/taag/#p=display&f=Banner&t=Connecting
# ===========================================================================================

page_access_token = os.environ['FACEBOOK_PAGE_ACCESS_TOKEN']
verify_token      = os.environ['FACEBOOK_VERIFY_TOKEN']

app = Flask(__name__)

# ===========================================================================================

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == verify_token:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()

    print "Recieved data! :)"

    if data["object"] == "page":

        print "Uh! Looks like a page object..."

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    print "Someone sent us a message!!!"

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    print "It was " + messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    print "My own ID is " + messaging_event["sender"]["id"]
                    message_text = messaging_event["message"]["text"]  # the message's text
                    timestamp = messaging_event["message"]["timestamp"]
                    print "Look, there is a timestamp " + str(timestamp) + " of type " +type(timestamp).__name__

                    send_message(sender_id, "roger that!")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200



def send_message(recipient_id, message_text):

    print "Sending message..."

    params = {
        "access_token": page_access_token
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)


# ===========================================================================================


 #     #                       #                                                               
 ##   ##   ##   # #    #      # #   #####  #####  #      #  ####    ##   ##### #  ####  #    # 
 # # # #  #  #  # ##   #     #   #  #    # #    # #      # #    #  #  #    #   # #    # ##   # 
 #  #  # #    # # # #  #    #     # #    # #    # #      # #      #    #   #   # #    # # #  # 
 #     # ###### # #  # #    ####### #####  #####  #      # #      ######   #   # #    # #  # # 
 #     # #    # # #   ##    #     # #      #      #      # #    # #    #   #   # #    # #   ## 
 #     # #    # # #    #    #     # #      #      ###### #  ####  #    #   #   #  ####  #    #                                                                                             

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    print "Starting the app..." 
    port = int( os.environ.get('PORT', 5000))
    app.run( host='0.0.0.0', port=port)
