from django.urls import path
from . import views

urlpatterns = [
    # Plural 'events' for the list endpoint
    path('events/', views.EventList.as_view(), name='event-list'),

    # You can keep singular here, but plural is more consistent
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-crud'),

    # Keep these as-is since your JS expects them
    path('event/<int:pk>/registrations/', views.EventRegistrationsAPIView.as_view(), name='event-registrations'),
    path('event/<int:pk>/register/', views.EventRegisterAPIView.as_view(), name='event-register'),
    path('registration/<int:pk>/cancel/', views.EventCancelAPIView.as_view(), name='event-cancel'),
    path('registration/<int:pk>/check-in/', views.CheckInAPIView.as_view(), name='check-in')
]