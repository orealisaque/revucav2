from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import CustomUser
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class Command(BaseCommand):
    help = 'Sincroniza os planos dos usuários com o Stripe'

    def handle(self, *args, **kwargs):
        # Busca todos os usuários VIP
        vip_users = CustomUser.objects.filter(plano='vip')
        
        for user in vip_users:
            try:
                # Verifica se tem cliente Stripe
                stripe_customer = user.stripecustomer_set.first()
                if not stripe_customer:
                    continue
                    
                # Verifica assinatura no Stripe
                subscription = stripe.Subscription.retrieve(stripe_customer.subscription_id)
                
                # Atualiza status do plano
                if subscription.status == 'active':
                    user.plano_expira_em = timezone.datetime.fromtimestamp(
                        subscription.current_period_end,
                        tz=timezone.get_current_timezone()
                    )
                    user.save(update_fields=['plano_expira_em'])
                    self.stdout.write(
                        self.style.SUCCESS(f'Plano atualizado para {user.email}')
                    )
                else:
                    user.plano = 'free'
                    user.plano_expira_em = None
                    user.save(update_fields=['plano', 'plano_expira_em'])
                    self.stdout.write(
                        self.style.WARNING(f'Plano cancelado para {user.email}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao sincronizar {user.email}: {str(e)}')
                ) 