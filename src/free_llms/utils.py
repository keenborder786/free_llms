"""Helper Functions for all of our models"""

from typing import List

import undetected_chromedriver as uc
from fake_useragent import UserAgent


def configure_options(driver_config: List[str]) -> uc.ChromeOptions:
    """
    Configures the Chrome options.

    Args:
    driver_config (List[str]): List of Chrome driver configuration options.

    Returns:
    uc.ChromeOptions: Configured Chrome options.
    """
    chrome_options = uc.ChromeOptions()
    userAgent = UserAgent(browsers="chrome").random
    for arg in driver_config:
        chrome_options.add_argument(arg)
    chrome_options.add_argument(f"--user-agent={userAgent}")
    return chrome_options
