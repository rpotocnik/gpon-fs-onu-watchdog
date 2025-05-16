#!/usr/bin/python3

import os
import paramiko
import time
import re
import logging

# Configuration
ONU_IP = os.getenv('ONU_IP', '192.168.1.10')  # Replace with the ONU module's IP address
ONU_USERNAME = os.getenv('ONU_USERNAME', 'ONTUSER')  # Replace with the ONU module's SSH username
ONU_PASSWORD = os.getenv('ONU_PASSWORD', '7sp!lwUBz1')  # Replace with the ONU's SSH password
GPON_COMMAND = os.getenv('GPON_COMMAND', '/opt/lantiq/bin/onu ploamsg')  # Update this path if needed
GPON_UP_STATE = int(os.getenv('GPON_UP_STATE', 5))
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 60))  # In seconds, how often to check the state
MAX_ATTEMPTS = int(os.getenv('MAX_ATTEMPTS', 2))  # Number of consecutive attempts to check the state

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def check_gpon_state():
    try:
        logging.info(f"Connecting to ONU at {ONU_IP}...")  # Debugging output

        # Setup SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the ONU via SSH
        logging.info(f"Attempting SSH connection with user: {ONU_USERNAME}")  # Debugging output
        ssh.connect(ONU_IP, username=ONU_USERNAME, password=ONU_PASSWORD)

        # Run the command to check GPON state
        logging.info(f"Running command: {GPON_COMMAND}")  # Debugging output
        stdin, stdout, stderr = ssh.exec_command(GPON_COMMAND)
        output = stdout.read().decode('utf-8')

        # Print the output to see the result
        logging.info(f"GPON Command Output: {output}")  # Debugging output

        # Use regex to extract curr_state value
        match = re.search(r'curr_state=(\d+)', output)
        if match:
            curr_state = int(match.group(1))
        else:
            logging.info(f"Error: curr_state not found in output: {output}")
            curr_state = None

        # Close the SSH connection
        ssh.close()

        logging.info(f"GPON current state: {curr_state}")  # Debugging output
        return curr_state

    except Exception as e:
        logging.info(f"Error connecting to ONU: {e}")
        return None


def reboot_onu():
    try:
        logging.info(f"Rebooting ONU at {ONU_IP}...")  # Debugging output

        # Setup SSH client for rebooting
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the ONU via SSH
        ssh.connect(ONU_IP, username=ONU_USERNAME, password=ONU_PASSWORD)

        # Send reboot command
        reboot_command = '/sbin/reboot'  # Assuming 'reboot' is the correct command for the ONU
        logging.info(f"Sending reboot command: {reboot_command}")  # Debugging output
        ssh.exec_command(reboot_command)

        logging.info("Rebooting ONU...")  # Debugging output
        ssh.close()

    except Exception as e:
        logging.info(f"Error during reboot: {e}")


def monitor_gpon():
    consecutive_failed_checks = 0
    logging.info(f"Monitoring GPON state for ONU at {ONU_IP} every {CHECK_INTERVAL} seconds...")  # Debugging output

    while True:
        logging.info(f"Checking GPON state...")  # Debugging output
        curr_state = check_gpon_state()

        if curr_state == GPON_UP_STATE:
            logging.info(f"GPON is up. State: {curr_state}")  # Debugging output
            consecutive_failed_checks = 0
        else:
            logging.info(f"GPON is down or in error. State: {curr_state}")  # Debugging output
            consecutive_failed_checks += 1

            if consecutive_failed_checks >= MAX_ATTEMPTS:
                logging.info(f"GPON has been down for {MAX_ATTEMPTS} checks. Rebooting ONU...")  # Debugging output
                reboot_onu()
                consecutive_failed_checks = 0

        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    monitor_gpon()

