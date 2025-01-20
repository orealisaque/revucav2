from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.html import format_html
from datetime import timedelta
from .models import CustomUser, AcompanhanteProfile, Badge, Review, Estado, Cidade

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'first_name']
    readonly_fields = ['date_joined', 'last_login']

@admin.register(AcompanhanteProfile)
class AcompanhanteProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'nome_completo', 'cidade', 'estado']
    search_fields = ['nome_completo', 'user__email']
    list_filter = ['estado', 'cidade']

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sigla']
    search_fields = ['nome', 'sigla']

@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'estado']
    search_fields = ['nome']
    list_filter = ['estado']

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'required_reviews']
    search_fields = ['name', 'description']

admin.site.register(Review) 