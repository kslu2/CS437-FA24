# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import csv
import logging
import json
import pandas as pd

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Modify these paths as needed
certificate = "./cert/certificate_{}.pem"
key = "./cert/device_{}.private.pem"
data_path = "./keys/AmazonRootCA1.pem"
output_file = './csv_data/max/vehicle_max.csv'

def process_csv(input_data, output_file):
    try:
        # Read and parse the CSV file
        vehicle_data = json.loads(input_data)

        # Calculate max CO2 emission
        print(vehicle_data)
        max_CO2 = float(max(vehicle_data['vehicle_CO2']))
        vehicle_id = vehicle_data['vehicle_id'][0]

        if vehicle_id is None:
            logger.error("No valid vehicle data found.")
            return

        # Write the result to a new CSV file
        with open(output_file, mode='w', newline='') as outfile:
            fieldnames = ['vehicle_id', 'max_CO2']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'vehicle_id': vehicle_id, 'max_CO2': max_CO2})

        logger.info(f"Max CO2 emission for vehicle {vehicle_id}: {max_CO2} saved to {output_file}")

    except Exception as e:
        logger.error(f"Error processing CSV file: {e}")

class MQTTClient:
    def __init__(self, device_id, cert, key):
        # For certificate-based connection
        self.device_id = str(device_id)
        self.client = AWSIoTMQTTClient(self.device_id)
        self.client.configureEndpoint("a1riphw90uetyv-ats.iot.us-east-2.amazonaws.com", 8883)
        self.client.configureCredentials(data_path, key, cert)
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec
        self.client.onMessage = self.customOnMessage  # Handle incoming messages
        
    def customOnMessage(self, message):
        # Print the incoming message payload to the console
        print(f"Received message: {message.payload} from topic: {message.topic}")

    def subscribe(self, topic="vehicle/emission/data"):
        # Subscribe to the given topic
        print(f"Subscribing to topic: {topic}")
        print(self.client.subscribe(topic, 1, callback=self.customSubackCallback))
        
    def customSubackCallback(self, client, userData, message, topic="vehicle/emission/processed"):
        #print(f"Received message with topic: {message.topic}")
        payload = message.payload.decode('utf-8')
        #print(f"Message Payload: {payload}")
        process_csv(payload, output_file)
        df = pd.read_csv(output_file)
        payload = df.to_dict(orient='records')
        payload_json = json.dumps(payload)
        self.client.publishAsync(topic, payload_json, 0)

    def connect(self):
        # Connect the client to the MQTT broker
        self.client.connect()

    def disconnect(self):
        # Disconnect the client
        self.client.disconnect()


# Create and initialize the MQTT client
device_id = 0  # Modify device_id as needed
client = MQTTClient(device_id, certificate.format(device_id), key.format(device_id))

# Connect the client
print("Connecting to MQTT broker...")
client.connect()

# Subscribe to the desired topic
client.subscribe("vehicle/emission/data")

# Keep the script running to listen for messages
print("Waiting for messages... (Press Ctrl+C to exit)")
while True:
    time.sleep(1)
