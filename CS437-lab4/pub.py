# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import pandas as pd

# Paths to dataset and certificate files
data_path = "./csv_data/vehicle{}.csv"
certificate_formatter = "./cert/certificate_{}.pem"
key_formatter = "./cert/device_{}.private.pem"


class MQTTClient:
    def __init__(self, device_id, cert, key):
        # For certificate-based connection
        self.device_id = str(device_id)
        self.state = 0
        self.client = AWSIoTMQTTClient(self.device_id)
        self.client.configureEndpoint("a1riphw90uetyv-ats.iot.us-east-2.amazonaws.com", 8883)
        self.client.configureCredentials("./keys/AmazonRootCA1.pem", key, cert)
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec

    def customOnMessage(self, client, userdata, message):
        print(f"Client {self.device_id} received payload: {message.payload.decode('utf-8')} from topic: {message.topic}")

    def subscribe(self, topic="vehicle/emission/processed"):
        # Subscribe to the specified topic
        print(f"Subscribing to topic: {topic}")
        self.client.subscribe(topic, 1, callback=self.customOnMessage)

    def publish(self, topic="vehicle/emission/data", id=0):
        # Load the entire vehicle emission data CSV into a DataFrame
        df = pd.read_csv(data_path.format(id))
        
        # Extract 'vehicle_id' and 'vehicle_CO2' columns
        vehicle_id = df['vehicle_id'].tolist()
        vehicle_co2 = df['vehicle_CO2'].tolist()  # Convert the column to a list

        # Create the payload with 'vehicle_CO2' values
        payload = {
            'vehicle_id': vehicle_id,
            'vehicle_CO2': vehicle_co2
        }
        payload_json = json.dumps(payload)

        # Publish the vehicle_CO2 data as a single payload
        print(f"Publishing 'vehicle_CO2' data from {data_path.format(id)} to {topic}")
        self.client.publishAsync(topic, payload_json, 0)

        # Sleep to simulate real-time data publishing if needed
        time.sleep(1)


print("Loading vehicle data...")
data = []
for i in range(5):
    a = pd.read_csv(data_path.format(i))
    data.append(a)

print(data)

print("Initializing MQTTClients...")
client = MQTTClient(1, certificate_formatter.format(1), key_formatter.format(1))
client.client.connect()  # Connect client
client.subscribe()  # Subscribe to the processed data topic

while True:
    print("Send now? (Press 's' to send, 'd' to disconnect, or any other key to retry)")
    x = input()
    if x == "s":
        for i in range(0, 5):
            client.publish(id=i)
    elif x == "d":
        client.client.disconnect()
        print("All devices disconnected")
        exit()
    else:
        print("Wrong key pressed. Please try again.")

    time.sleep(3)
