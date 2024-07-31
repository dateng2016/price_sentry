import sys

sys.path.append("/home/da/Desktop/coding/price_sentry/app")


from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import os
from lxml import etree
from typing import Optional, List


from scraper.utils import *
from lib import schemas
from lib.utils import hash256, get_logger


BASE_URL = "https://www.amazon.com"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = CURRENT_DIR + "/html"

# Configure logging

logger = get_logger(
    name=__name__,
    filename="log/scraper.log",
    fmt="%(asctime)s - %(levelname)s - AMAZON - %(message)s",
)


def amazon_search(keyword: str, include: str = None) -> Optional[List[schemas.Product]]:

    include = include or ""
    include_ls = include.split(" ")

    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.get(f"https://www.amazon.com/s?k={keyword}")
    sleep(3)  # Wait enough time for the page to load
    page_source = driver.page_source
    with open(HTML_PATH + "/page_source.html", "w") as file:
        file.write(page_source)

    tree = etree.fromstring(text=page_source, parser=etree.HTMLParser())

    # The parent div contains all the potential products
    parent = tree.xpath('//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]')[0]
    if parent is None:
        return None
    parent_str = etree.tostring(element_or_tree=parent).decode()
    with open(CURRENT_DIR + "/html/parent.html", "w") as file:
        file.write(parent_str)

    potential_products = parent.xpath("./div")
    if not potential_products:
        return None

    # Iterate through the list to find which <div> contains a product
    # Criteria:
    #   has to have an image
    #   has to contain 'out of 5 stars'
    #   has to contain a <a> tag
    #   has to include every word in the "include" list

    products = []
    html_str = ""  # For debugging purpose

    count = 0  # During DEV mode, we limit the number of iteration to avoid taking up too much time for testing.
    max_iter = 5

    for potential_product in potential_products:
        count += 1
        if count > max_iter:
            break
        image_elements = potential_product.xpath(".//img")
        link_elements = potential_product.xpath(".//a")

        potential_product_element_str = etree.tostring(
            element_or_tree=potential_product
        ).decode()
        if (
            not image_elements
            or not link_elements
            or not "out of 5 stars" in potential_product_element_str
        ):
            continue
        src = image_elements[0].get("src")
        href = link_elements[0].get("href")

        product_link = href if href.startswith("https://") else BASE_URL + href

        # For debugging
        html_str += f'<a href="{product_link}"> LINK </a>'
        html_str += f'<img src="{src}" / >'

        driver.get(product_link)

        # getting the price of the product
        try:
            price_div_element = driver.find_element(
                by=By.XPATH, value='//*[@id="corePrice_feature_div"]'
            )
            price_whole_element = price_div_element.find_element(
                by=By.XPATH, value='.//span[@class="a-price-whole"]'
            )
            price_fraction_element = price_div_element.find_element(
                by=By.XPATH, value='.//span[@class="a-price-fraction"]'
            )
        except:
            logger.error(f"No price found for link: {product_link}")
            continue

        price_whole = price_whole_element.text
        price_fraction = price_fraction_element.text
        price = price_whole + "." + price_fraction

        try:
            price = float(price)
        except:  # Not able to get the price from the page (might be out of stock)
            price = -1.0

        try:

            title_element = driver.find_element(
                by=By.XPATH, value='//*[@id="productTitle"]'
            )
            title = title_element.text

            has_include = True
            for word in include_ls:
                if word.lower() not in title.lower():
                    has_include = False
                    break
            if (
                not has_include
            ):  # The title of this product does not contain the include keywords

                continue
        except:
            logger.error(f"No title found for link: {product_link}")
            continue

        product = schemas.Product(
            title=title,
            vendor=schemas.Vendor.AMAZON.value,
            link=product_link,
            link_id=hash256(keyword=product_link),
            img_src=src,
            price=price,
        )

        products.append(product)

    with open(CURRENT_DIR + "/html/products.html", "w") as file:
        file.write(html_str)

    return products


def amazon_track_price(link: str) -> Optional[float]:
    current_dir = os.path.dirname(os.path.abspath(__file__))

    driver = webdriver.Chrome()
    driver.get(link)
    driver.implicitly_wait(5)

    price = None

    try:

        price_div_element = driver.find_element(
            by=By.XPATH, value='//*[@id="corePrice_feature_div"]'
        )

        price_whole_element = price_div_element.find_element(
            by=By.XPATH, value='.//span[@class="a-price-whole"]'
        )

        price_fraction_element = price_div_element.find_element(
            by=By.XPATH, value='.//span[@class="a-price-fraction"]'
        )

        price_whole = price_whole_element.text
        price_fraction = price_fraction_element.text
        price = price_whole + "." + price_fraction
    except Exception as err:
        print("Price not found.")
        print(err)

    # For debugging purpose
    # with open(current_dir + "/page_source/prod_detail.html", "w") as file:
    #     file.write(driver.page_source)

    driver.quit()

    if not price:
        return None

    try:
        price = float(price)
    except Exception as err:
        print(err)
        return

    return price


if __name__ == "__main__":

    products = amazon_search(keyword="sony xm", include="sony")
    print(f"Total number of products found: {len(products)}")
    for p in products:
        print(p)
        print("-------------")
