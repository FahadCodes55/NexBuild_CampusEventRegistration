from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

# Create your models here.


class Users(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('organizer', 'Organizer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    roll_no = models.CharField(max_length=50, blank=True, null=True, unique=True)
    department = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"


class EventCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Events(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    )
    CAMPUS_CHOICES = (
        ('main', 'Main Campus'),
        ('iqbal', 'Iqbal Campus'),
    )
    organizer = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='organized_events',
        limit_choices_to={'role__in': ['organizer', 'admin']},
        null=True, blank=True,
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    location = models.CharField(max_length=255)
    campus = models.CharField(max_length=20, choices=CAMPUS_CHOICES, default='main')
    categories = models.ManyToManyField(EventCategory, related_name='events')

    start_at_datetime = models.DateTimeField()
    end_at_datetime = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    cancellation_window_hours = models.PositiveIntegerField(
        default=48, help_text="How many hours before start can a student cancel?"
    )

    seats = models.PositiveIntegerField(help_text="Total capacity")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_at_datetime']

    def __str__(self):
        return self.name

    # Validation
    def clean(self):
        if self.end_at_datetime and self.start_at_datetime and self.end_at_datetime <= self.start_at_datetime:
            raise ValidationError("End datetime must be after start datetime.")
        if self.registration_deadline and self.start_at_datetime and self.registration_deadline > self.start_at_datetime:
            raise ValidationError("Registration deadline cannot be after the event start.")
        if self.seats is not None and self.seats <= 0:
            raise ValidationError("Seats must be greater than zero.")

    # Computed properties
    @property
    def confirmed_count(self):
        return self.registrations.filter(status='confirmed').count()

    @property
    def waitlist_count(self):
        return self.registrations.filter(status='waitlisted').count()

    @property
    def available_seats(self):
        return max(self.seats - self.confirmed_count, 0)

    @property
    def is_full(self):
        return self.available_seats == 0

    @property
    def is_registration_open(self):
        now = timezone.now()
        return (
                self.status == 'published'
                and now < self.registration_deadline
                and (self.is_full is False or True)
        )

    @property
    def is_cancellation_allowed(self):
        if not self.start_at_datetime:
            return False
        return timezone.now() < (self.start_at_datetime - timedelta(hours=self.cancellation_window_hours))


class EventRegistration(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('waitlisted', 'Waitlisted'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
    )

    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='registrations', null=True, blank=True)

    full_name = models.CharField(max_length=255, null=True, blank=True)
    roll_number = models.CharField(max_length=50, null=True, blank=True)
    university_email = models.EmailField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    waitlist_position = models.PositiveIntegerField(blank=True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('event', 'student')
        ordering = ['registered_at']

    def __str__(self):
        return f"{self.student} → {self.event.name} [{self.status}]"


class EventAttendance(models.Model):
    registration = models.OneToOneField(
        EventRegistration, on_delete=models.CASCADE, related_name='attendance'
    )
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(blank=True, null=True)
    checked_in_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='attendance_marked'
    )

    def __str__(self):
        return f"Attendance for {self.registration}"