from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from .serializers import EventsSerializer
from rest_framework import generics
from .models import Events, EventRegistration
import django.utils.timezone as timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

class EventList(generics.ListCreateAPIView):
    queryset = Events.objects.all()
    serializer_class = EventsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Events.objects.all()
    serializer_class = EventsSerializer


class EventRegisterAPIView(APIView):
    def post(self, request, pk):
        event = get_object_or_404(Events, pk=pk)

        full_name = request.data.get('full_name')
        roll_number = request.data.get('roll_number')
        university_email = request.data.get('university_email')

        if not full_name or not roll_number or not university_email:
            return Response(
                {"error": "Name, Roll Number, and Email are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if EventRegistration.objects.filter(event=event, university_email=university_email).exists():
            return Response(
                {"error": "This email is already registered for this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not event.is_registration_open:
            return Response(
                {"error": "Registration is closed for this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        registration_data = {
            'event': event,
            'full_name': full_name,
            'roll_number': roll_number,
            'university_email': university_email,
        }

        if request.user.is_authenticated:
            registration_data['student'] = request.user

        if event.is_full:
            reg = EventRegistration.objects.create(**registration_data, status='waitlisted')
            return Response({
                "message": "Event is full. You have been added to the waitlist.",
                "status": "waitlisted",
                "registration_id": reg.id
            }, status=status.HTTP_201_CREATED)
        else:
            reg = EventRegistration.objects.create(**registration_data, status='confirmed')
            return Response({
                "message": "Registration successful!",
                "status": "confirmed",
                "registration_id": reg.id
            }, status=status.HTTP_201_CREATED)

class EventRegistrationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        event = get_object_or_404(Events, pk=pk)

        if request.user.role != 'admin' and event.organizer != request.user:
            return Response({"error": "Not authorized to view this event's attendance."}, status=403)

        registrations = event.registrations.all().order_by('registered_at')

        attendees = [{
            'id': r.id,
            'full_name': r.full_name,
            'roll_number': r.roll_number,
            'university_email': r.university_email,
            'status': r.status,
        } for r in registrations]


        return Response({
            'confirmed': event.confirmed_count,
            'waitlisted': event.waitlist_count,
            'checked_in': event.registrations.filter(status='attended').count(),
            'attendees': attendees,
        })

class EventCancelAPIView(APIView):
    def post(self, request, pk):
        registration = get_object_or_404(EventRegistration, pk=pk)
        event = registration.event

        if registration.status == 'cancelled':
            return Response(
                {"error": "Registration is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not event.is_cancellation_allowed:
            return Response(
                {"error": "Cancellation window has closed for this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        was_confirmed = (registration.status == 'confirmed')

        registration.status = 'cancelled'
        registration.cancelled_at = timezone.now()
        registration.save()

        if was_confirmed:
            first_waitlist = EventRegistration.objects.filter(
                event=event, status='waitlisted'
            ).order_by('waitlist_position').first()

            if first_waitlist:
                first_waitlist.status = 'confirmed'
                first_waitlist.waitlist_position = None
                first_waitlist.save()

        return Response(
            {"message": "Registration cancelled successfully."},
            status=status.HTTP_200_OK
        )


class CheckInAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        registration = get_object_or_404(EventRegistration, pk=pk)

        if request.user.role != 'admin' and registration.event.organizer != request.user:
            return Response({"error": "Not authorized."}, status=403)

        if registration.status != 'confirmed':
            return Response(
                {"error": "Only confirmed registrations can be checked in."},
                status=400
            )

        registration.status = 'attended'
        registration.save()

        return Response({"message": "Checked in successfully."})