from email.message import EmailMessage
import smtplib
import schedule

from scraper.amazon.amazon_search import amazon_track_price
from db import models, crud
from db.base import SyncSessionLocal, get_sync_db
from lib import schemas
from config import get_settings
from lib.utils import get_logger

# Go through the products in the product table
# If lower price found, notify the user that subscribed to it.

settings = get_settings()
logger = get_logger(name="price_monitor", filename="log/price_monitor.log")


with SyncSessionLocal() as db:
    products = db.query(models.Product).all()
    # print(products)
db.close()
print(db)

for p in products:
    if schemas.Vendor(p.vendor) == schemas.Vendor.AMAZON:
        # new_price = amazon_track_price(p.link)
        new_price = p.price - 1  # This is only for testing purposes
        if new_price != p.price:
            # Update our db
            query = db.query(models.Product).filter(models.Product.link_id == p.link_id)
            user = query.first()
            query.update({"price": new_price})
            db.commit()