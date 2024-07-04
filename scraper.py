import json
import os
import requests
import time
import logging

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\u001b[35m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Set up logging
logging.basicConfig(filename='fetching.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Base directory for orders
orders_dir = 'all_orders'

# Ensure the base directory exists
if not os.path.exists(orders_dir):
    os.makedirs(orders_dir)
    print(f"{bcolors.OKGREEN}Created directory: {orders_dir}{bcolors.ENDC}")
    logging.info(f"Created directory: {orders_dir}")
else:
    print(f"{bcolors.OKBLUE}Directory already exists: {orders_dir}{bcolors.ENDC}")
    logging.info(f"Directory already exists: {orders_dir}")

# Load headers from config file
with open('config.json') as config_file:
    config = json.load(config_file)
    print(f"{bcolors.OKGREEN}Loaded configuration from 'config.json'{bcolors.ENDC}")
    logging.info("Loaded configuration from 'config.json'")

base_url = "https://apirest.3dcart.com/3dCartWebAPI/v1/Orders"
headers = {
    'SecureURL': config['SecureURL'],
    'PrivateKey': config['PrivateKey'],
    'Token': config['Token']
}

batch_size = 200
max_retries = 2

def fetch_all_orders():
    checkpoint_file = 'checkpoint.json'
    
    # Initialize or load checkpoint
    if os.path.isfile(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
        offset = checkpoint['offset']
        batch_number = checkpoint['batch_number']
        print(f"{bcolors.OKBLUE}Resuming from checkpoint: offset={offset}, batch_number={batch_number}{bcolors.ENDC}")
        logging.info(f"Resuming from checkpoint: offset={offset}, batch_number={batch_number}")
    else:
        offset = 0
        batch_number = 1
        print(f"{bcolors.WARNING}No checkpoint found. Starting from the beginning.{bcolors.ENDC}")
        logging.info("No checkpoint found. Starting from the beginning.")

    more_orders = True

    while more_orders:
        print(f"{bcolors.HEADER}Fetching batch {batch_number}...{bcolors.ENDC}")
        logging.info(f"Fetching batch {batch_number}...")
        
        # Construct the URL for the API request
        url = f"{base_url}?limit={batch_size}&offset={offset}"
        print(f"{bcolors.OKCYAN}API URL: {url}{bcolors.ENDC}")
        logging.info(f"API URL: {url}")
        
        success = False
        retries = 0

        # Try fetching data from the API, with a retry mechanism
        while not success and retries < max_retries:
            try:
                response = requests.request("GET", url, headers=headers)
                response.raise_for_status()
                success = True
                print(f"{bcolors.OKGREEN}Successfully fetched data from {url}{bcolors.ENDC}")
                logging.info(f"Successfully fetched data from {url}")
            except requests.exceptions.RequestException as e:
                print(f"{bcolors.FAIL}Error fetching data: {str(e)}{bcolors.ENDC}")
                logging.error(f"Error fetching data: {str(e)}")
                print(f"{bcolors.WARNING}Retrying...{bcolors.ENDC}")
                logging.info("Retrying...")
                retries += 1
                time.sleep(10)

        # Break the loop if unable to fetch data after multiple retries
        if not success:
            print(f"{bcolors.FAIL}Failed to fetch data after multiple retries.{bcolors.ENDC}")
            logging.error("Failed to fetch data after multiple retries.")
            return False  # Indicate failure to the main loop

        # Process the fetched data
        orders = response.json()
        if orders:
            # Save the fetched orders to a JSON file
            file_path = os.path.join(orders_dir, f'orders_batch_{batch_number}.json')
            with open(file_path, 'w') as f:
                json.dump(orders, f, indent=4)
            print(f"{bcolors.OKGREEN}Batch {batch_number} orders saved to {file_path}{bcolors.ENDC}")
            logging.info(f"Batch {batch_number} orders saved to {file_path}")

            # Save the checkpoint
            checkpoint = {
                'offset': offset + batch_size,
                'batch_number': batch_number + 1
            }
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint, f)
            print(f"{bcolors.OKBLUE}Checkpoint saved: offset={checkpoint['offset']}, batch_number={checkpoint['batch_number']}{bcolors.ENDC}")
            logging.info(f"Checkpoint saved: offset={checkpoint['offset']}, batch_number={checkpoint['batch_number']}")

            offset += batch_size
            batch_number += 1
            # Check if the number of orders fetched is less than the batch size
            if len(orders) < batch_size:
                more_orders = False
                print(f"{bcolors.WARNING}No more orders to fetch.{bcolors.ENDC}")
                logging.info(f"No more orders to fetch.")
            else:
                print(f"{bcolors.OKBLUE}More orders to fetch. Continuing...{bcolors.ENDC}")
                logging.info(f"More orders to fetch. Continuing...")
        else:
            more_orders = False
            print(f"{bcolors.WARNING}No orders found in the current batch.{bcolors.ENDC}")
            logging.info(f"No orders found in the current batch.")

    print(f"{bcolors.OKGREEN}All orders processed. Fetching completed.{bcolors.ENDC}")
    logging.info("All orders processed. Fetching completed.")
    return True  # Indicate successful completion

max_restarts = 10
restart_count = 0

while restart_count < max_restarts:
    try:
        print(f"{bcolors.HEADER}Starting to fetch all orders... (Attempt {restart_count + 1}/{max_restarts}){bcolors.ENDC}")
        logging.info(f"Starting to fetch all orders... (Attempt {restart_count + 1}/{max_restarts})")
        success = fetch_all_orders()
        if success:
            print(f"{bcolors.OKGREEN}Fetch operation completed successfully for all orders.{bcolors.ENDC}")
            logging.info("Fetch operation completed successfully for all orders.")
            break  # Exit the loop if all orders are processed successfully
        else:
            print(f"{bcolors.WARNING}Fetch operation failed. Will retry after waiting period.{bcolors.ENDC}")
            logging.info("Fetch operation failed. Will retry after waiting period.")
    except Exception as e:
        print(f"{bcolors.FAIL}An error occurred: {str(e)}{bcolors.ENDC}")
        logging.error(f"An error occurred: {str(e)}")
    
    restart_count += 1
    if restart_count < max_restarts:
        print(f"{bcolors.WARNING}Waiting for 10 minutes before restarting... (Restart {restart_count}/{max_restarts}){bcolors.ENDC}")
        logging.info(f"Waiting for 10 minutes before restarting... (Restart {restart_count}/{max_restarts})")
        time.sleep(600)  # Wait for 10 minutes (600 seconds)
        print(f"{bcolors.HEADER}Restarting the script...{bcolors.ENDC}")
        logging.info("Restarting the script...")
    else:
        print(f"{bcolors.FAIL}Maximum number of restarts ({max_restarts}) reached. Stopping the script.{bcolors.ENDC}")
        logging.error(f"Maximum number of restarts ({max_restarts}) reached. Stopping the script.")

if restart_count == max_restarts:
    print(f"{bcolors.FAIL}Scraping stopped due to too many restart attempts.{bcolors.ENDC}")
    logging.error("Scraping stopped due to too many restart attempts.")
else:
    print(f"{bcolors.OKGREEN}Scraping Completed Successfully{bcolors.ENDC}")
    logging.info("Scraping Completed Successfully")
