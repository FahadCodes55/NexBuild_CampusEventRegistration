from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from api.models import Events, EventRegistration
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Q

# Create your views here.

def index(request):
    all_events = Events.objects.filter(status='published').order_by('-start_at_datetime')
    search_query = request.GET.get('search', '')
    if search_query:
        all_events = all_events.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    category_filter = request.GET.get('category', 'all')
    if category_filter and category_filter != 'all':
        all_events = all_events.filter(categories__name__iexact=category_filter)

    campus_filter = request.GET.get('campus', '')
    if campus_filter:
        all_events = all_events.filter(campus=campus_filter)

    return render(request, 'Events/index.html', {
        'all_events': all_events,
        'search_query': search_query,
        'active_category': category_filter,
        'active_campus': campus_filter,
    })
    return render(request, 'Events/index.html', context)

def events(request, pk):
    event = get_object_or_404(Events, pk=pk)
    return render(request, 'Events/event_detail.html', {
        'event_detail': event,
    })


def login(request):
    if request.user.is_authenticated:
        if request.user.role in ['organizer', 'admin']:
            return redirect('dashboard')
        return redirect('home')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            if user.role in ['organizer', 'admin']:
                return redirect('dashboard')
            return redirect('home')
        else:
            error = "Invalid username or password."

    # Pass the error variable directly to the template
    return render(request, 'Events/login.html', {'error': error})



def logout(request):
    auth_logout(request)
    return redirect('home')

@login_required(login_url='login')
def ticket(request):
    ticket = EventRegistration.objects.filter(
        status__in=['confirmed', 'waitlisted']
    ).select_related('event').order_by('-registered_at')
    return render(request, 'Events/ticket.html', {'tickets': ticket})


@login_required(login_url='login')
def dashboard(request):
    if request.user.role not in ['organizer', 'admin']:
        return HttpResponseForbidden("You do not have permission to access this page.")

    if request.user.role == 'admin':
        my_events = Events.objects.all().order_by('-created_at')
    else:
        my_events = Events.objects.filter(organizer=request.user).order_by('-created_at')

    return render(request, 'Events/dashboard.html', {'my_events': my_events})