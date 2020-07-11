#Import libraries
import discord
import requests
from bs4 import BeautifulSoup
from random import randint
import re
import math

#KCL
BASE_URL = "https://www.kingsmathsschool.com"
WEEKLY_URL = BASE_URL + "/weekly-maths-challenge/" # All problems are sourced from the Kings Maths School Seven Day Maths website
TITLE_CLASS = "MathsQuizCardstyled__MathsQuizCardStyled-sc-1bfsz0n-0 fKREdG"
DESCRIPTION_CLASS = "HTMLRaw HTMLRaw-sc-40skyg-0 eMcAdk"
PAGENUMBER_CLASS = "last PagingItemstyled__PagingItemStyled-sc-84ej5y-0 KLJqO"
TITLE_ROLE = "page title"

#Discord
TOKEN = 'XXX'
NOTIF_CHANNEL_ID = 123
TARGET_CHANNEL_ID = 123

#Bot
FILENAME = "challenge.txt" # tracks challenges that have inconsistent URLs (do not end in "challenge-[num]") or are broken 

#Messages
WEEKLY_TEXT = "This week's challenge!\n--------------------------\n" # Beginning of the message that gets posted when the weekly problem updates
HELP = """```A maths bot to give maths questions from King's Maths School's weekly maths challenge questions!

%help - This command! Lists possible commands and their usage.
%weekly - Returns that week's maths question.
%question [number] [category] - Returns a maths question; either from a specific challenge number, or random from a specific category (listed below) or all questions if no category is specified.

Question Categories:
Algebra
Combinatorics
Geometry
Number Theory
Probability
Ratios and Proportions```"""

# Gets the most recent (weekly) challenge's url or number
def getMostRecentChallenge(url):
    r = requests.get(WEEKLY_URL)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')

    #Find all questions on the page, and get the top (most recent) one
    questions = soup.findAll("a", {"class": TITLE_CLASS})
    link = questions[0]["href"]
    
    if url:
        return link
    else:
        result = 0
        i = -1
        con = True
        # the url will typically end in "challenge-[num]", but may sometimes have additional words separated by hyphens
        while con: # iterate backwards through the string until a valid challenge number is found
            try:
                result = int(link.split("-")[i])
                con = False
            except Exception:
                i -= 1

        return result

