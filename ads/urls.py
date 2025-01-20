from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.AnuncioListView.as_view(), name='anuncio_list'),
    path('novo/', views.AnuncioCreateView.as_view(), name='anuncio_create'),
    path('<int:pk>/', views.AnuncioDetailView.as_view(), name='anuncio_detail'),
    path('<int:pk>/editar/', views.AnuncioUpdateView.as_view(), name='anuncio_update'),
    path('<int:pk>/excluir/', views.AnuncioDeleteView.as_view(), name='anuncio_delete'),
    path('<int:pk>/modal/', views.anuncio_modal, name='anuncio_modal'),
    path('api/anuncios/ativos/', views.anuncios_ativos, name='anuncios_ativos'),
    path('api/anuncios/categoria/<str:categoria>/', views.anuncios_por_categoria, name='anuncios_por_categoria'),
    path('categoria/<slug:slug>/', views.categoria_list, name='categoria_list'),
    path('<int:pk>/delete/', views.AnuncioDeleteView.as_view(), name='delete'),
    path('api/anuncio/<int:pk>/', views.anuncio_api_detail, name='anuncio_api_detail'),
] 