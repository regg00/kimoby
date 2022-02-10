from lib2to3.pgen2 import token
import logging
from tkinter import NO
from urllib.parse import urljoin
import requests
from datetime import datetime
from pprint import pprint
import os
import phonenumbers
import json


class Kimoby:
    def __init__(
        self,
        api_key,
        api_secret,
        log_level="INFO",
        version="1",
        host="api.kimoby.com",
    ):
        """Python class to interrogate the Kimoby REST API.
        Each call to the API is returned as a Python dict.

        Args:
            token (str): Kimoby API key.
            log_level (str, optional): Log level. Defaults is "INFO".
            version (str, optional): Version of the API to use. Defaults is 1.
            host (str, optional): Kimoby API host. Defaults is api.kimoby.com.
        """
        self.headers = {"Content-type": "application/json"}
        self.base_url = f"https://{host}/v{version}"

        self.api_key = api_key
        self.api_secret = api_secret

        self.logger = logging.getLogger("default")
        self.logger.setLevel(logging.getLevelName(log_level))
        formatter = logging.Formatter(
            "%(asctime)s - %(funcName)s - %(levelname)s - %(message)s"
        )
        ch = logging.StreamHandler()

        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def format_phone_number(self, phone_number):
        return phonenumbers.format_number(
            phonenumbers.parse(phone_number, "US"), phonenumbers.PhoneNumberFormat.E164
        )

    def make_request(self, method, path, parameters=None, body=None):
        """Function to standardize requests made to the API.

        Args:
            method (str): Method to use. GET, POST, etc.
            path (str): API path to query.
            parameters (dict, optional): Parameters to pass the queried path. See the official API documentation here: https://api-doc.kimoby.com/
        """
        url = self.base_url + path
        params = {}

        self.logger.debug(f"{method}\t{url}")

        s = requests.Session()
        if parameters is not None:
            params.update(parameters)
        if body is not None:
            body_json = json.dumps(body)
            response = s.request(
                method,
                url,
                headers=self.headers,
                params=params,
                auth=(self.api_key, self.api_secret),
                data=body_json,
            )
        else:
            response = s.request(
                method,
                url,
                headers=self.headers,
                params=params,
                auth=(self.api_key, self.api_secret),
            )

        if response.ok:
            if response.status_code != 204:
                return response.json()
        elif response.content:
            raise Exception(
                str(response.status_code)
                + ": "
                + response.reason
                + ": "
                + str(response.content)
            )
        else:
            raise Exception(str(response.status_code) + ": " + response.reason)

    def get_customers(self, params=None):
        """List all customers. It matches the customers JSON schema here: https://api-doc.kimoby.com/json-schemas/customers.json

        Args:
            params (dict, optional): Parameters to pass the queried path. See the official API documentation here: https://api-doc.kimoby.com/
        """
        return self.make_request("GET", "/customers", params)

    def get_customer(self, id=None, reference=None, cell_phone_number=None):
        """Retrieve a customer. It matches the customers JSON schema here: https://api-doc.kimoby.com/json-schemas/customers.json

        Args:
            id (string, optional): The id generated by Kimoby
            reference (string, optional): Unique string identifier used in your system.
            cell_phone_number (string, optional): The cell phone number of the customer in E.164 format.
            params (dict, optional): Parameters to pass the queried path. See the official API documentation here: https://api-doc.kimoby.com/
        """
        params = ""
        if id:
            params = {"id": id}
        if reference:
            params = {"reference": reference}
        if cell_phone_number:
            params = {"cell_phone_number": self.format_phone_number(cell_phone_number)}
        return self.make_request("GET", "/customers/", params)

    def create_customer(self, payload):
        """Create a customer.

        To create a customer, send the customer attributes in JSON in the payload of the request. Only the name is required, all other attributes of the Customer Model are optional.
        If there is a validation error it will be returned in JSON as mentioned in the Error Section, otherwise, the customer will be returned.

        Args:
            params (dict, optional): Parameters to pass the queried path. See the official API documentation here: https://api-doc.kimoby.com/
        """
        return self.make_request("PUT", "/customers", body=payload)

    def delete_customer(self, id=None, reference=None, cell_phone_number=None):
        """Delete a customer.

        Args:
            id (string, optional): The id generated by Kimoby
            reference (string, optional): Unique string identifier used in your system.
            cell_phone_number (string, optional): The cell phone number of the customer in E.164 format.
            params (dict, optional): Parameters to pass the queried path. See the official API documentation here: https://api-doc.kimoby.com/
        """
        params = ""
        if id:
            params = {"id": id}
        if reference:
            params = {"reference": reference}
        if cell_phone_number:
            params = {"cell_phone_number": self.format_phone_number(cell_phone_number)}
        return self.make_request("DELETE", "/customers/", params)

    # TODO: Seems that this API endpoint create a new customer instead of updating it.
    def update_customer(
        self, id=None, reference=None, cell_phone_number=None, payload=None
    ):
        """Retrieve a customer. It matches the customers JSON schema here: https://api-doc.kimoby.com/json-schemas/customers.json

        Args:
            payload (dict): The new information for the specified customer.
            id (string, optional): The id generated by Kimoby
            reference (string, optional): Unique string identifier used in your system.
            cell_phone_number (string, optional): The cell phone number of the customer in E.164 format.
            params (dict, optional): Parameters to pass the queried path. See the official API documentation here: https://api-doc.kimoby.com/
        """
        params = ""
        if id:
            params = {"id": id}
        if reference:
            params = {"reference": reference}
        if cell_phone_number:
            params = {"cell_phone_number": self.format_phone_number(cell_phone_number)}
        return self.make_request("PUT", "/customers/", parameters=params, body=payload)

    def send_message(self, payload):
        """Send a message to a customer. It matches the customers JSON schema here: https://api-doc.kimoby.com/json-schemas/customers.json

        Args:
            payload (dict): The message to send as dict. See: https://api-doc.kimoby.com/#messages2_message_sendhtml
        """
        return self.make_request("POST", "/messages/", body=payload)