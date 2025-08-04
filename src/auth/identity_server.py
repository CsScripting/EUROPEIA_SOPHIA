# Authentication logic for Identity Server
import requests
import logging
# Assuming config.py is in the parent directory relative to where the script using this module might run from
# Or adjust the import based on your execution context and project structure
try:
    import config
except ModuleNotFoundError:
    # Handle case where config might be relative to src directory if running tests/scripts from root
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..')) # Add project root to path
    import config


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_access_token():
    """Fetches the access token from the Identity Server using Password Credentials Grant."""

    payload = {
        'grant_type': 'password',
        'username': config.USERNAME,
        'password': config.PASSWORD,
        'client_id': config.CLIENT_ID,
        'client_secret': config.CLIENT_SECRET,
    }

    # Add scope if it's defined in config and not None or empty
    # Uncomment the following line in config.py if scope is needed
    # if hasattr(config, 'SCOPE') and config.SCOPE:
    #     payload['scope'] = config.SCOPE

    try:
        logging.info(f"Requesting access token from {config.IDENTITY_SERVER_URL}")
        response = requests.post(
            config.IDENTITY_SERVER_URL,
            data=payload,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses (4XX or 5XX)

        token_data = response.json()

        if 'access_token' in token_data:
            logging.info("Successfully obtained access token.")
            return token_data['access_token']
        else:
            logging.error("Access token not found in response.")
            logging.error(f"Response data: {token_data}")
            raise ValueError("Access token not found in response from Identity Server.")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error requesting access token: {e}")
        # Log response body if available for more context
        if e.response is not None:
            logging.error(f"Response status code: {e.response.status_code}")
            logging.error(f"Response body: {e.response.text}")
        raise ConnectionError(f"Could not connect to Identity Server or failed to get token: {e}") from e
    except ValueError as e:
        # Catch JSON decoding errors or the ValueError raised above
        logging.error(f"Error processing token response: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred during authentication: {e}")
        raise

# Example usage (for testing purposes)
if __name__ == '__main__':
    try:
        # Make sure to replace placeholder values in config.py before running this
        if "YOUR_" in config.IDENTITY_SERVER_URL or \
           "YOUR_" in config.CLIENT_ID or \
           "YOUR_" in config.CLIENT_SECRET or \
           "YOUR_" in config.USERNAME or \
           "YOUR_" in config.PASSWORD:
            print("Please replace placeholder values in config.py before running the example.")
        else:
            token = get_access_token()
            print(f"Access Token: {token[:10]}...{token[-5:]}") # Print truncated token for verification
    except (ValueError, ConnectionError, Exception) as e:
        print(f"Failed to get token: {e}") 