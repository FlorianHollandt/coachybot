from flask import Flask, request, Response

from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage

import os 

username = os.environ['BOT_USERNAME'] 
api_key = os.environ['BOT_API_KEY']

app = Flask(__name__)
kik = KikApi(username, api_key)

config = Configuration(webhook=os.environ['WEBHOOK'])
kik.set_configuration(config)

@app.route('/', methods=['POST'])
def incoming():

    if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):

        return Response(status=403)

    messages = messages_from_json(request.json['messages'])

    print messages

    for message in messages:
        print message
        if isinstance(message, TextMessage):
            kik.send_messages([
                TextMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    body=message.body
                )
            ])

    return Response(status=200)


if __name__ == "__main__":
    print "Starting the app now!"
    app.run(port=8080, debug=True)
