# NexBuild - Campus Event Registration System

A full-stack campus event management platform built as part of a NexBuild internship project. Students can discover events, register, join waitlists, cancel within a defined window, and manage their tickets. Organizers get a protected dashboard to create events, manage capacity, close registration, and track attendance.

## 🚀 What the Project Does
### For Students

    Discover Events — Browse published events on the homepage with search, category, and campus filters

    Register — Fill in Name, Roll Number, and Email to secure a seat

    Auto-Waitlist — If an event is full, the student is automatically added to the waitlist

    My Tickets — View all confirmed and waitlisted registrations

    Cancel — Cancel registration up to 48 hours before the event. If a confirmed student cancels, the next waitlisted student is auto-promoted

### For Organizers

    Protected Dashboard — Only organizers and admins can access /dashboard/

    Create Events — Publish events with image, category, campus, capacity, dates, and cancellation rules

    Manage Events — Close registration, publish drafts, view attendee counts

    Attendance — Select an event, view all registrants, and mark students as Checked In

### For Admins

    Django Admin Panel — Full CRUD over Users, Events, Categories, and Registrations

    User Management — Create student/organizer accounts with proper password hashing

## 📦 How to Run It
Prerequisites

    Python 3.10+

    PostgreSQL 14+

    pip and virtualenv   

## Step 1 — Clone and Enter the Project
git clone https://github.com/<your-username>/campus-event-registration.git
cd campus-event-registration

## Step 2 — Create and Activate Virtual Environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

## Step 3 — Install Dependencies
pip install django djangorestframework psycopg2-binary Pillow

## Step 4 — Create the PostgreSQL Database
Open pgAdmin or psql:

CREATE DATABASE campuseventregistration;

## Step 5 — Configure the Database
DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'campuseventregistration',
        'USER': 'postgres',
        'PASSWORD': 'your_postgres_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

## Step 6 — Run Migrations
python manage.py makemigrations
python manage.py migrate

## Step 7 — Create a Superuser
python manage.py createsuperuser
