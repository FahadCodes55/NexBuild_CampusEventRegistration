from django.urls import path
from django.conf.urls.static import static, settings
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('event details/<int:pk>/', views.events, name='events'),
    path('ticket/', views.ticket, name='ticket'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)