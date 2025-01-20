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
    list_display = ['titulo', 'usuario', 'categoria', 'preco_formatado', 'cidade', 'status', 'created_at', 'acoes']
    list_filter = ['status', 'categoria', 'cidade']
    search_fields = ['titulo', 'descricao', 'usuario__email']
    readonly_fields = ['visualizacoes', 'created_at', 'updated_at']
    inlines = [AnuncioFotoInline, AnuncioVideoInline]
    actions = ['aprovar_anuncios', 'rejeitar_anuncios']

    def preco_formatado(self, obj):
        return f'R$ {obj.preco}/hora'
    preco_formatado.short_description = 'Preço/Hora'

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

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug']
    prepopulated_fields = {'slug': ('nome',)} 