import logging
import stripe

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import (HttpResponseBadRequest, HttpResponse)
from django.conf import settings

from lessons.payments.stripe import upgrade_customer

logger = logging.getLogger(__name__)


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

    # Handle the event
    if event.type == 'invoice.payment_succeeded':
        # ... handle other event types
        upgrade_customer(invoice=event.data.object)
    else:
        # Unexpected event type
        return HttpResponseBadRequest()

    return HttpResponse(status=200)
