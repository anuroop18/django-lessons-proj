import logging
import stripe

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import (HttpResponseBadRequest, HttpResponse)
from django.conf import settings

from lessons.payments.stripe import (
    upgrade_customer_from_invoice,
    upgrade_customer_from_charge
)

logger = logging.getLogger(__name__)

INVOICE_PAYMENT_SUCCESS = 'invoice.payment_succeeded'
CHARGE_SUCCESS = 'charge.succeeded'


@require_POST
@csrf_exempt
def webhook(request):
    logger.info("Stripe webhook received")

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SIGNING_KEY
        )
        logger.info("Event constructed correctly")
    except ValueError:
        # Invalid payload
        logger.warning("Invalid Payload")
        return HttpResponseBadRequest()
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        logger.warning("Invalid signature")
        return HttpResponseBadRequest()

    if event.type == INVOICE_PAYMENT_SUCCESS:
        # recurring payments
        upgrade_customer_from_invoice(
            invoice=event.data.object
        )
    if event.type == CHARGE_SUCCESS:
        # one time charges
        upgrade_customer_from_charge(
            amount=event.data.amount
        )

    return HttpResponse(status=200)
