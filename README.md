# 3dcart/Shift4Shop Order Fetching Script

This Python script fetches all orders from a 3dcart store using the 3dcart API. It retrieves orders in batches and saves them as JSON files. 

## Features

- Fetches all orders from a 3dcart store
- Processes orders in batches (default 200 orders per batch)
- Implements checkpointing for resume capability
- Includes error handling and automatic retries
- Provides detailed logging
- Implements a restart mechanism for improved resilience

## Prerequisites

- Python 3.6 or higher
- `requests` library

## Setup

1. Clone this repository or download the script.

2. Install the required Python library:

   ```
   pip install requests
   ```

3. Create a `config.json` file in the same directory as the script with your 3dcart API credentials:
   You need to set up an account in the dev portal for this. 

   ```json
   {
     "SecureURL": "your_store_url",
     "PrivateKey": "your_private_key",
     "Token": "your_token"
   }
   ```

   Replace `your_store_url`, `your_private_key`, and `your_token` with your actual 3dcart API credentials.

## Usage

Run the script using Python:

```
python order_fetching_script.py
```

The script will start fetching orders and save them in JSON files in the `all_orders` directory. Each file will contain a batch of orders (default 200 orders per file).

## Output

- Order data is saved in the `all_orders` directory.
- Each batch of orders is saved as a separate JSON file named `orders_batch_X.json`, where X is the batch number.
- A log file `fetching.log` is created, containing detailed information about the script's execution.

## Checkpointing

The script uses a checkpoint system to allow for resuming the fetch operation if it's interrupted. The checkpoint information is stored in a `checkpoint.json` file.

## Error Handling

The script includes error handling and will attempt to retry failed requests. If persistent errors occur, the script will restart up to 10 times, with a 10-minute wait between restarts.

## Customization

You can modify the following variables in the script to customize its behavior:

- `batch_size`: Number of orders to fetch in each batch (default: 200)
- `max_retries`: Maximum number of retry attempts for a failed request (default: 2)
- `max_restarts`: Maximum number of script restarts on persistent failures (default: 10)

## Support

For any issues or questions, please open an issue or contact me directly. The documentation for the API is not up to date so most of this was made by trial & error, so if you look at the official doc vs this code you will see conflicts. 

## Disclaimer

This script is provided as-is. Please ensure you comply with 3dcart's API usage policies and rate limits when using this script.
