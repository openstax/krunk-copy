from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_chrome_driver(headless=False):
    """ Instantiates the Chrome webdriver with or without the headless option.

    """
    chrome_options = Options()
    chrome_options.add_experimental_option("w3c", False)
    if headless:
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    return driver

