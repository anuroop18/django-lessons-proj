import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from lessons.payments import paypal as my_paypal
from paypalrestsdk.notifications import WebhookEvent


@require_POST
@csrf_exempt
def webhook(request):
    transmission_id = request.headers['Paypal-Transmission-Id']
    timestamp = request.headers['Paypal-Transmission-Time']
    webhook_id = settings.PAYPAL_WEBHOOK_ID
    event_body = request.body.decode('utf-8')
    cert_url = request.headers['Paypal-Cert-Url']
    auth_algo = request.headers['Paypal-Auth-Algo']
    actual_signature = request.headers['Paypal-Transmission-Sig']

    response = WebhookEvent.verify(
        transmission_id,
        timestamp,
        webhook_id,
        event_body,
        cert_url,
        actual_signature,
        auth_algo
    )
    if response:
        obj = json.loads(request.body)

        event_type = obj.get('event_type')
        resource = obj.get('resource')

        if event_type == 'PAYMENT.SALE.COMPLETED':
            my_paypal.set_paid_until(resource, my_paypal.SUBSCRIPTION)

        if event_type == 'CHECKOUT.ORDER.APPROVED':
            my_paypal.set_paid_until(resource, my_paypal.ORDER)

    return HttpResponse(status=200)
