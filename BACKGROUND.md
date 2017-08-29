# Algorithmic Coaching

If Coachybot reminds you of the famous first chatbot [ELIZA](https://en.wikipedia.org/wiki/ELIZA) (* 1966), you're not quite wrong - She was indeed the inspiration for my first version of Coachybot.

Eliza does not 'lead' the conversation - She cleverly reflects the users' statements as questions, prompting them to explore their own statements in some depth. While being an effective aid for introspection, Eliza's conversations do not lead anywhere.

Coachybot starts with the end in mind - To trigger a positive change in her user's life. Why? Because that is what coaching is about: "If you're not generating action, you're not coaching" says master coach [Michael Bungay-Stanier](http://boxofcrayons.com/michael-bungay-stanier/).

But how to teach the complexity and subtility of a real-life coaching to something as stupid and un-empathic as a bot? If you read this far, you already know my solution: By mapping an idealized coaching conversation to a graph model, where each node represents a state of the conversation.

If coaching is essentially about generating (positive) action, we already have an endpoint of the coaching graph: The user's affirmation of the bot's question "Are you totally committed to doing X?".

The choice of the starting point of the coaching conversation is ours. My choice is to use the formularic greeting "Hello, how are you?" as a starting node and to transition smoothly from there, but it might just as well be the world's best question "What's on your mind?" or even the more explicit "What do you want to talk about?".

Now that the starting and the end point are defined, the challenge is to find a sequence of states that lead from one to the other. No, the actual challenge is to choose those states in such a way that
- they constitute a plausible and enjoyable conversation for the user,
- a conversation can be funneled into this path, and
- it is robust to the deviations of real-life conversations.

Now that already sounds doable, right?

Even more encouraging is that real-life coaches use not only their empathy and wisdom, but also various techniques that easily inspire conversational 'algorithms'. One notable example is the so-called Coaching Funnel, which models a coaching conversation as a two cones joined at their bases:
- The conversation begins rather narrow, by identifying a recent issue of the coachee
- It gets broader as patterns and root causes of the issue are identified
- The broadest part is in the middle, when options for dealing with or improving the situation are explored
- Then it gets narrower again, as plans to pursue a chosen solution are made
- It ends very narrow, at the point where a commitment to the next steps is made

Precisely this Coaching Funnel is the core of the 'alpha' version of Coachybot.

Whether Coachybot is a valid proof of the concept of algorithmic coaching is for the user to decide.<br/>
It is undisputable that such an algorithmic approach to coaching will never reach nearly the performance of an actual coach - To even get close, I would assume that it would at least take a reinforcement learning approach and an immense training dataset. However, an advanced version of Coachybot can still have its use, especially as a easily available guide for exploring current life issues and their possible solutions for (young) people without the resources or opportunities to access actual coaching.


