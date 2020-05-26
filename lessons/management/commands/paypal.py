import logging
import os

import paypalrestsdk
import yaml
from django.conf import settings
from django.core.management.base import BaseCommand
from lessons.payments.paypal import mode

PRODUCT = "product"
PLAN_M = "plan_m"  # monthly plan subscription
PLAN_A = "plan_a"  # annual plan subscription

BASE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),  # commands
    "../",  #
    "../",  #
    "../",  #
)

PRODUCT_CONF_PATH = os.path.join(
    BASE_DIR, "paypal", "lessons.yml"
)
PLAN_M_CONF_PATH = os.path.join(
    BASE_DIR, "paypal", "plan-monthly.yml"
)
PLAN_A_CONF_PATH = os.path.join(
    BASE_DIR, "paypal", "plan-annual.yml"
)

logger = logging.getLogger(__name__)

myapi = paypalrestsdk.Api({
    "mode": mode(),  # noqa "sandbox" or "live"
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})


class Command(BaseCommand):

    help = """
    Manages Paypal Plans and Products
"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--create",
            "-c",
            choices=[PRODUCT, PLAN_A, PLAN_M],
            help="Creates Paypal product or plan"
        )
        parser.add_argument(
            "--list",
            "-l",
            choices=[PRODUCT, PLAN_A, PLAN_M],
            help="List Paypal products or plans"
        )

    def create_product(self):
        with open(PRODUCT_CONF_PATH, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            ret = myapi.post("v1/catalogs/products", data)
            logger.debug(ret)

    def create_plan(self, what_plan):
        plans = {
            'plan_m': PLAN_M_CONF_PATH,
            'plan_a': PLAN_A_CONF_PATH
        }
        with open(plans[what_plan], "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            ret = myapi.post("v1/billing/plans", data)
            logger.debug(ret)

    def list_product(self):
        ret = myapi.get("v1/catalogs/products")
        logger.debug(ret)

    def list_plan(self):
        ret = myapi.get("v1/billing/plans")
        logger.debug(ret)

    def create(self, what):
        if what == PRODUCT:
            self.create_product()
        else:
            self.create_plan(what)

    def list(self, what):
        if what == PRODUCT:
            self.list_product()
        else:
            self.list_plan()

    def handle(self, *args, **options):
        create_what = options.get("create")
        list_what = options.get("list")

        if create_what:
            logger.debug(f"Create a {create_what}")
            self.create(create_what)
        elif list_what:
            logger.debug(f"List {list_what}")
            self.list(list_what)
