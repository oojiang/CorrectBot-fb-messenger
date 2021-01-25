# CorrectBot: A Facebook Messenger Chatbot
CorrectBot is a chatbot that attempts to always be correct by understanding the simple rule:  
*All statements are true unless they are not.*

<img src="images/CorrectBot-Demo.gif" width="250" height="431"/>

In this repository lives the code for CorrectBot's Messenger webhook.
Unfortunately, due to COVID-19, Facebook is 
[not doing app reviews for individuals](https://developers.facebook.com/docs/development/release/individual-verification), 
so CorrectBot cannot live on Messenger for now. 
Try chatting with CorrectBot [here](https://oojiang.github.io/CorrectBot/) instead.

# Technologies
CorrectBot's NLP is powered by Python's [SpaCy](https://spacy.io/) library. 
Its webhook communicates with Facebook's [Messenger API](https://developers.facebook.com/docs/messenger-platform/) 
using [Flask](https://palletsprojects.com/p/flask/) and is hosted on [Heroku](https://www.heroku.com/) for free.
