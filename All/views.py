from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import AbstractUserModel
from django.http import HttpResponse

# Register view
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        try:
            user = AbstractUserModel.objects.create_user(
                email=email,
                username=username,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            user.save()

            user = authenticate(request, email=email, password=password1)
            if user is not None:
                login(request, user)
                return redirect('login')
            else:
                messages.error(request, 'Authentication failed.')
                return redirect('login')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('register')

    return render(request, 'register.html')
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

    return render(request, 'login.html')