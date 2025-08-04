# API client for making requests
import requests
import logging
from urllib.parse import urljoin

# Assuming config.py is accessible (adjust import path if needed)
try:
    import config
except ModuleNotFoundError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..')) # Add project root to path
    import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ApiClient:
    """Client for interacting with the BEST API."""

    def __init__(self, access_token: str):
        """
        Initializes the API client.

        Args:
            access_token: The OAuth 2.0 access token for authentication.
        """
        if not access_token:
            raise ValueError("Access token cannot be empty.")
        self.base_url = config.API_BASE_URL
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json' # Assuming JSON responses
            # Add other common headers if necessary
            # 'Content-Type': 'application/json' # Needed for POST/PUT/PATCH
        }
        logging.info("ApiClient initialized.")

    def _make_request(self, method: str, endpoint_path: str, params: dict = None, json_data: dict = None) -> dict | list:
        """
        Makes an HTTP request to the API.

        Args:
            method: HTTP method (e.g., 'GET', 'POST', 'PUT', 'PATCH').
            endpoint_path: Relative path of the API endpoint (e.g., '/AcademicTerm').
                           Can also be a full URL if needed (e.g., for WLoads template).
            params: Optional dictionary of query parameters for GET requests.
            json_data: Optional dictionary for the JSON body of POST/PUT/PATCH requests.

        Returns:
            The JSON response from the API as a dictionary or list.

        Raises:
            requests.exceptions.RequestException: For connection errors or HTTP error statuses.
            ValueError: If the response is not valid JSON.
        """
        # Construct the full URL safely
        # Check if endpoint_path is already a full URL
        if endpoint_path.startswith(('http://', 'https://')):
            full_url = endpoint_path
        else:
            # Ensure endpoint_path starts with '/' if it's relative
            if not endpoint_path.startswith('/'):
                endpoint_path = '/' + endpoint_path
            full_url = urljoin(self.base_url.rstrip('/') + '/', endpoint_path.lstrip('/'))


        request_headers = self.headers.copy()
        if json_data:
            # Add Content-Type header only if sending JSON data
            request_headers['Content-Type'] = 'application/json'

        try:
            logging.debug(f"Making {method} request to {full_url} with params={params}, data={json_data}")
            response = requests.request(
                method,
                full_url,
                headers=request_headers,
                params=params,
                json=json_data,
                timeout=30 # Add a reasonable timeout
            )
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            # Check if response body is empty before trying to parse JSON
            if not response.content:
                logging.warning(f"Received empty response body from {full_url}")
                return {} # Return empty dict for empty successful responses (adjust if list is expected)

            return response.json()

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err} - Status: {http_err.response.status_code}")
            logging.error(f"Response body: {http_err.response.text}")
            raise
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Connection error occurred: {conn_err}")
            raise
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout error occurred: {timeout_err}")
            raise
        except requests.exceptions.RequestException as req_err:
            logging.error(f"An unexpected request error occurred: {req_err}")
            raise
        except ValueError as json_err: # Catches JSONDecodeError
            logging.error(f"Failed to decode JSON response from {full_url}: {json_err}")
            logging.error(f"Response text: {response.text}")
            raise ValueError(f"Invalid JSON received from {full_url}") from json_err

    def get_data(self, endpoint_path: str, params: dict = None) -> dict | list:
        """
        Fetches data from a specific API endpoint using GET.

        Args:
            endpoint_path: Relative path of the API endpoint (e.g., '/AcademicTerm')
                           or a full URL.
            params: Optional dictionary of query parameters.

        Returns:
            The JSON response from the API (can be a dict or a list).
        """
        # logging.info(f"Fetching data from endpoint: {endpoint_path} with params: {params}")
        # The response could be a list (e.g., /all endpoint) or a dict
        response_data = self._make_request('GET', endpoint_path, params=params)
        return response_data

    def search_data(self, endpoint_path: str, json_payload: dict) -> dict | list:
        """
        Sends a search request to a specific API endpoint using POST with a JSON payload.

        Args:
            endpoint_path: Relative path of the API endpoint (e.g., '/AcademicTerm/search').
            json_payload: The dictionary representing the JSON body for the search request.

        Returns:
            The JSON response from the API (can be a dict or a list).
        """
        logging.info(f"Searching data at endpoint: {endpoint_path} with payload: {json_payload}")
        # The response could be a list (search results) or a dict
        response_data = self._make_request('POST', endpoint_path, json_data=json_payload)
        return response_data

    # --- Methods for updating data will be added later ---
    # def update_event_data(self, payload: dict) -> dict:
    #     """ Sends data to the /Event endpoint (using POST/PUT/PATCH). """
    #     method = 'POST' # Or PUT/PATCH based on API spec
    #     logging.info(f"Sending data to destination endpoint: {config.DESTINATION_ENDPOINT}")
    #     return self._make_request(method, config.DESTINATION_ENDPOINT, json_data=payload) 