import http.server
import json
import logging
import os
import pickle
import socketserver
import threading
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv

from helper.chrome import cast_to_chromecast, get_chromecast_device
from helper.mawaqit import MawaqitClient

logging.basicConfig(level=logging.INFO)
load_dotenv()

config = {
    "latitude": os.getenv("LATITUDE"),
    "longitude": os.getenv("LONGITUDE"),
    "username": os.getenv("USERNAME"),
    "password": os.getenv("PASSWORD"),
    "chromecast": os.getenv("CHROMECAST"),
    "adhan_link": os.getenv("ADHAN_LINK"),
    "reminder_link": os.getenv("REMINDER_LINK"),
    "reminder_before": int(os.getenv("REMINDER_BEFORE")),
    "status_port": int(os.getenv("STATUS_PORT", 5000)),
    "time_zone": os.getenv("TZ"),
}


def init_pickle_data():
    """
    Initializes the pickle data. This function should be called once at the
    startup of the script. It fetches the prayer times and reminder times from
    the Mawaqit API and stores them in the pickle file.

    Returns:
        None
    """
    data = {}
    the_month_index = datetime.now().month - 1
    the_day_index = datetime.now().day
    prayerTimes = mawaqitClient.fetch_prayer_times()
    data["PrayerTimes"] = prayerTimes["calendar"][the_month_index][
        the_day_index.__str__()
    ]
    data["PrayerTimes"].pop(1)  # Remove the sunrise time
    data["ReminderTimes"] = [
        (
            datetime.strptime(time_str, "%H:%M")
            - timedelta(minutes=config["reminder_before"])
        ).strftime("%H:%M")
        for time_str in prayerTimes["calendar"][the_month_index][
            the_day_index.__str__()
        ]
    ]
    with open("mawaqit.pkl", "wb") as f:
        pickle.dump(data, f)


def get_pickle_data():
    with open("mawaqit.pkl", "rb") as f:
        data = pickle.load(f)
        return data


server_status = {
    "status": "OK",
    "mosque_name": "",
    "chromecast_name": "",
    "prayer_times": [],
}


class StatusHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            # Convert dictionary to JSON and send response
            server_status["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.wfile.write(json.dumps(server_status).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def run_server():
    with socketserver.TCPServer(
        ("0.0.0.0", config["status_port"]), StatusHandler
    ) as httpd:
        logging.info("Server started on port {}".format(config["status_port"]))
        httpd.serve_forever()


if __name__ == "__main__":
    """
    Initializes a MawaqitClient,
    authenticates the client, fetches the prayer times, and then enters an infinite loop
    where it continuously checks the current time and casts the Adhan or reminder if the
    current time matches the prayer times or reminder times.
    """
    logging.info("AdhanCast: Starting...")

    logging.info("MawaqitClient: Initialized")

    mawaqitClient = MawaqitClient(
        config["latitude"], config["longitude"], config["username"], config["password"]
    )

    try:
        mawaqitClient.get_api_access_token()
        logging.info("MawaqitClient: Authenticated")
    except Exception as e:
        logging.error(f"MawaqitClient: Failed to authenticate {e}")
        exit(1)

    try:
        chromecast_device = get_chromecast_device(config["chromecast"])

        logging.info(
            f"Chromecast device {chromecast_device.cast_info.friendly_name} found"
        )

    except Exception as e:
        logging.error(f"Failed to get Chromecast device {e}")
        exit(1)

    init_pickle_data()

    server_status["status"] = "OK"
    server_status["mosque_name"] = mawaqitClient.mosque_name
    server_status["chromecast_name"] = chromecast_device.cast_info.friendly_name

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    logging.info(f"Starting time: " + datetime.now().strftime("%H:%M"))

    while True:
        hh_mm = datetime.now().strftime("%H:%M")

        pickle_data = get_pickle_data()
        prayer_times = pickle_data["PrayerTimes"]
        server_status["prayer_times"] = prayer_times
        reminder_times = pickle_data["ReminderTimes"]

        if hh_mm == "00:00":
            logging.info("Fetching prayer times")
            init_pickle_data()

        if hh_mm in prayer_times:
            cast_to_chromecast(
                config["adhan_link"],
                chromecast_device,
            )

        if hh_mm in reminder_times:
            cast_to_chromecast(
                config["reminder_link"],
                chromecast_device,
            )

        time.sleep(60 - datetime.now().second)
