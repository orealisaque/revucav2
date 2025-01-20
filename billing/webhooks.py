import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Subscription
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'customer.subscription.updated':
        subscription_data = event['data']['object']
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=subscription_data['id']
            )
            subscription.status = subscription_data['status']
            subscription.current_period_end = timezone.datetime.fromtimestamp(
                subscription_data['current_period_end']
            )
            subscription.save()
        except Subscription.DoesNotExist:
            pass

    elif event['type'] == 'customer.subscription.deleted':
        subscription_data = event['data']['object']
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=subscription_data['id']
            )
            subscription.status = 'canceled'
            subscription.save()
        except Subscription.DoesNotExist:
            pass

    return HttpResponse(status=200) 