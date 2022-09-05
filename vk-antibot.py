# antibots with Amino.py

import os
from time import sleep
from contextlib import suppress
from time import time as timestamp
from json import loads, dump

os.system("pip install --upgrade Amino.py")
from amino import (
    Client,
    SubClient,
    objects
)


clear = lambda: os.system("cls" if os.name == "nt" else "clear")

clear()

#--------------------account-info--------------------#
email = input("Email?: ")
password = input("Password?: ")
secret = "" if password else input("Secret?: ")
device="423ae9aef48008707155ba8ca2d258e5a90475821e2e59298731de68e29a4cf40aaaced538db3ee5fd"
#-----------------end-account-info----------------#



#-------------------configuration--------------------#
errorFormat = "[antibot]:{userId}: {args}"
loggerFile = "deleted-bots-ids.txt"
community = input("\nCommunity-Link?: ")
admins = [
    input("Your Global Link?: ")
]
https = input("Https-Proxy?: ")
#----------------end-configuration----------------#


ANTIRAID = {}
ANTISPAM = {}
ANTIBOT = {}
cache = {}
spamCache = {}


bot = Client(
    deviceId = device,
    proxies = {"https": https.replace("https://", "") if https else None}
)



bot.admins = [
    bot.get_from_code(link).objectId for link in admins
]


def isadmin(event: objects.Event) -> bool:
    return event.userProfile.userId in bot.admins



def get_clients(event: objects.Event) -> SubClient:
    subclient = SubClient(
        comId = event.comId,
        profile = bot.profile
    )
    subclient.device_id = bot.device_id
    return subclient



def reg_event(comId: int) -> None:
    while True:
        with suppress(Exception):
            bot.subscribe_topic(comId = comId, topic=0)
            break
        sleep(1)



def detectUrl(text: str) -> list:
    return [url for url in text.split() if any(url.startswith(x) for x in ["http://", "https://", "ndc://"])]



def urlFilter(url: str, comId: int) -> bool:
    with suppress(Exception):
        return Amino.get_from_code(url).comId != comId
    return True



helpText = """
[c]Command List

▪︎!antibot: on | off

▪︎!antiraid: on | off

▪︎!antispam: on | off

▪︎!help: on| off
"""



def antiBotFunc(event: objects.Event) -> None:
    if ANTIBOT.get(event.message.comId, False) is False:
        return None

    Amino = get_clients(event = event)
    Profile = event.userProfile

    if Profile.reputation > 25:
        return

    if Profile.icon is not None:
        return

    Members = Amino.get_all_users(
        type = "recent",
        start = 0,
        size = 50
    ).profile

    users = zip(Members.userId, Members.nickname, Members.reputation)

    users = filter(lambda x: x[0] != Profile.userId, users)

    userIds = map(lambda x: x[0], users)
    nicknames = map(lambda x: x[1], users)
    reputations = map(lambda x: x[2], users)

    if Profile.nickname not in nicknames:
        return

    try:
        Amino.ban(
            userId = Profile.userId,
            reason = "user is Bot",
        ); sleep(1)
        with open(loggerFile, "a") as log:
            log.write("ndc://user-profile/%s\n" % Profile.userId)

        print("~ Banned susseffuly -> %r bot!" % Profile.nickname)

    except Exception as Error:
        textError = errorFormat.format(
            userId = Profile.userId,
            args = Error.args[0]["api:message"] if isinstance(Error.args[0], dict) else Error.args[0]
        )

        print(textError)
        return None



def antiRaidFunc(event: objects.Event) -> None:
    global cache

    if ANTIRAID.get(event.chatId, False) is False:
        return None

    Amino = get_clients(event = event)
    Profile = event.userProfile
    chatId = event.message.chatId

    if chatId not in cache.keys():
        cache[chatId] = {}

    if Profile.userId not in cache.keys():
        cache[Profile.userId] = 0

    if Profile.userId not in cache.get(chatId, {}).keys():
        cache[chatId][Profile.userId] = int(timestamp())
        return None

    lastMsg = cache.get(chatId, {}).get(Profile.userId, 0)

    if (timestamp() - lastMsg) > 4:
        cache[chatId][Profile.userId] = int(timestamp())
        if cache.get(Profile.userId, 0) > 0:
            cache[Profile.userId] -= 1
        return None

    if (warns := cache.get(Profile.userId, 0)) < 10:
        cache[Profile.userId] = warns + 1

        print(">> %r %s..." % (Profile.nickname, ("is fast" if warns < 4 else "is very fast" if warns < 8 else "looks like a bot")))

        if warns >= 8:
            Amino.send_message(
                chatId = chatId,
                message = "You look like a bot!, if you keep sending quick messages you will be banned!"
            )

        return None

    Amino.kick(
        chatId = chatId,
        userId = Profile.userId,
        allowRejoin = False
    )

    print("~ Kick from %r -> %r bot!" % (title, Profile.userId))