# Gets the title of a problem from the challenge URL
def getTitle(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')

    # find the title on the page based off HTML role name
    title = soup.findAll("h2", {"role": TITLE_ROLE})[0].contents[0]
    return title

def getDescription(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')

    # find the description on the page from the HTML class name
    div = soup.findAll("div", {"class": DESCRIPTION_CLASS})[0]
    return div.getText() # returns the text in that element, which will be the entire challenge description

# Get all the challenge numbers for a specified mathematical category
def getCategoryChallengeNums(category):
    # sets up base URL
    category = category.lower()
    url = WEEKLY_URL + "1"
    urlEnd = "?category="

    # convert bot category names to URL endings
    if category == "algebra":
        urlEnd = urlEnd + "algebra"
    elif category == "combinatorics":
        urlEnd = urlEnd + "combinatorics"
    elif category == "geometry":
        urlEnd = urlEnd + "geometry"
    elif category == "number" or "number theory":
        urlEnd = urlEnd + "number"
    elif category == "probability":
        urlEnd = urlEnd + "probability"
    elif category == "ratios" or category == "proportions" or category == "ratios and proportions":
        urlEnd = urlEnd + "ratios-and-proportions"
    else:
        return ""

    r = requests.get(url+urlEnd)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')

    # challenges will likely be split across multiple pages, so find the final page based on HTML class name
    lastPage = soup.findAll("button", {"class": PAGENUMBER_CLASS})[0]
    lastPage = lastPage.findChildren()[0].getText()

    nums = []
    # iterate through all pages containing challenges of this category
    for i in range(1, int(lastPage)+1):
        # get the challenges for the current page
        url = WEEKLY_URL + str(i)
        r = requests.get(url+urlEnd)
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')

        # get all links to challenges on this page
        links = soup.findAll("a", {"class": TITLE_CLASS})

        # for each challenge, get the challenge number
        for j in links:
            k = -1
            con = True
            # the url will typically end in "challenge-[num]", but may sometimes have additional words separated by hyphens
            while con: # iterate backwards through the string until a valid challenge number is found
                try:
                    nums.append(int(j["href"].split("-")[k]))
                    con = False
                except Exception:
                    k -= 1

    return nums # returns list of challenge numbers

# returns the message to be sent by the bot, either for the weekly challenge, a random one (default number), a specified number or a random challenge from a mathematical category
def question(weekly=False, number=-1, category="NONE"):
    if weekly: # return current weekly challenge
        url = BASE_URL + getMostRecentChallenge(True)
        title = getTitle(url)
        description = getDescription(url)

        # title in bold
        message = "**" + title + "**\n" + description
        return message
    else:
        if number == -1:
            if category == "NONE": # random question, generate random number up to most recent challenge number
                number = randint(1, int(getMostRecentChallenge(False)))
            else: # pick a random challenge number from the list generated for the specified category
                nums = getCategoryChallengeNums(category)
                rand = randint(0, len(nums)-1)
                number = nums[rand]

        # get dictionary of all broken/inconsistent challenges from external file
        brokenChallenges = {}
        with open(FILENAME) as file:
            for line in file:
                (key, value) = line.split(" ")
                brokenChallenges[int(key)] = value.rstrip("\n")

        # if the challenge is broken or has an inconcsistent URL
        if number in brokenChallenges.keys():
            if brokenChallenges[number] == "BROKEN":
                message = "There was a problem, that question could not be fetched. Sorry!"
                return message
            else: # adjust URL and send message
                url = brokenChallenges[number]
                title = getTitle(url)
                description = getDescription(url)

                # title in bold
                message = "**" + title + "**\n" + description
                return message
        else:
            try: # get the message for the challenge of the number specified earlier (by user or picked programmatically)
                url = WEEKLY_URL + "challenge-" + str(number)

                title = getTitle(url)
                description = getDescription(url)

                # title in bold
                message = "**" + title + "**\n" + description
                return message
            except Exception:
                message = "There was a problem, that question could not be fetched. Sorry!"
                return message
    return "There was a problem, that question could not be fetched. Sorry!" # if no other message returned, return an error

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # send help message
    if message.content.startswith('%help'):
        msg = HELP
        await message.channel.send(msg)

    # sends message with current weekly challenge
    if message.content.startswith("%weekly"):
        msg = question(True)
        pointer = 0
        for i in range(math.ceil(len(msg) / 2000)): # discord character limit
            content = msg[pointer:pointer+2000]
            await message.channel.send(content)
            pointer += 2000

    # returns either a random question (from a category if specified) or one with a specific challenge number
    if message.content.startswith("%question"):
        args = message.content.split(" ") # get any arguments
        if len(args) > 1: # if there were additional arguments
            try: # if the argument was a number
                num = int(args[1])
                msg = question(False, number=num) # get the challenge for the specified number
            except ValueError: # argument was not a number, therefore treat it as a category name
                msg = question(False, category=args[1]) # get a challenge from the specified category
        else:
            msg = question(False) # get a random challenge

        pointer = 0
        for i in range(math.ceil(len(msg) / 2000)): # discord character limit
            content = msg[pointer:pointer+2000]
            await message.channel.send(content)
            pointer += 2000
        

    #The bot posts a message when the weekly challenge updates; this relies on a webhook connected to their Twitter account. (which only tweets when the challenge updates)
    #The bot listens to a specific channel; this should be a private channel only used for the webhook
    #When a message is sent to the notification channel, the bot posts the weekly challenge to the target channel.
    notifChannel = client.get_channel(NOTIF_CHANNEL_ID)
    targetChannel = client.get_channel(TARGET_CHANNEL_ID)
    
    if message.channel == notifChannel and message.content.startswith("!post"):
        msg = WEEKLY_TEXT
        msg += question(True) # get current weekly challenge

        # check if the weekly URL is inconsistent (not ending with "challenge-[num]")
        weeklyUrl = getMostRecentChallenge(True) # get weekly URL
        broken = False
        try:
            result = int(weeklyUrl.split("-")[-1]) # if it ends with an integer
        except Exception:
            broken = True # otherwise, URL is inconsistent and must be tracked

        # if weekly URL is inconsistent, add to tracked list in external file
        if broken:
            with open(FILENAME, "a+") as file:
                # format for each line is "[num] url"
                line = str(getMostRecentChallenge(False)) + " " + BASE_URL + str(getMostRecentChallenge(True)) + "\n"
                file.write(line)

        currentPins = await targetChannel.pins() #Gets all current pins from the channel where the message is to be posted
        for i in currentPins: #Loops through all currently pinned messages
            if i.content.startswith(WEEKLY_TEXT) and i.author == client.user: #If the message is the last weekly problem post
                await i.unpin() #Unpin the message

        toPin = await targetChannel.send(msg) #Sends the message to the target channel, and assigns that message to the variable toPin
        await toPin.pin() #Pins the message

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(activity=discord.Activity(name='%help', type=discord.ActivityType.watching))

client.run(TOKEN)
