import paho.mqtt.client as mqtt

# Define your HiveMQ cluster details
broker = "a08ed05c46d84095a16f4d8ae787f742.s1.eu.hivemq.cloud"
port = 8883
#username = "stinker"
#password = "ThisisTest1"

username= "hivemq.webclient.1724134316495"
password= "a08ed05c46d84095a16f4d8ae787f742.s1.eu.hivemq.cloud"

# Define the topic
topic = "test/topic"


# Define the callbacks
# Define the callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
        client.subscribe(topic)
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} from topic: {msg.topic}")

# Create an MQTT client instance with protocol version
client = mqtt.Client(protocol=mqtt.MQTTv311)

# Set username and password
client.username_pw_set(username, password)

# Enable TLS for a secure connection
client.tls_set()

# Assign the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
try:
    client.connect(broker, port, keepalive=60)
except Exception as e:
    print(f"Connection failed: {e}")

# Publish a message
client.publish(topic, "Hello from HiveMQ!")

# Start the loop to process callbacks
client.loop_forever()