def antiSpamFunc(event: objects.Event) -> None:
    global spamCache

    if ANTISPAM.get(event.comId, False) is False:
        return None

    Amino = get_clients(event = event)
    Profile = event.userProfile
    chatId = event.message.chatId

    if chatId not in spamCache.keys():
        spamCache[chatId] = {}

    urls = detectUrl(text = event.message.content)
    urls = list(filter(lambda x: urlFilter(x, comId), urls))

    if not urls:
        return None

    print(">> %r is spamming!" % Profile.nickname)

    with suppress(Exception):
        Amino.delete_message(
            chatId = chatId,
            messageId = event.message.messageId,
            asStaff = True,
            reason = "spam message"
        )

    if Profile.userId not in spamCache.get(chatId, {}).keys():
        spamCache[chatId][Profile.userId] = {
            "time": int(timestamp()),
            "content": event.message.content,
            "spams": urls,
            "count": 1
        }

        return None

    if (count := spamCache[chatId][Profile.userId].get("count", 1)):
        Amino.send_message(
            chatId = chatId,
            message = "You are spamming, be careful." if count < 4 else "Do not send spam or you could be banned." if count < 7 else "%d more spam and you will be banned from the community" % (10 - count)
        )

        if count < 7:
            return None

        elif count < 10:
            Amino.kick(
                userId = Profile.userId,
                chatId = chatId,
                allowRejoin = True
            )

            return None

    Amino.ban(
        userId = Profile.userId,
        reason = "user is spammer",
    )

    print("\n>> banned %r bot!" % Profile.nickname)



def antiBotConfig(event: objects.Event) -> None:
    global ANTIBOT

    Amino = get_clients(event = event)
    Profile = event.userProfile
    chatId = event.message.chatId

    if not isadmin(event = event):
        return None

    if "on" in event.message.content.lower().split():
        ANTIBOT[comId] = True

        Amino.send_message(
            chatId = event.message.chatId,
            message = "Antibot is ready!"
        ); return None

    elif "off" in event.message.content.lower().split():
        ANTIBOT[comId] = False

        Amino.send_message(
            chatId = event.message.chatId,
            message = "Antibot was turned off!"
        ); return None

    Amino.send_message(
        chatId = event.message.chatId,
        message = "antibot status: %s" % "ON" if ANTIBOT.get(chatId) else "OFF"
    )



def antiRaidConfig(event: objects.Event) -> None:
    global ANTIRAID

    Amino = get_clients(event = event)
    Profile = event.userProfile
    chatId = event.message.chatId

    if not isadmin(event = event):
        return None

    if "on" in event.message.content.lower().split():
        ANTIRAID[comId] = True

        Amino.send_message(
            chatId = event.message.chatId,
            message = "Antiraid is ready!"
        ); return None

    elif "off" in event.message.content.lower().split():
        ANTIRAID[comId] = False

        Amino.send_message(
            chatId = event.message.chatId,
            message = "Antiraid was turned off!"
        ); return None

    Amino.send_message(
        chatId = event.message.chatId,
        message = "antiraid status: %s" % "ON" if ANTIRAID.get(chatId) else "OFF"
    )



def antiSpamConfig(event: objects.Event) -> None:
    global ANTISPAM

    Amino = get_clients(event = event)
    Profile = event.userProfile
    chatId = event.message.chatId

    if not isadmin(event = event):
        return None

    if "on" in event.message.content.lower().split():
        ANTISPAM[comId] = True

        Amino.send_message(
            chatId = event.message.chatId,
            message = "Antispam is ready!"
        ); return None

    elif "off" in event.message.content.lower().split():
        ANTISPAM[comId] = False

        Amino.send_message(
            chatId = event.message.chatId,
            message = "Antispam was turned off!"
        ); return None

    Amino.send_message(
        chatId = event.message.chatId,
        message = "antispam status: %s" % "ON" if ANTISPAM.get(chatId) else "OFF"
    )



def helpFunc(event: objects.Event) -> None:
    Amino = get_clients(event = event)
    Profile = event.userProfile
    chatId = event.message.chatId

    Amino.send_message(
        chatId = chatId,
        message = helpText,
        replyTo = event.message.messageId
    )



@bot.event("on_live_user_update")
def on_live_user_update(event: objects.Event) -> None:
    Thread(
        target = antiBotFunc,
        args = [event]
    ).start()



@bot.event("on_all")
def on_text_message(event: objects.Event) -> None:

    if (message := event.message.content):
        if message.lower().split()[0] == ("!help"):
            event.message.content = " ".join(message.split()[1:])
            return Thread(
                target = helpFunc,
                args = [event]
            ).start()

        if message.lower().split()[0] == ("!antibot"):
            event.message.content = " ".join(message.split()[1:])
            return Thread(
                target = antiBotConfig,
                args = [event]
            ).start()

        if message.lower().split()[0] == ("!antiraid"):
            event.message.content = " ".join(message.split()[1:])
            return Thread(
                target = antiRaidConfig,
                args = [event]
            ).start()

        if message.lower().split()[0] == ("!antispam"):
            event.message.content = " ".join(message.split()[1:])
            return Thread(
                target = antiSpamConfig,
                args = [event]
            ).start()

    Thread(
        target = antiRaidFunc,
        args = [event]
    ).start()

    Thread(
        target = antiSpamFunc,
        args = [event]
    ).start()

    Thread(
        target = antiBotFunc,
        args = [event]
    ).start()



def main_function() -> None:
    bot.login(
        email = email,
        password = password if password else None,
        secret = secret if secret else None
    )

    if community:
        comId = bot.get_from_code(community).comId
        reg_event(comId = comId)

    else:
        for comId in bot.sub_clients(size = 30).comId:
            reg_event(comId = comId)

    print(">> ready!")

    while True:
        sleep(180)
        bot.close()

        bot.login(
            email = email,
            password = password if password else None,
            secret = secret if secret else None
        )



if __name__ == "__main__":
    clear()
    print(">> wait...")
    main_function()
