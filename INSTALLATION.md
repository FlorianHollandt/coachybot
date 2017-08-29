# Setup

To get your local clone of Coachybot running on Kik or Facebook Messenger, you will have to do the full installation including setting up your Heroku account and database. It is totally doable, but it will take you some minutes. :)

## Heroku setup, including database

**Step 1:** Set up your Heroku account and create an app as described in [this excellent guide](https://github.com/kikinteractive/kik-bot-python-example) by @kikinteractive. For the purpose of this setup, you can skip the tutorial.

**Step 2:** In your new account's app home screen, you can see a button "Add ressources". Klick here and select to add a new (free, using the 'hobby-dev' tier) PostgreSQL database to your account. We will set up the tables in a moment, but for now, just copy the database URL and (in 'Settings') enter it as the value of a new environment variable `DATABASE_URL`.

**Step 3:** We now install the Heroku command line interface and log in with the credentials of our new account. You can skip this step if you already have the Heroku CLI installed and are logged in.

```bash
sudo add-apt-repository "deb https://cli-assets.heroku.com/branches/stable/apt ./" 
curl -L https://cli-assets.heroku.com/apt/release.key | sudo apt-key add - 
sudo apt-get install heroku 

heroku login
```

**Step 4:** We need to install Coachybot's dependencies. To prevent interference between this repository's and your general Python setup, we use a [virtual environment](https://virtualenv.pypa.io/en/stable/).

```bash
virtualenv venv
source venv/bin/activate

pip install -r requirements.txt
```

**Step 5:** Validate that Coachybot's nodes and skills work properly on your system by running their unit test suites. Neither of them should produce any errors or failures:

```bash
python node_tests.py
python skill_tests.py
```

**Step 6:** Now we set up the database tables. To do this, open the file `setup_tables.sql`, select and copy everything and paste it into the command line as described below.


```bash
heroku pg:psql

>> Paste copied sql code here! <<

\q
```

That's been the Heroku setup part for now. Before we can upload the repository on Heroku, we first need to set up one messenger and enter its login credentials as Heroku environment variables. 

At this point you should have decided whether you want to use Coachybot in Kik or Facebook messenger. You need to acutally make this decision instead of simply running Coachybot on both simultaneously, because the free Heroku account only allows you one active process.

## Kik setup

In Kik Messenger, your bot will appear similar to a regular user with a username, a first and last name and a profile picture. The profile picture will contain a small violett __thingy__ to indicate that it is a bot and not a human.

To proceed with the next steps of the installation for Kik Messenger, you need to have the app installed (You can get it from [Play Store]() or [App Store]()).

**Step 1:** Go to [the Kik developer page](https://dev.kik.com/#/home) and get a scan code, which you scan using the Kik Messenger app. This will prompt a conversation with Botsworth, your friendly bot-configuration bot. You will meet him again every time you want to log back in (with a new session) in the Bot Configuration Center.

**Step 2:** Botsworth will ask you for the name of your bot, which you should provide and confirm. Back on your desktop, you will be asked to confirm the [Kik API Terms of Use](https://engine.kik.com/#/terms).

**Step 3:** 

## Facebook setup

In Facebook, your bot will have a page which you can decorate and where you can post stuff. The actual chatbot will be the part of the page where you can write it a message using Facebook Messenger.

Facebook offers a huge range of options concerning your Facebook page and the 'app' that you build around it. For this tutorial, we will focus on setting up the Messenger interface for sending and receiving text messages.

This tutorial is based on [the excellent introduction of how to build a Facebook Messenger bot](https://blog.hartleybrody.com/fb-messenger-bot/) by @hartleybrody.

**Step 1:** [Create a Facebook page](https://www.facebook.com/pages/create/) for your bot. The name of the page should be your bot's name. Everything else about the bot's page, including the category, is decoration and not neccessary for the purpose of this tutorial.

** Step 2:** Go to [the Facebook developer quickstart site](https://developers.facebook.com/quickstarts/?platform=web) ans click on 'Skip and Create App ID' - I Facebook's terminology, your cloud-hosted chatbot is considered an app. You need to provide the display name of your app.


** Step 3:** You should now be in the 'Select a product' site of your Facebook app's backend - If you aren't, go to [your app overview](https://developers.facebook.com/apps/), select your new app, and choose '+ Add Product' from the navigation sidebar.<br/>
Now choose 'Messenger' and click on 'Set up'. On the Messenger settings page, go to the box 'Token Generation' and select the page of your bot from the dropdown 'Page'. You need to allow the app to access the page's setting, and will then get a 'Page Access Token' displayed.

At this point, switch to your Heroku app's backend and set up a new config variable `FACEBOOK_PAGE_ACCESS_TOKEN` with the Token from Facebook as its value. <br/>
Alternatively, you can do this with the Heroku CLI:

```bash
heroku config:add FACEBOOK_PAGE_ACCESS_TOKEN=your_page_token_here
```

** Step 4:** Now you already need to push your local repository to Heroku, so that the app will reply to Facebook's Token verification request:

```bash
git push heroku master
```



** Step 5:** You should now be in the 'Select a product' site of your Facebook app's backend - If you aren't, go to [your app overview](https://developers.facebook.com/apps/), select your new app, and choose '+ Add Product' from the navigation sidebar.<br/>
Now choose 'Webhooks', select 'Page' from the dropdown (where 'User' is selected by default) and click on 'Subscribe to this topic'.<br/>
You should now see a layer with two text entry fields, 'Callback URL' and 'Verify Token':
- In the field 'Callback URL', you need to enter the URL of your Heroku app, e.g. `https://foobar.herokuapp.com/`
- In the filed 'Verify token', you need to enter a string that Facebook uses as a part of the verification process. Consider using something that is difficult to guess like [a random key](https://randomkeygen.com/).

Now quickly switch to your Heroku app backend, go to 'Settings', and enter a new config variable `FACEBOOK_VERIFY_TOKEN` with the 'Verfiy token' value you just entered for your Facebook webhook.<br/>
Alternatively, you can do this with the Heroku CLI:

```bash
heroku config:add FACEBOOK_VERIFY_TOKEN=your_verification_token_here
```

Switch back to the Facebook webhook configuration and click on 'Verify and Save'. If there is an error, it means that the Facebook cannot complete the verification process... Either because it cannot connect to your Heroku app, or because it doesn't receive the token. In this case, make sure that the environment variable is set correctly and that the app was successfully built and started in Heroku.


** Step :**


** Step :**


** Step :**


** Step :**


## Testing
