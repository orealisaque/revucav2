from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.html import format_html
from datetime import timedelta
from .models import CustomUser, AcompanhanteProfile, Badge, Review, Estado, Cidade

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'status_plano', 'get_cidade', 'get_estado')
    list_filter = ('plano', 'is_staff', 'cidade_ref', 'estado_ref')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('status_plano', 'is_vip')
    
    PLANO_CHOICES = [
        ('basic', 'Básico'),
        ('vip', 'VIP'),
    ]
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'foto', 'birth_date')}),
        ('Contato', {'fields': ('phone', 'whatsapp')}),
        ('Redes Sociais', {'fields': ('instagram', 'twitter')}),
        ('Localização', {'fields': ('cidade', 'estado')}),
        ('Plano', {'fields': ('plano', 'plano_expira_em', 'status_plano'),
                  'description': 'Para ativar o plano VIP, selecione "VIP" e defina uma data de expiração futura'}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'plano' in form.base_fields:
            form.base_fields['plano'].help_text = 'Escolha o tipo de plano do usuário'
            form.base_fields['plano_expira_em'].help_text = (
                'Para plano VIP, defina uma data futura. '
                'Sugestão: 30 dias a partir de hoje ({})'.format(
                    (timezone.now() + timedelta(days=30)).strftime('%d/%m/%Y')
                )
            )
        return form

    def status_plano(self, obj):
        """Exibe o status do plano de forma visual"""
        if obj.plano == 'vip' and obj.plano_expira_em and obj.plano_expira_em > timezone.now():
            dias_restantes = (obj.plano_expira_em - timezone.now()).days
            return format_html(
                '<span style="color: green; font-weight: bold;">VIP ATIVO</span><br>'
                '<small>Expira em: {} ({} dias restantes)</small>',
                obj.plano_expira_em.strftime('%d/%m/%Y'),
                dias_restantes
            )
        elif obj.plano == 'vip' and obj.plano_expira_em and obj.plano_expira_em <= timezone.now():
            return format_html(
                '<span style="color: red;">VIP EXPIRADO</span><br>'
                '<small>Expirou em: {}</small>',
                obj.plano_expira_em.strftime('%d/%m/%Y')
            )
        return format_html('<span style="color: gray;">PLANO BÁSICO</span>')
    
    status_plano.short_description = 'Status do Plano'

    def save_model(self, request, obj, form, change):
        # Não precisa definir is_vip aqui, o modelo cuida disso
        super().save_model(request, obj, form, change)

    def get_cidade(self, obj):
        return obj.cidade_ref.nome if obj.cidade_ref else '-'
    get_cidade.short_description = 'Cidade'
    
    def get_estado(self, obj):
        return obj.estado_ref.sigla if obj.estado_ref else '-'
    get_estado.short_description = 'Estado'

@admin.register(AcompanhanteProfile)
class AcompanhanteProfileAdmin(admin.ModelAdmin):
    list_display = ('nome_artistico', 'idade', 'get_cidade', 'get_estado', 'reviews_count', 'is_premium')
    list_filter = (
        'is_premium',
        'cidade_ref',
        'estado_ref'
    )
    search_fields = ('nome_artistico', 'bio')
    
    def get_cidade(self, obj):
        return obj.cidade_ref.nome if obj.cidade_ref else '-'
    get_cidade.short_description = 'Cidade'
    
    def get_estado(self, obj):
        return obj.estado_ref.sigla if obj.estado_ref else '-'
    get_estado.short_description = 'Estado'

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla')
    search_fields = ('nome', 'sigla')

@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'estado')
    list_filter = ('estado',)
    search_fields = ('nome',)

admin.site.register(Badge)
admin.site.register(Review) 