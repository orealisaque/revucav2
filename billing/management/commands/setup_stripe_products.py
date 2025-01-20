from django.core.management.base import BaseCommand
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class Command(BaseCommand):
    help = 'Configura produtos e preços no Stripe'

    def handle(self, *args, **kwargs):
        try:
            # Cria produto VIP
            vip_product = stripe.Product.create(
                name='Plano VIP',
                description='Acesso a recursos premium'
            )
            
            # Cria preço para o produto VIP
            vip_price = stripe.Price.create(
                product=vip_product.id,
                unit_amount=4990,  # R$ 49,90
                currency='brl',
                recurring={
                    'interval': 'month'
                }
            )
            
            # Cria produto Boost
            boost_product = stripe.Product.create(
                name='Boost de Anúncio',
                description='7 dias de destaque'
            )
            
            # Cria preço para o boost
            boost_price = stripe.Price.create(
                product=boost_product.id,
                unit_amount=1990,  # R$ 19,90
                currency='brl'
            )
            
            self.stdout.write(self.style.SUCCESS('Produtos configurados com sucesso!'))
            self.stdout.write(f'VIP Price ID: {vip_price.id}')
            self.stdout.write(f'Boost Price ID: {boost_price.id}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao configurar produtos: {str(e)}')) 