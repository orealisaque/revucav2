from django.urls import path
from . import views

app_name = 'mod'

urlpatterns = [
    path('', views.ModerationQueueView.as_view(), name='queue'),
    path('<int:pk>/', views.ModerationDetailView.as_view(), name='detail'),
] 