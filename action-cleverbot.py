#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from snipsTools import SnipsConfigParser
import paho.mqtt.publish as publish
import paho.mqtt.client as paho
import time
import json
import cleverbot

CONFIG_INI = "config.ini"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class Cleverbot(object):
    """Class used to wrap action code with mqtt connection

        Please change the name refering to your application
    """
    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None

        self.apiKey = self.config["secret"]["api_key"]

        self.bot = cleverbot.Cleverbot(self.apiKey, timeout=60)

        # start listening to MQTT
        self.tmpClient = paho.Client("snips-skill-cleverbot-" + str(int(round(time.time() * 1000))))
        self.tmpClient.on_message = self.on_message
        self.tmpClient.on_log = self.on_log
        self.tmpClient.connect(MQTT_IP_ADDR, MQTT_PORT)
        self.tmpClient.subscribe("hermes/intent/#")
        self.tmpClient.subscribe("hermes/nlu/intentNotRecognized")
        self.tmpClient.loop_forever()

    def on_message(self, client, userdata, message):
        topic = message.topic
        msgJson = json.loads(message.payload)

        intent_name = "void"

        if "intent" in msgJson:
            intent_name = msgJson["intent"]["intentName"]

        print intent_name
        print topic

        if ':' in intent_name:
            intent_name = intent_name.split(":")[1]

        if intent_name == "cleverbotDiscussion" or topic == "hermes/nlu/intentNotRecognized":
            self.cleverbotDiscussion(payload=msgJson)

    def on_log(self, client, userdata, level, buf):
        if level != 16:
            print("log: ", buf)

    def cleverbotDiscussion(self, payload):
        try:
            reply = self.bot.say(payload["input"])
        except cleverbot.CleverbotError as error:
            print(error)
        else:
            print("[CleverBot]: " + reply)
            self.tmpClient.publish("hermes/dialogueManager/startSession", json.dumps({"siteId": "pi3sat1", "init": {"type": "notification", "text": reply.decode("utf-8")}}))

if __name__ == "__main__":
    Cleverbot()



