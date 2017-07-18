import time

import artikcloud
import json
from artikcloud.apis.messages_api import MessagesApi
from pprint import pprint
from random import randint
import websocket 
from websocket import create_connection
import thread
DEFAULT_CONFIG_PATH = 'config/config.json'

INTERVAL = 10 #in seconds

class SmartPole:

    sdid = ''
    token = ''
    akc_config = artikcloud.Configuration()
    ARTIK_URI = "wss://api.artik.cloud/v1.1/websocket?ack=true"
    ###ws = websocket.WebSocket()
    ws = create_connection(ARTIK_URI)
    def __init__(self):
        with open(DEFAULT_CONFIG_PATH, 'r') as config_file:
            config = json.load(config_file)['pole']
        self.akc_config.access_token = config['deviceToken']
        self.token = config['deviceToken']
        self.sdid  = config['deviceId']
        REGISTER_JSON = json.dumps({"sdid": self.sdid,
                                    "Authorization": "bearer " + self.token,
                                    "type": "register"
                                    })

        ##self.ws.connect(self.ARTIK_URI)

        try:
            print "starting websocket listner thread"
            thread.start_new_thread(self.process_action, (self.ws, "ws"))
        except:
            print "Error: unable to start thread"

        self.ws.send(REGISTER_JSON)


    def send_message(self,field,val):
        message = artikcloud.Message()
        message.type = "message"
        message.sdid = self.sdid
        message.ts = int(round(time.time() * 1000))
        message.data = {field: val}
        api = MessagesApi()

        response = api.send_message(message)
        #pprint(response)

    def process_action(self,ws,name):
        print "listener thread started"

        while(True):
            result = ws.recv()

            json_res = json.loads(result)
            if ('data' in json_res and 'actions' in json_res['data'] and
                        json_res['data']['actions'][0]['name'] == 'setBrightness'):
                print "brightness is", json_res['data']['actions'][0]['parameters']['brightness']




if __name__ == '__main__':

    pole = SmartPole()

    while(True):
        msg_type_int = randint(1, 4)
        if(msg_type_int == 1):
            msg_type = 'UBATT'
        elif(msg_type_int == 2):
            msg_type = 'TBATT'
        elif(msg_type_int == 3):
            msg_type = 'BATTSTAT'
        else:
            msg_type = 'BRGT'

        value = randint(0,100)
        print "sending {} {}".format(msg_type, value)
        pole.send_message(msg_type,value)
        time.sleep(INTERVAL)
