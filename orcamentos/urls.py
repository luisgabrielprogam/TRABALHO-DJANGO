from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_produtos, name='lista_produtos'),
    path('produtos/novo/', views.criar_produto, name='criar_produto'),
    path('produtos/editar/<int:pk>/', views.editar_produto, name='editar_produto'),
    path('produtos/deletar/<int:pk>/', views.deletar_produto, name='deletar_produto'),
    
    path('orcamentos/', views.lista_orcamentos, name='lista_orcamentos'),
    path('orcamentos/novo/', views.criar_orcamento, name='criar_orcamento'),
    path('orcamentos/<int:pk>/', views.detalhe_orcamento, name='detalhe_orcamento'),
    path('orcamentos/<int:pk>/pdf/', views.gerar_pdf, name='gerar_pdf'),
    path('orcamentos/deletar/<int:pk>/', views.deletar_orcamento, name='deletar_orcamento'),
]
