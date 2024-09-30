"""
URL configuration for projeto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
urlpatterns = [
    path('',views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('residuo/',views.residuo, name='residuo'),
    path('add-residuo/', views.add_residuo, name='add_residuo'),
    path('edit-residuo/', views.edit_residuo, name='edit_residuo'),
    path('delete-residuo/', views.delete_residuo, name='delete_residuo'),
    path('deposito/',views.deposito, name='deposito'),
    path('add-deposito/', views.add_deposito, name='add_deposito'),
    path('edit-deposito/', views.edit_deposito, name='edit_deposito'),
    path('delete-deposito/', views.delete_deposito, name='delete_deposito'),
    path('parceiro/',views.parceiro, name='parceiro'),
    path('parceiro_coletor/',views.parceiro_coletor, name='parceiro_coletor'),
    path('salvar-solicitacao/', views.salvar_solicitacao, name='salvar_solicitacao'),
    path('aprovar_solicitacoes/', views.aprovar_solicitacoes, name='aprovar_solicitacoes'),
]
