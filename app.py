import os
import sys
import json

import requests
from flask import Flask, request

import hmac
from hashlib import sha1

import sentences

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
APP_SECRET = os.environ.get("APP_SECRET")
app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.challenge'):
        if not request.args.get('hub.verify_token') == VERIFY_TOKEN:
            log('AAA')
            log(request.args.get('hub.verify_token'))
            log(VERIFY_TOKEN)
            log('BBB')
            return "Verification token mismatch", 403
        else:
            return request.args['hub.challenge'], 200
    else:
        return ':)', 200
    
@app.route('/', methods=['POST'])
def webhook():
    try:
        header_signature = request.headers.get('X-Hub-Signature')
        if not header_signature:
            log('X-Hub-Signature missing')
            return 'ok', 200
        expected_signature = hmac.new(bytes(APP_SECRET, 'utf-8'), 
                                        bytes(request.data, 'utf-8'), digestmod='sha1').hexdigest()
        if not hmac.compare_digest(expected_signature, header_signature):
            log('X-Hub-Signature mismatch')
            return 'ok', 200
    except BaseException:
        log("X-HUB-SIGNATURE EXCEPTION")
        print(BaseException.with_traceback())
        return 'ok', 200
    data = request.get_json()
    if data.get('object') == 'page' and data.get('entry'):
        for entry in data['entry']:
            for event in entry.get('messaging'):
                if event.get('message'):
                    sender_id = event['sender']['id']
                    recipient_id = event['recipient']['id']
                    message_text = event['message']['text']
                    try:
                        send_message(sender_id, gen_response(message_text))
                    except BaseException: 
                        log("SOMETHING WENT WRONG")
                        send_message(sender_id, "Woops, something went wrong (unless nothing did).")
    return 'ok', 200
    
def gen_response(user_text):
    log("RECEIVED MSG: " + user_text)
    pov_text = sentences.changepov(user_text)
    sents = sentences.qualify(pov_text)
    if sents:
        out = "So, you believe: " + sents.pop(0) \
            + "\nHave you considered that maybe: " + sents.pop(0)
        while(sents):
            out += "\nor maybe: " + sents.pop(0)
        return out
    else:
        return "Hi! I believe that all things are true, unless they are not true! What is something that you believe?"

def send_message(user_id, text):
    url = "https://graph.facebook.com/v9.0/me/messages"
    params = {"access_token" : ACCESS_TOKEN}
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "messaging_type": "RESPONSE",
        "recipient": {
            "id": user_id
        },
        "message": {
            "text": text
        }
    })
    log('ATTEMPTING TO SEND MESSAGE: ' + text)
    log('DATA: \n' + data)
    r = requests.post(url, params=params, headers=headers, data = data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def log(message):
    print(message)
    sys.stdout.flush()
