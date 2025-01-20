from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View, TemplateView
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
import stripe
from .models import Plan, Subscription, StripeCustomer, AnuncioBoost
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from datetime import timedelta
from django.db.models import F
from ads.models import Anuncio

stripe.api_key = settings.STRIPE_SECRET_KEY

class PlanListView(ListView):
    model = Plan
    template_name = 'billing/plan_list.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return Plan.objects.filter(is_active=True)

class SubscriptionDetailView(LoginRequiredMixin, DetailView):
    model = Subscription
    template_name = 'billing/subscription_detail.html'
    
    def get_object(self, queryset=None):
        return self.request.user.subscription

class CheckoutView(LoginRequiredMixin, DetailView):
    model = Plan
    template_name = 'billing/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context
    
    def post(self, request, *args, **kwargs):
        plan = self.get_object()
        
        try:
            # Criar ou atualizar cliente no Stripe
            if not hasattr(request.user, 'stripe_customer_id'):
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
            return redirect('billing:subscription_detail')
            
        except stripe.error.CardError as e:
            messages.error(request, f'Erro no cartão: {e.error.message}')
            return redirect('billing:checkout', pk=plan.pk)

class CancelSubscriptionView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            subscription = request.user.subscription
            
            # Cancelar no Stripe
            stripe_subscription = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
            
            # Atualizar no banco de dados
            subscription.cancel_at_period_end = True
            subscription.save()
            
            messages.success(request, 'Sua assinatura será cancelada ao final do período atual.')
            
        except Exception as e:
            messages.error(request, 'Erro ao cancelar assinatura. Por favor, tente novamente.')
        
        return redirect('billing:subscription_detail') 

class UpgradeView(LoginRequiredMixin, TemplateView):
    template_name = 'billing/upgrade.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        
        # Criar sessão do Stripe
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': settings.STRIPE_PRICE_ID,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=request.build_absolute_uri(reverse('billing:success')),
                cancel_url=request.build_absolute_uri(reverse('billing:cancel')),
                customer_email=self.request.user.email,
            )
            context['checkout_session_id'] = session.id
        except Exception as e:
            messages.error(self.request, 'Erro ao criar sessão de pagamento.')
        
        return context

class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'billing/success.html'

class PaymentCancelView(LoginRequiredMixin, TemplateView):
    template_name = 'billing/cancel.html'

@login_required
def upgrade_view(request):
    return render(request, 'billing/upgrade.html', {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

@login_required
def create_checkout_session(request):
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': 'Plano VIP',
                        'description': 'Acesso a recursos premium'
                    },
                    'unit_amount': 4990,  # R$ 49,90
                    'recurring': {
                        'interval': 'month'
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri('/billing/success/'),
            cancel_url=request.build_absolute_uri('/billing/cancel/'),
        )
        return JsonResponse({'sessionId': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def boost_anuncio(request, anuncio_id):
    try:
        anuncio = get_object_or_404(Anuncio, id=anuncio_id, usuario=request.user)
        
        if not anuncio.status == 'aprovado':
            return JsonResponse({'error': 'Apenas anúncios aprovados podem ser impulsionados'}, status=400)
            
        if anuncio.is_boosted:
            return JsonResponse({'error': 'Este anúncio já está impulsionado'}, status=400)
        
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': 'Boost de Anúncio',
                        'description': '7 dias de destaque'
                    },
                    'unit_amount': 1990,  # R$ 19,90
                },
                'quantity': 1,
            }],
            mode='payment',
            metadata={
                'anuncio_id': anuncio.id
            },
            success_url=request.build_absolute_uri('/billing/success/'),
            cancel_url=request.build_absolute_uri('/billing/cancel/'),
        )
        return JsonResponse({'sessionId': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
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

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        if session.mode == 'subscription':
            try:
                # Busca o usuário pelo email
                from users.models import CustomUser
                user = CustomUser.objects.get(email=session.customer_email)
                
                # Atualiza o plano
                user.plano = 'vip'
                user.plano_expira_em = timezone.now() + timedelta(days=30)
                user.save(update_fields=['plano', 'plano_expira_em'])
                
                # Cria ou atualiza o cliente Stripe
                StripeCustomer.objects.update_or_create(
                    user=user,
                    defaults={
                        'stripe_customer_id': session.customer,
                        'subscription_id': session.subscription
                    }
                )
                
            except CustomUser.DoesNotExist:
                print(f"Usuário não encontrado para o email: {session.customer_email}")
            except Exception as e:
                print(f"Erro ao processar assinatura: {str(e)}")
                
        elif session.mode == 'payment' and session.metadata.get('anuncio_id'):
            try:
                anuncio = Anuncio.objects.get(id=session.metadata['anuncio_id'])
                usuario = anuncio.usuario
                
                # Cria o boost
                AnuncioBoost.objects.create(
                    anuncio=anuncio,
                    expira_em=timezone.now() + timedelta(days=7),
                    stripe_payment_id=session.payment_intent
                )
                
                # Atualiza o anúncio
                anuncio.is_boosted = True
                anuncio.boost_expira_em = timezone.now() + timedelta(days=7)
                anuncio.boost_views_antes = anuncio.views
                anuncio.save()
                
                # Incrementa contador de boosts
                usuario.total_boosts = F('total_boosts') + 1
                usuario.save(update_fields=['total_boosts'])
                
            except Exception as e:
                print(f"Erro ao processar boost: {str(e)}")

    return HttpResponse(status=200) 