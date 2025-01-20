from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['anuncio', 'reporter', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['anuncio__titulo', 'reporter__email', 'reason']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('anuncio', 'reporter') 