# Discord Maths Bot
## NOTE
---
The KCL website has recently been updated, and as such until the bot is updated it will not work with the new website. Fix coming as soon as I can manage!
---

A Discord Maths Bot written in Python. designed to give problems from the Kings Maths School Seven Day Maths website. https://www.kcl.ac.uk/mathsschool/weekly-maths-challenge/weekly-maths-challenge.aspx This includes the current weekly challenge, as well as a random problem from their archive.

# Usage
  - `!weekly` to get the weekly challenge
  - `!question` to get a random problem from the archive

# Dependencies
#### Python libraries:
* [discord](http://discordpy.readthedocs.io/en/latest/api.html) - An API wrapper for Discord
* [requests](http://docs.python-requests.org/en/master/) - Used for HTTP requests to fetch content from the website
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - From `bs4`, used to parse the HTML from the website
* [randint](https://docs.python.org/3/library/random.html) - From `random`, does what it says on the tin
* [re](https://docs.python.org/3/library/re.html) - Regular expressions, or regex, used for searching through the HTML
* [math](https://docs.python.org/3/library/math.html) - Mathematical functions, used for its `.floor()` function
* [requests_html](https://html.python-requests.org/_modules/requests_html.html) - Used for additional HTTP requests and parsing HTML

### Other
To know when the weekly challenge has change, the bot relies on a webhook that posts to a Discord channel to trigger the message with the Weekly Challenge in it. This is used because [@sevendaymaths](http://twitter.com/sevendaymaths) only tweets when the challenge has updated, and thus serves as a useful trigger for the bot. Currently, this is done with an [IFTTT](https://ifttt.com/) applet; further details can be found in the Installation guide but details of the applet can be found below.

### Installation

The bot currently is only confirmed to work with Python 3.6. This may change depending on how [`discord.py`](https://github.com/Rapptz/discord.py) is updated, but it is recommended to use at least Python 3.4, and any higher than Python 3.6 may not function correctly.

Install the required libraries using `pip`, again making sure they are the correct versions for your version of Python.

Once all the libraries are installed, the webhook and Discord channel must be set up. Create an [IFTTT](https://ifttt.com) account if you have not already, then create a new applet.
The trigger should be `New tweet by a specific user` where the `username to watch` is `sevendaymaths`. The response should be to `Make a web request` with IFTTT's webhook functionality. The URL should be your own Discord webhook URL; information on how to set this up can be found [here](https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks). Make sure in your Discord server there is a dedicated (ideally private) channel set up, that can be used with this webhook.
The following information should then be filled in about your request:
- **Method**: `POST`
- **Content Type**: `application/json`
- **Body**: `{ "content":"!post {{Text}}"}` (note: the `content` can contain anything, so long as it starts with `!post`)



Finally, ensure that all constants at the top of the program are filled in with your values.
```python
TOKEN = "XXX" #This is the token from Discord for your bot. This assumes your bot has been created and set up already.
NOTIF_CHANNEL_ID = 'XXX' #This is the ID of the channel that your webhook will send messages to
TARGET_CHANNEL_ID = 'XXX' #This is the ID of the channel you would like the bot to send the message containing the Weekly Challenge to
```

And you should be good to go! Simply run your program `python maths-bot.py` to get your bot online.

---
This project is licensed under the terms of the MIT license, which can be found in the `LICENSE.txt` file in the root of the repository.
