import boto3

iot_client = boto3.client('iot')

device_st = 0
device_end = 10
policy_name = 'part_policy'
thing_group_name = 'thing_group'

for device_id in range(device_st, device_end):
    thing_name = f"device_{device_id}"
    create_response = iot_client.create_thing(thingName=thing_name)
    key_response = iot_client.create_keys_and_certificate(setAsActive=True)
    certificate_arn = key_response['certificateArn']    
    attach_response = iot_client.attach_policy(policyName=policy_name, target=certificate_arn)
    principal_response = iot_client.attach_thing_principal(thingName=thing_name, principal=certificate_arn)
    group_response = iot_client.add_thing_to_thing_group(thingName=thing_name, thingGroupName=thing_group_name)
    with open(f"./cert/certificate_{device_id}.pem", "w") as cert_file:
        cert_file.write(key_response['certificatePem'])
    with open(f"./cert/device_{device_id}.private.pem", "w") as private_key_file:
        private_key_file.write(key_response['keyPair']['PrivateKey'])
    print(f"Made device {device_id}")