import logging
from datetime import datetime

import requests


class NotAuthenticatedException(Exception):
    pass


class NoSuccessfulResponse(Exception):
    pass


class MawaqitClient:

    def __init__(self, latitude: float, longitude: float, username: str, password: str):
        self.base_url = "https://mawaqit.net/api/2.0"
        self.me_url = f"{self.base_url}/me"
        self.mosque_search_url = f"{self.base_url}/mosque/search"
        self.prayer_times_url = self.base_url + "/mosque/{mosque_id}/prayer-times"
        self.username = username
        self.password = password
        self.latitude = latitude
        self.longitude = longitude
        self.mosquee = None
        self.headers = {
            "Api-Access-Token": "",
            "Content-Type": "application/json",
        }

    def get_api_access_token(self):
        """Retrieves the API access token using basic authentication."""

        auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        response = requests.get(self.me_url, auth=auth)

        if response.status_code != 200:
            if response.status_code == 401:
                logging.error(f"Authentication failed {response.status_code}")
                raise NotAuthenticatedException("Authentication falled")
            logging.error(f"Failed to get API access token {response.status_code}")
            raise NoSuccessfulResponse("Failed to get API access token")

        data = response.json()
        return data["apiAccessToken"]

    def all_mosques_neighborhood(self):
        """
        Gets all mosques in the neighborhood of the given latitude and longitude.

        :return: a list of mosques in the neighborhood
        :raises: NoSuccessfulResponse if the API call fails
        """
        if self.headers["Api-Access-Token"] == "":
            self.headers["Api-Access-Token"] = self.get_api_access_token()
        payload = {"lat": self.latitude, "lon": self.longitude}
        with requests.get(
            self.mosque_search_url, params=payload, data=None, headers=self.headers
        ) as response:
            if response.status_code != 200:
                logging.error(f"Failed to get mosques {response.status_code}")
                raise NoSuccessfulResponse("Failed to get mosques")
            return response.json()

    def fetch_prayer_times(self) -> list[str]:
        """
        Fetches the prayer times of the closest mosque to the user.

        :return: a list of prayer times as strings in format "HH:MM"
        :raises: NoSuccessfulResponse if the API call fails
        """
        mosque = self.all_mosques_neighborhood()[0]
        mosque_id = mosque["uuid"]

        if self.headers["Api-Access-Token"] == "":
            self.headers["Api-Access-Token"] = self.get_api_access_token()

        with requests.get(
            self.prayer_times_url.format(mosque_id=mosque_id),
            data=None,
            headers=self.headers,
        ) as response:
            if response.status_code != 200:
                logging.error(f"Failed to get prayer times {response.status_code}")
                raise NoSuccessfulResponse("Failed to get prayer times")
            return response.json()
