from selenium import webdriver
from selenium.webdriver.common.by import By


def click_button_xpath(driver: webdriver.Chrome, xpath: str):
    button = driver.find_element(by=By.XPATH, value=xpath)
    button.click()


def click_button_classname(driver: webdriver.Chrome, classname: str):
    button = driver.find_element(by=By.CLASS_NAME, value=classname)
    button.click()


def send_keys_xpath(driver: webdriver.Chrome, xpath: str, keys: str):
    textbox = driver.find_element(by=By.XPATH, value=xpath)
    textbox.send_keys(keys)
