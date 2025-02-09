import logging
from typing import Optional

import pychromecast
import zeroconf


def get_chromecast_device(friendly_name: str) -> Optional[pychromecast.Chromecast]:
    """Returns the Chromecast device with the friendly name stored in the database.

    Args:
        friendly_name: The friendly name to search for.

    Returns:
        The Chromecast device with the specified friendly name, or None if not found.
    """

    zconf = zeroconf.Zeroconf()
    browser = pychromecast.CastBrowser(
        pychromecast.SimpleCastListener(
            lambda uuid, service: print(browser.devices[uuid].friendly_name)
        ),
        zconf,
    )
    browser.start_discovery()
    pychromecast.discovery.stop_discovery(browser)

    # Get the Chromecast device with the friendly name.
    chromecasts, browser = pychromecast.get_listed_chromecasts(
        friendly_names=[friendly_name]
    )

    if not chromecasts:
        logging.error("Chromecast device not found")
        raise Exception("Chromecast device not found")

    return chromecasts[0]


def cast_to_chromecast(link: str, device: pychromecast.Chromecast) -> None:
    """Casts the link to the Chromecast device.

    Args:
        link: The link to cast.
        device: The Chromecast device to cast to.
    """

    device.wait()

    # Set the volume to 0.4.
    device.set_volume(0.4)

    # Play the adhan.
    mc = device.media_controller
    mc.play_media(link, "audio/mp3")
    mc.block_until_active()
    mc.play()
