from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from .models import Request


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        text = request.POST.get('text', '')
        if text:
            Request.objects.create(user=request.user, text=text.upper())
            messages.success(request, f'Text "{text}" converted to uppercase successfully.')
            return redirect('home')
    return render(request, 'home.html')


def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('login')


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def history(request):
    # if not request.user.is_authenticated:
    #     return redirect('login')
    requests = Request.objects.filter(user=request.user).order_by('-created_at')[:20]
    return render(request, 'history.html', {'requests': requests})


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')
