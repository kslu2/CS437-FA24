import csv
import logging

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_csv(input_file, output_file):
    try:
        # Read and parse the CSV file
        vehicle_data = []
        with open(input_file, mode='r') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                vehicle_data.append(row)

        # Calculate max CO2 emission
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

        # Write the result to a new CSV file
        with open(output_file, mode='w', newline='') as outfile:
            fieldnames = ['vehicle_id', 'max_CO2']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'vehicle_id': vehicle_id, 'max_CO2': max_CO2})

        logger.info(f"Max CO2 emission for vehicle {vehicle_id}: {max_CO2} saved to {output_file}")

    except Exception as e:
        logger.error(f"Error processing CSV file: {e}")

# Example usage
input_file = './csv_data/vehicle4.csv'  # Input CSV file
output_file = './csv_data/max/vehicle4_max.csv'  # Output CSV file

process_csv(input_file, output_file)
