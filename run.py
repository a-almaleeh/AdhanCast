import logging
import os
import pickle
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv

from helper.chrome import cast_to_chromecast, get_chromecast_device
from helper.mawaqit import MawaqitClient

logging.basicConfig(level=logging.INFO)
load_dotenv()

config = {
    "latitude": os.getenv("latitude"),
    "longitude": os.getenv("longitude"),
    "username": os.getenv("username"),
    "password": os.getenv("password"),
    "chromecast": os.getenv("chromecast"),
    "adhan_link": os.getenv("adhan_link"),
    "reminder_link": os.getenv("reminder_link"),
    "reminder_before": int(os.getenv("reminder_before")),
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

    while True:
        hh_mm = datetime.now().strftime("%H:%M")
        logging.info(f"Current time: {hh_mm}")

        pickle_data = get_pickle_data()
        prayer_times = pickle_data["PrayerTimes"]
        reminder_times = pickle_data["ReminderTimes"]

        if hh_mm == "00:00":
            logging.info("Fetching prayer times")
            init_pickle_data()

        if hh_mm in prayer_times:
            logging.info("Casting Adhan")
            cast_to_chromecast(
                config["adhan_link"],
                chromecast_device,
            )

        if hh_mm in reminder_times:
            logging.info("Casting reminder")
            cast_to_chromecast(
                config["reminder_link"],
                chromecast_device,
            )

        time.sleep(60)
