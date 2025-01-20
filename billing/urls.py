from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('upgrade/', views.upgrade_view, name='upgrade'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout'),
    path('webhook/', views.stripe_webhook, name='webhook'),
    path('boost/<int:anuncio_id>/', views.boost_anuncio, name='boost'),
    path('success/', views.PaymentSuccessView.as_view(), name='success'),
    path('cancel/', views.PaymentCancelView.as_view(), name='cancel'),
] 