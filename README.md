![Release v1.0](https://img.shields.io/badge/release-v1.0-yellow.svg)
![Python 2.7](https://img.shields.io/badge/python-2.7-brightgreen.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)
![MIT license](https://img.shields.io/badge/license-MIT-blue.svg)
[![Twitter URL](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/Coachybot)

# Coachybot

A chatbot designed to perform basic life coaching.<br/>
Running on Kik and Facebook Messenger, and locally on jupyter notebook and terminal.

## Description

Coachybot is a chatbot that leads you through a coaching conversation. During this coaching conversation, Coachybot will:
- Ask how you day was, with a focus on highlights and lowlights
- Probe for open issues and problems
- Ask you to evaluate how relevant and solvable a given problem is
- Brainstorm various possible solutions with you
- Try to get a committment from you for implementing a solution

Do you think it's hopeless/insane/wrong/fascinating to 'teach' coaching, a skill highly based on empathy and wisdom, to a bot? Sometimes I do, too. [On this background page](https://github.com/botmaker-florian/coachybot/master/BACKGROUND.md), you can find some thoughts on why I stink this is valuable and worth trying.

Technically, each state of the coaching conversation is represented as a node class that uses the user's history and current message as arguments and returns the updated user history, the answer and the name of the next node.

```python
>>> user = {
...     "firstname"  : "Alan"
... }
>>> message = "Hello there! :)"
>>> test_node = Welcome( message, user)
>>> test_node.answer
['Oh hello! What a pleasure to meet you, Alan!',
 'My name is Coachybot, but you can call me Coachy.',
 'I have been programmed to improve your life by providing some basic coaching. So...',
 'How are you today?']
>>> test_node.node_next
'HowAreYou'
>>> test_node.user
{'firstname': 'Alan',
 'message_previous': False,
 'node_current': 'HowAreYou',
 'node_previous': 'Welcome'}
```

The natural language processing facilities (dubbed 'skills') of Coachybot are based on keyword lists and regular expressions. Some attempts for a more grammar-based approach using NLTK and sentiment analysis have been implemented, with yet unsatisfactory results.

```python
>>> message = "i really hope that Coachybot provides some value."
>> check_if_statement( message, "has_desire")
True
```

Coachybot is curently hosted on the cloud service Heroku, uses Heroku's postgreSQL database and runs on Facebook Messenger. This repository contains the scripts for running Coachybot on Kik Messenger as well, where the setup process is somewhat easier.

In terms of maturity, Coachybot is in minimum viable product / alpha stage. Chances that you will have a satisfying conversation with Coachybot on Facebook Messenger are not quite bad! The scope of the conversation is limited, and you might well encounter some points where the conversation doesn't flow smoothly.

## Installation

### Quickstart using Jupyter notebook or terminal

To run Coachybot locally, just download and unzip [this entire repository from GitHub](https://github.com/botmaker-florian/coachybot), either interactively, or by entering the following in your Terminal:

```bash
git clone https://github.com/botmaker-florian/coachybot
```

Next, navigate into the top directory of your local repository and install Python's [NLTK](https://www.nltk.com/) and [regex package](https://pypi.python.org/pypi/regex/), if you don't have them already:

```bash
cd coachybot
pip install nltk
pip install regex
```

To have a conversation with Coachybot in your browser and to get a first impresson of how he works, open the repository's notebook file:

```bash
jupyter notebook coachybot_notebook.ipynb
```

Alternatively, to enjoy a plain terminal conversation with Coachybot, do the following:

```bash
python coachybot_terminal.py
```

### Full installation

You can find the installation guide [here](https://github.com/botmaker-florian/coachybot/master/INSTALL.md). It contains instructions to run Coachybot at the cloud hosting service Heroku and to register your bot at Kik and Facebook.

## Testing

### Nodes

Coachybot node classes were developed using rigorous Test-Driven Developemt. The test suite
for the node classes can be run by

```bash
python node-tests.py
```

By toggling the verbose argument in each test function, the node evaluation with the
specific arguments can be investigated.

### Skills / Natural language processing

Most of Coachybot's skills were developed using Test-Driven Development. Admittedly, there is
some confirmation bias, and for a few skills there are no unit tests. The test suite for skills
can be run by

```bash
python skill-tests.py
```

### Cloud-based functionality

Currently, I am not well aware of how to run unit test for the cloud-based functionality. Any suggestions
and hints are welcome!

## Contribution

This is my first open source project, and every form of positive engagement and contribution is welcome!

Please check [CONTRIBUTING.md](https://github.com/botmaker-florian/coachybot/master/CONTRIBUTING.md) for ideas about how and what to contribute. To make engagement in this project a positive experience for everyone involved, please take not of and adhere to the [Contributor Covenant code of conduct](https://github.com/botmaker-florian/coachybot/master/CODE_OF_CONDUCT.md).


## License

Coachybot is published under the [MIT license](https://github.com/botmaker-florian/coachybot/master/LICENSE.md).

## Contact

I look forward to getting in touch with you! The choice of channel is yours:
- [email](mailto:botmaker.florian@gmail.com)
- GitHub message
- [LinkedIn](https://www.linkedin.com/in/florian-hollandt-2a362083/)
- [Twitter](https://twitter.com/Coachybot)
