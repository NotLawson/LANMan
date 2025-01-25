import paho.mqtt.client as mqtt
import json, time
from flask import Flask, render_template, request


class Computer:
    status = {"status":"offline"}
    game = "idle"
    library = None
    def __init__(self, name, address):
        self.name = name
        self.address = address
        CLIENT.message_callback_add(f"computers/{address}/client", self.imcomming_message)
        CLIENT.subscribe(f"computers/{address}/client")
        CLIENT.message_callback_add(f"computers/{address}/status", self._status)
        CLIENT.subscribe(f"computers/{address}/status")
        CLIENT.publish(f"computers/{address}/server", json.dumps({"type":"library"}))
        
    def launch(self, game, options = None):
        if options:
            CLIENT.publish(f"computers/{self.address}/server", json.dumps({"type":"launch", "game":game, "options":options}))
        else:
            CLIENT.publish(f"computers/{self.address}/server", json.dumps({"type":"launch", "game":game}))
    def close(self, game):
        CLIENT.publish(f"computers/{self.address}/server", json.dumps({"type":"close", "game":game}))
        pass
    
    def _status(self, client, userdata, msg):
        time.sleep(0.1)
        self.status = json.loads(msg.payload)
        if self.status["status"] == "running":
            if self.library == None:
                CLIENT.publish(f"computers/{self.address}/server", json.dumps({"type":"library"}))
                time.sleep(0.1)
            self.game = self.library[self.status["game"]]
        else:
            self.game = "idle"

    def imcomming_message(self, client, userdata, msg):
        msg.payload = json.loads(msg.payload)
        if msg.payload["type"] == "library":
            self.library = msg.payload["library"]
        elif msg.payload["type"] == "error":
            print(f"Error: {msg.payload['message']}")
        elif msg.payload["type"] == "done":
            print(f"Done: {msg.payload['message']}")
        else:
            print(f"Unknown message type: {msg.payload['type']}")

    # todo: setup actions

class Group:
    def __init__(self, name, computers):
        self.name = name
        self.computers = computers
    
    def launch(self, game, options = None):
        # setup client first before doing too much
        for computer in self.computers:
            computer.launch(game, options)

def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    

# Startup
print("LANMan Server")

print("Loading configuration...", end="\r")
CONFIG = json.load(open('config.json'))
print("Loading configuration  ✓")

print("Starting MQTT Client...", end="\r")
CLIENT = mqtt.Client("LANMan")
CLIENT.on_connect = on_connect
CLIENT.username_pw_set("hass", "homeassistant") # for now
CLIENT.connect(CONFIG["server_ip"], 1883, 60)
print("Starting MQTT Client  ✓")

# Register computers
print("Registering computers")

layout = CONFIG["layout"]

groups = []
for group in layout:
    print("")
    print(group["name"]+" ("+group["id"]+"):")
    computers = []
    for computer in group["computers"]:
        computers.append(Computer(computer["name"], computer["address"]))
        print("    "+computer["name"]+" ("+computer["address"]+")")
        CLIENT.publish(f"computers/{computer['address']}/status", json.dumps({"status":"offline"}), retain=True)
    groups.append(Group(group["name"], computers))

print("Computers registered")

CLIENT.loop_start()

print("Starting web server...")
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", groups = groups)

@app.route("/api/<path:path>")
def api(path):
    path = path.split("/")
    try:
        if path[0] == "action":
            if path[1] == "launch":
                game = request.args.get("game")
                options = request.args.get("options")
                computer = path[2]
                e = False
                for group in groups:
                    for computer in group:
                        if computer.address == computer:
                            if options:

                                computer.launch(game, options)
                            e = True
                            break
                    if e:
                        break
            elif path[1] == "close":
                pass
            elif path[1] == "status":
                pass
            elif path[1] == "library":
                pass
            else:
                pass
    except IndexError:
        return {"error":"Invalid path"}

app.run(port=5000)