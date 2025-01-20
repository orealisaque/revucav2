from django.contrib import admin
from django.utils.html import format_html
from .models import Anuncio, AnuncioFoto, AnuncioVideo, Categoria

class AnuncioFotoInline(admin.TabularInline):
    model = AnuncioFoto
    extra = 0
    max_num = 3
    readonly_fields = ['preview']
    
    def preview(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="max-height: 50px;"/>',
                obj.imagem.url
            )
        return "Sem imagem"

class AnuncioVideoInline(admin.TabularInline):
    model = AnuncioVideo
    extra = 0
    max_num = 1

@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'status', 'created_at', 'is_boosted']
    list_filter = ['status', 'is_boosted', 'created_at']
    search_fields = ['titulo', 'descricao', 'usuario__email']
    readonly_fields = ['created_at', 'updated_at', 'views']
    inlines = [AnuncioFotoInline, AnuncioVideoInline]
    actions = ['aprovar_anuncios', 'rejeitar_anuncios']

    def acoes(self, obj):
        if obj.status == 'pendente':
            return format_html(
                '<a class="button" href="{}?action=aprovar">✅ Aprovar</a> '
                '<a class="button" href="{}?action=rejeitar">❌ Rejeitar</a>',
                obj.id, obj.id
            )
        return obj.get_status_display()
    acoes.short_description = 'Ações'

    def aprovar_anuncios(self, request, queryset):
        queryset.update(status='aprovado')
    aprovar_anuncios.short_description = "Aprovar anúncios selecionados"

    def rejeitar_anuncios(self, request, queryset):
        queryset.update(status='rejeitado')
    rejeitar_anuncios.short_description = "Rejeitar anúncios selecionados"

    class Media:
        css = {
            'all': ['admin/css/custom_admin.css']
        }

@admin.register(AnuncioFoto)
class AnuncioFotoAdmin(admin.ModelAdmin):
    list_display = ['anuncio', 'is_capa', 'created_at']
    list_filter = ['is_capa', 'created_at']
    search_fields = ['anuncio__titulo']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug']
    search_fields = ['nome']
    prepopulated_fields = {'slug': ('nome',)} 