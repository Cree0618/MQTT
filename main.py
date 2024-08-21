import paho.mqtt.client as mqtt
import time

# Callback when connected to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("test/topic")

# Callback when a message is received
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

# Create MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# Connect to a public MQTT broker
client.connect("a08ed05c46d84095a16f4d8ae787f742.s1.eu.hivemq.cloud", 8883, 60)

# Start the loop to process network events
client.loop_start()

# Publish a message every 5 seconds
while True:
    client.publish("test/topic", "Hello, MQTT!")
    time.sleep(5)