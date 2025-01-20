from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('get_cidades/', views.get_cidades, name='get_cidades'),
    path('logout/', views.custom_logout, name='logout'),
    path('cidades/<int:estado_id>/', views.get_cidades, name='get_cidades'),
] 