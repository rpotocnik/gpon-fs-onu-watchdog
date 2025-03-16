#!/usr/bin/python3

import paramiko
import time
import re  # Added for regex parsing

# Configuration
ONU_IP = '192.168.1.10'  # Replace with the ONU module's IP address
ONU_USERNAME = 'redacteduser'  # Replace with the ONU module's SSH username
ONU_PASSWORD = 'redactedpassword'  # Replace with the ONU's SSH password
GPON_COMMAND = '/opt/lantiq/bin/onu ploamsg'  # Update this path if needed
GPON_UP_STATE = 5
CHECK_INTERVAL = 60  # In seconds, how often to check the state
MAX_ATTEMPTS = 5  # Number of consecutive attempts to check the state

def check_gpon_state():
    try:
        print(f"Connecting to ONU at {ONU_IP}...")  # Debugging output

        # Setup SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the ONU via SSH
        print(f"Attempting SSH connection with user: {ONU_USERNAME}")  # Debugging output
        ssh.connect(ONU_IP, username=ONU_USERNAME, password=ONU_PASSWORD)

        # Run the command to check GPON state
        print(f"Running command: {GPON_COMMAND}")  # Debugging output
        stdin, stdout, stderr = ssh.exec_command(GPON_COMMAND)
        output = stdout.read().decode('utf-8')

        # Print the output to see the result
        print(f"GPON Command Output: {output}")  # Debugging output

        # Use regex to extract curr_state value
        match = re.search(r'curr_state=(\d+)', output)
        if match:
            curr_state = int(match.group(1))
        else:
            print(f"Error: curr_state not found in output: {output}")
            curr_state = None

        # Close the SSH connection
        ssh.close()

        print(f"GPON current state: {curr_state}")  # Debugging output
        return curr_state

    except Exception as e:
        print(f"Error connecting to ONU: {e}")
        return None


def reboot_onu():
    try:
        print(f"Rebooting ONU at {ONU_IP}...")  # Debugging output

        # Setup SSH client for rebooting
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the ONU via SSH
        ssh.connect(ONU_IP, username=ONU_USERNAME, password=ONU_PASSWORD)

        # Send reboot command
#        reboot_command = 'reboot'  # Assuming 'reboot' is the correct command for the ONU
#        print(f"Sending reboot command: {reboot_command}")  # Debugging output
#        ssh.exec_command(reboot_command)

        print("Rebooting ONU...")  # Debugging output
        ssh.close()

    except Exception as e:
        print(f"Error during reboot: {e}")


def monitor_gpon():
    consecutive_failed_checks = 0
    print(f"Monitoring GPON state for ONU at {ONU_IP} every {CHECK_INTERVAL} seconds...")  # Debugging output

    while True:
        print(f"Checking GPON state...")  # Debugging output
        curr_state = check_gpon_state()

        if curr_state == GPON_UP_STATE:
            print(f"GPON is up. State: {curr_state}")  # Debugging output
            consecutive_failed_checks = 0
        else:
            print(f"GPON is down or in error. State: {curr_state}")  # Debugging output
            consecutive_failed_checks += 1

            if consecutive_failed_checks >= MAX_ATTEMPTS:
                print(f"GPON has been down for {MAX_ATTEMPTS} checks. Rebooting ONU...")  # Debugging output
                reboot_onu()
                consecutive_failed_checks = 0

        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    monitor_gpon()
