# antibot-with Amino.py

import os
from time import sleep
from contextlib import suppress
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
secret = input("Secret?: ") if not password else ""
device="423ae9aef48008707155ba8ca2d258e5a90475821e2e59298731de68e29a4cf40aaaced538db3ee5fd"
https = input("Https-Proxy?: ")
#-----------------end-account-info----------------#



#-------------------configuration--------------------#
errorFormat = "[antibot]:{userId}: {args}"
loggerFile = "deleted-bots-ids.txt"
community = "http://aminoapps.com/c/"
#----------------end-configuration----------------#



bot = Client(
    deviceId = device,
    proxies = {"https": https.replace("https://", "")}
)



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



def checkTask(event: objects.Event) -> (bool, str):
    Amino = get_clients(event = event)
    Profile = event.userProfile

    if Profile.reputation > 25:
        return False

    if Profile.icon is not None:
        return False

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
        return False

    try:
        Amino.ban(
            userId = Profile.userId,
            reason = "Bot",
        ); sleep(1)
        with open(loggerFile, "a") as log:
            log.write("ndc://user-profile/%s\n" % Profile.userId)

        return Profile.nickname

    except Exception as Error:
        textError = errorFormat.format(
            userId = Profile.userId,
            args = Error.args[0]["api:message"] if isinstance(Error.args[0], dict) else Error.args[0]
        )

        print(textError)
        return False



@bot.event("on_live_user_update")
def on_live_user_update(event: objects.Event) -> None:
    if (nick := checkTask(event = event)) is not False:
        print("~ Banned susseffuly -> %r bot!" % nick)



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
        bot.run_amino_socket()

if __name__ == "__main__":
    clear()
    print(">> wait...")
    main_function()
