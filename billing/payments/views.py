from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.conf import settings
from django.contrib import messages
import stripe
from .models import Plan, Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

class PlanListView(ListView):
    model = Plan
    template_name = 'payments/plan_list.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return Plan.objects.filter(is_active=True)

class SubscriptionDetailView(LoginRequiredMixin, DetailView):
    model = Subscription
    template_name = 'payments/subscription_detail.html'
    
    def get_object(self, queryset=None):
        return self.request.user.subscription

class CheckoutView(LoginRequiredMixin, DetailView):
    model = Plan
    template_name = 'payments/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context
    
    def post(self, request, *args, **kwargs):
        plan = self.get_object()
        
        try:
            # Criar ou atualizar cliente no Stripe
            if not request.user.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=request.user.email,
                    source=request.POST['stripeToken']
                )
                request.user.stripe_customer_id = customer.id
                request.user.save()
            
            # Criar assinatura
            subscription = stripe.Subscription.create(
                customer=request.user.stripe_customer_id,
                items=[{'price': plan.stripe_price_id}],
            )
            
            # Salvar assinatura no banco de dados
            Subscription.objects.create(
                user=request.user,
                plan=plan,
                stripe_subscription_id=subscription.id,
                status=subscription.status,
                current_period_end=timezone.datetime.fromtimestamp(
                    subscription.current_period_end
                )
            )
            
            messages.success(request, 'Assinatura realizada com sucesso!')
            return redirect('payments:subscription_detail')
            
        except stripe.error.CardError as e:
            messages.error(request, f'Erro no cartão: {e.error.message}')
            return redirect('payments:checkout', pk=plan.pk) 