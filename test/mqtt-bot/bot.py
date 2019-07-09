import requests
import json
from greenhouse import Greenhouse
import random
import sys
import getopt
import threading
import os

names = [
    'allessandra',
    'alice',
    'arianna',
    'patrizio',
    'massimo',
    'donatello',
    'stefano',
    'gian'
]


class Bot(object):
    def __init__(self, unicity=False):
        self.username = random.choice(
            names) + str(random.randint(1, 999))   # Generate random name
        self.id = ''
        self.greenhouses = []
        self.unicity = unicity

        # Create user
        self.createUser()
        self.createGreenhouses()

    def createUser(self):
        try:
            r = requests.post(os.environ['URI'] + "/api/v1/user",
                              headers={'Content-type': 'application/json',
                                       'Accept': 'application/json'},
                              json={"username": self.username})
        except Exception as e:
            print(e)

        data = json.loads(r.text)
        user = data['data']

        self.id = user['id']
        self.greenhouses = user['greenhouses']

    def createGreenhouses(self):
        if self.unicity:
            ngreenhouses = 2
        else:
            ngreenhouses = random.randint(1, 10)

        for i in range(1, ngreenhouses):
            self.greenhouses.append(Greenhouse(self.id, unicity=self.unicity))
            print('created greenhouse ' + str(i) +
                  ' for user ' + self.username)

    def talk(self):
        for g in self.greenhouses:
            g.talk()


def main():
    hstr = 'bot.py -s <http://uri:port> -n <numberbots>'
    unicity = False
    uri = 'http://localhost:80'
    nbots = 1
    telemetric = None

    try:
        opts, _ = getopt.getopt(sys.argv[1:], "hue:b:t:", [
            "help", "unicity", "server=", "endpoint=", "telemetric="])
    except getopt.GetoptError as err:
        print(str(err))
        print(hstr)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(hstr)
            sys.exit()
        elif opt in ("-u", "--unicity"):
            unicity = True
        elif opt in ("-e", "--endpoint"):
            uri = arg
        elif opt in ("-b", "--bots"):
            nbots = int(arg)
            print(nbots)
        elif opt in ("-t", "--telemetric"):
            telemetric = arg
        else:
            assert False, "unhandled option"

    os.environ['URI'] = uri
    # If unicity is True select the telemetric you want ot test
    if unicity is True:
        if telemetric is None:
            os.environ['TELEMETRIC'] = 'moisture'
        else:
            os.environ['TELEMETRIC'] = telemetric

    bots = []
    # Set unicity to True to generate only one greenhouse, bed and sensor
    for i in range(0, nbots):
        bot = Bot(unicity=unicity)
        bots.append(bot)

    for i in range(0, len(bots)):
        threading.Timer(0.5, bots[i].talk())


if __name__ == '__main__':

    os.environ['CHANNEL_KEY'] = "ea2oE_cLeqzsXNafzhAoIpfewZlx3VeI"
    os.environ['CHANNEL'] = "sensor/moisture/"
    os.environ['HOST'] = "localhost"
    os.environ['PORT'] = "8080"

    main()
