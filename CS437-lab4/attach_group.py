import boto3

# Initialize the Greengrass client
greengrass_client = boto3.client('greengrass', region_name='us-east-2')  # e.g., 'us-west-2'
iot_client = boto3.client('iot', region_name='us-east-2')  # Same region as your Greengrass

# Replace with your Greengrass Group ID and IoT Thing Names
GREENGRASS_GROUP_ID = 'e2eedb55-8df6-4984-a8c6-6f5d3644c607'
DEVICE_NAMES = ['device_0', 'device_1', 'device_2', 'device_3', 'device_4', 'device_5', 'device_6', 'device_7', 'device_8', 'device_9', ]  # List of IoT Thing Names

def get_core_definition_version_id(group_id):
    response = greengrass_client.get_group(
        GroupId=group_id
    )
    core_definition_id = response['LatestVersion']['CoreDefinitionVersionArn'].split('/')[-1]
    return core_definition_id

def add_devices_to_greengrass_group(group_id, device_names):
    # Step 1: Get the latest device definition version ID
    response = greengrass_client.get_group(
        GroupId=group_id
    )
    latest_device_def_version = response['LatestVersion']['DeviceDefinitionVersionArn'].split('/')[-1]
    device_definition_id = response['LatestVersion']['DeviceDefinitionId']
    
    # Step 2: Prepare devices list with their ARNs
    devices = []
    for device_name in device_names:
        # Retrieve the IoT Thing ARN
        thing_arn = iot_client.describe_thing(
            thingName=device_name
        )['thingArn']
        
        devices.append({
            'Id': device_name,               # Unique ID for each device in Greengrass
            'ThingArn': thing_arn,           # IoT Thing ARN
            'CertificateArn': thing_arn,     # Attach the same certificate ARN if they use a shared one
            'SyncShadow': True               # Set to True if the device should sync its shadow
        })
    
    # Step 3: Create a new version for the device definition with the updated list of devices
    response = greengrass_client.create_device_definition_version(
        DeviceDefinitionId=device_definition_id,
        Devices=devices
    )
    device_definition_version_id = response['Version']
    print(f"Created new device definition version ID: {device_definition_version_id}")

    # Step 4: Deploy the new version to the Greengrass Group
    greengrass_client.create_deployment(
        DeploymentType='NewDeployment',
        GroupId=group_id,
        GroupVersionId=latest_device_def_version
    )
    print(f"Devices successfully connected to Greengrass Group '{group_id}'.")

# Run the function
add_devices_to_greengrass_group(GREENGRASS_GROUP_ID, DEVICE_NAMES)
