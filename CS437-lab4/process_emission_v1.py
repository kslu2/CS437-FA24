import json
import logging
import sys
import csv
from io import StringIO

import greengrasssdk

# Logging
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# SDK Client
client = greengrasssdk.client("iot-data")

def lambda_handler(event, context):
    try:
        # TODO1: Parse the CSV data
        vehicle_data = []
        for record in event:
            csv_content = record.get("csv_data")
            if not csv_content:
                logger.warning("Missing CSV data in event record.")
                continue
            
            try:
                # Parse CSV data into a list of dictionaries
                csv_file = StringIO(csv_content)
                reader = csv.DictReader(csv_file)
                for row in reader:
                    vehicle_data.append(row)
            except Exception as e:
                logger.error(f"Failed to parse CSV data: {e}")
                continue

        # TODO2: Calculate max CO2 emission
        max_CO2 = 0.0
        vehicle_id = None
        for row in vehicle_data:
            try:
                CO2_val = float(row['vehicle_CO2'])
                current_vehicle_id = row['vehicle_id']

                if CO2_val > max_CO2:
                    max_CO2 = CO2_val
                    vehicle_id = current_vehicle_id
            except KeyError as e:
                logger.error(f"Missing key in CSV row: {e}")
            except ValueError as e:
                logger.error(f"Invalid CO2 value in CSV row: {e}")

        if vehicle_id is None:
            logger.error("No valid vehicle data found.")
            return

        # TODO3: Publish the result
        client.publish(
            topic="vehicle/emission/processed",
            queueFullPolicy="AllOrException",
            payload=json.dumps({"vehicle_id": vehicle_id, "max_CO2": max_CO2}),
        )
        logger.info(f"Published max CO2 for vehicle {vehicle_id}: {max_CO2}")

    except Exception as e:
        logger.error(f"Error processing event: {e}")

    return
