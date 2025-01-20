from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy
from ads.models import Anuncio
from .models import ModerationLog

class ModeratorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'moderador'

class ModerationQueueView(ModeratorRequiredMixin, ListView):
    model = Anuncio
    template_name = 'moderation/queue.html'
    context_object_name = 'anuncios'
    paginate_by = 20

    def get_queryset(self):
        return Anuncio.objects.filter(status='pendente').order_by('created_at')

class ModerationDetailView(ModeratorRequiredMixin, DetailView):
    model = Anuncio
    template_name = 'moderation/detail.html'
    context_object_name = 'anuncio'

    def post(self, request, *args, **kwargs):
        anuncio = self.get_object()
        action = request.POST.get('action')
        reason = request.POST.get('reason', '')

        if action in ['approve', 'reject', 'suspend']:
            status_map = {
                'approve': 'aprovado',
                'reject': 'rejeitado',
                'suspend': 'suspenso'
            }
            
            anuncio.status = status_map[action]
            anuncio.save()

            ModerationLog.objects.create(
                anuncio=anuncio,
                moderator=request.user,
                action=action,
                reason=reason
            )

            messages.success(request, f'Anúncio {status_map[action]} com sucesso.')
            return redirect('moderation:queue')

        messages.error(request, 'Ação inválida.')
        return redirect('moderation:detail', pk=anuncio.pk) 