# Client script
# Communicates to the server via MQTT
from queue import Queue
from threading import Thread
import paho.mqtt.client as mqtt
from subprocess import Popen
import json
import time

# Variables
RUNNING = {}

STATUS = {
    "status":"idle",
    "game":"idle"
}
# <game>:<Popen object>

# Actions
def follow(game, p):
    p.wait()
    STATUS["status"] = "idle"
    STATUS["game"] = "idle"
    del RUNNING[game]

def launch(game, options = None):
    if game in CONFIG['games']:
        if options:
            p = Popen([CONFIG['games'][game]["path"], options])
        else:
            p = Popen([CONFIG['games'][game]["path"], CONFIG['games'][game]["options"]])
        
        RUNNING[game] = p
        Thread(target=follow, args=(game, p)).start()
        CLIENT.publish(f"computers/{ADDRESS}/client", '{"type": "done", "message": "Game launched"}')
        STATUS["status"] = "running"
        STATUS["game"] = game

    else:
        CLIENT.publish(f"computers/{ADDRESS}/client", '{"type": "error", "message": "Game not found"}')
        
def close(game):
    try: 
        p = RUNNING[game]
        p.kill()
        CLIENT.publish(f"computers/{ADDRESS}/client", '{"type": "done", "message": "Game closed"}')
    except KeyError:
        CLIENT.publish(f"computers/{ADDRESS}/client", '{"type": "error", "message": "Game not running"}')


# Communication functions
def incomming_message(client, userdata, msg):
    msg.payload = json.loads(msg.payload)
    if msg.payload["type"] == "launch":
        try: launch(msg.payload["game"], msg.payload["options"])
        except KeyError: launch(msg.payload["game"])
    elif msg.payload["type"] == "close":
        close(msg.payload["game"])
    elif msg.payload["type"] == "library":
        CLIENT.publish(f"computers/{ADDRESS}/client", json.dumps({"type":"library","library":CONFIG['games']}))
    else:
        CLIENT.publish(f"computers/{ADDRESS}/client", '{"type": "error", "message": "Invalid command type"}')

def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    
    # subscribe
    client.subscribe(f"computers/{ADDRESS}/server")

def main():
    # update status
    CLIENT.publish(f"computers/{ADDRESS}/status", json.dumps(STATUS), retain=True)
    time.sleep(5)

# Startup
print("LANMan Client")

print("Loading configuration...", end="\r")
CONFIG = json.load(open('config.json'))
print("Loading configuration  ✓")


ADDRESS = CONFIG['address']
print("Client address:", ADDRESS)

print("Starting MQTT Client...", end="\r")
CLIENT = mqtt.Client(ADDRESS)
CLIENT.on_connect = on_connect
CLIENT.on_message = incomming_message
CLIENT.will_set(f"computers/{ADDRESS}/status", '{"status":"offline"}', retain=True)
CLIENT.username_pw_set("hass", "homeassistant") # for now
CLIENT.connect(CONFIG["server_ip"], 1883, 60)
CLIENT.loop_start()
print("Starting MQTT Client  ✓")

print("Entering mainloop!")

while True: main() # Main loop