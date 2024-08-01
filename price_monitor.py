from email.message import EmailMessage
import smtplib
import schedule
from typing import List
import time

from scraper.amazon.amazon_search import amazon_track_price
from db import models
from db.base import SyncSessionLocal
from lib import schemas
from config import get_settings
from lib.utils import get_logger


class PriceMonitor:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = get_logger(name="price_monitor", filename="log/price_monitor.log")
        self.db = SyncSessionLocal()
        self.products = []

    def get_all_products(self) -> None:
        self.logger.info("Getting all products in the database")
        products = self.db.query(models.Product).all()
        self.products = products

    def check_price(self) -> None:
        for p in self.products:
            should_send_email = False
            if schemas.Vendor(p.vendor) == schemas.Vendor.AMAZON:
                # new_price = amazon_track_price(p.link)
                new_price = (
                    p.price - 1
                )  # This is only for testing purposes, pretending that the price dropped

            # TODO OTHER VENDORS

            if new_price != p.price:
                if new_price < p.price:
                    should_send_email = True
                # Update our db
                product_query = self.db.query(models.Product).filter(
                    models.Product.link_id == p.link_id
                )
                product = product_query.first()
                if not product:
                    self.logger.error(f"Product with link id {p.link_id} not found")
                    return

                product_query.update({"price": new_price})
                self.db.commit()

            if should_send_email:
                emails = self.get_emails_by_product(p.link_id)
                self.logger.info(f"Sending email to user xxx")
                for email_to in emails:
                    self.send_email(
                        email_to=email_to,
                        vendor="amazon",
                        new_price=new_price,
                        product=p,
                    )

    def get_emails_by_product(self, link_id: str) -> List[str]:
        emails = []
        # first go through the subscription table to grap all the user id
        user_id_ls = []
        self.logger.info(f"Getting all subscriptions for the link id {link_id}")
        subscriptions = (
            self.db.query(models.Subscription)
            .filter(models.Subscription.link_id == link_id)
            .all()
        )
        if not subscriptions:
            self.logger.error(f"Failed to get subscriptions by link id {link_id}")
            return []
        for s in subscriptions:
            user_id_ls.append(s.user_id)
        for user_id in user_id_ls:
            self.logger.info(f"Getting user email by user id {user_id}")
            user = self.db.query(models.User).filter(models.User.id == user_id).first()
            if not user:
                self.logger.error(f"Failed to get user email by user id {user_id}")
            emails.append(user.email)
        return emails

    def send_email(
        self,
        email_to: str,
        vendor: str,
        new_price: str,
        product: schemas.Product,
    ) -> None:
        try:
            self.logger.info(f"Sending price update email to {email_to}")
            msg = EmailMessage()
            msg.set_content(
                f"Great news! We have a lower price of ${new_price} for your {vendor} product {product.title}. Here is your link! {product.link}"
            )

            msg["Subject"] = "Hurry up! We got a better deal for your product!"
            msg["From"] = self.settings.email_from
            msg["To"] = email_to

            # Connect to Gmail's SMTP server
            connection = smtplib.SMTP("smtp.gmail.com", 587)
            connection.starttls()
            connection.login(
                user=self.settings.email_from, password=self.settings.app_password
            )
            connection.send_message(msg=msg)
            connection.quit()
        except Exception as err:
            self.logger.error(f"Failed to send price update email to {email_to}. {err}")


if __name__ == "__main__":
    price_monitor = PriceMonitor()

    schedule.every().hour.do(price_monitor.get_all_products)
    schedule.every().hour.do(price_monitor.check_price)
    while True:
        schedule.run_pending()
        time.sleep(100)
