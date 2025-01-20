from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('plans/', views.PlanListView.as_view(), name='plan_list'),
    path('subscription/', views.SubscriptionDetailView.as_view(), name='subscription_detail'),
    path('checkout/<int:pk>/', views.CheckoutView.as_view(), name='checkout'),
] 