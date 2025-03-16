# FS.com ONU stick watchdog

The python script connects to a FS.com ONU stick via SSH and runs "onu ploamsg" command. In case GPON isn't running - isn't in O5 (Operation) for consecutive 5 attempts it reboots the module.
I got all the info on [Hack GPON](https://hack-gpon.org/ont-fs-com-gpon-onu-stick-with-mac/)

You should change the default values and provide your own

ONU_IP = '192.168.1.10'  # Replace with the ONU module's IP address
ONU_USERNAME = 'ONTUSER'  # Replace with the ONU module's SSH username
ONU_PASSWORD = 'redactedpassword'  # Replace with the ONU's SSH password
GPON_COMMAND = '/opt/lantiq/bin/onu ploamsg'  # Update this path if needed
GPON_UP_STATE = 5
CHECK_INTERVAL = 60  # In seconds, how often to check the state
MAX_ATTEMPTS = 5  # Number of consecutive attempts to check the state
