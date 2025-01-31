from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from .models import AbstractUserModel
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required

MAX_DEPOSIT = 9999999.00

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
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
    if request.user.is_authenticated:
        return redirect('home')
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

def check_account_balance(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    try:
        user_detail = AbstractUserModel.objects.get(email=user.email)
        context = {
            'user': user,
            'account_balance': user_detail.account_balance,
        }
    except AbstractUserModel.DoesNotExist:
        context = {
            'error': 'User details not found!',
        }

    return render(request, 'check_balance.html', context)

MAX_BALANCE_DIGITS = 10

def deposit_money(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    try:
        user_detail = AbstractUserModel.objects.get(email=user.email)
    except AbstractUserModel.DoesNotExist:
        return render(request, 'error.html', {'error': 'User not found'})

    if request.method == 'POST':
        amount = request.POST.get('amount')

        if not amount:
            return render(request, 'deposit_money.html', {'error': 'Please enter a valid amount to deposit.'})

        amount = amount.strip()
        amount = amount.replace(',', '')

        if not all(c.isdigit() or c == '.' for c in amount):
            return render(request, 'deposit_money.html', {'error': 'Invalid amount format. Only numbers and a decimal point are allowed.'})

        try:
            deposit_amount = Decimal(amount)
        except InvalidOperation:
            return render(request, 'deposit_money.html', {'error': 'Invalid amount format. Please enter a valid number.'})

        try:
            deposit_amount = deposit_amount.quantize(Decimal('0.01'))
        except InvalidOperation:
            return render(request, 'deposit_money.html', {'error': 'Invalid deposit amount format.'})

        if deposit_amount <= 0:
            return render(request, 'deposit_money.html', {'error': 'Amount must be greater than zero.'})

        if deposit_amount >= MAX_DEPOSIT:
            return render(request, 'deposit_money.html', {'error': f'Amount exceeds the allowed limit of ${MAX_DEPOSIT}.'})

        new_balance = user_detail.account_balance + deposit_amount
        if len(str(new_balance).replace('.', '').replace('-', '')) > MAX_BALANCE_DIGITS:
            return render(request, 'deposit_money.html', {'error': 'Depositing this amount would exceed the maximum allowed balance.'})

        user_detail.account_balance = new_balance
        try:
            user_detail.save()
        except Exception:
            return render(request, 'deposit_money.html', {'error': 'There was an error processing your deposit.'})

        return render(request, 'deposit_money.html', {'success': f'You have successfully deposited ${deposit_amount}.'})

    return render(request, 'deposit_money.html')
def withdraw_money(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    
    try:
        user_detail = AbstractUserModel.objects.get(email=user.email)
        context = {
            'user': user_detail
        }
    except AbstractUserModel.DoesNotExist:
        messages.error(request, 'User not found.')
        return render(request, 'withdraw_money.html', context)

    if request.method == 'POST':
        amount = request.POST.get('amount')

        if not amount or float(amount) <= 0:
            messages.error(request, 'Please enter a valid amount to withdraw.')
            return render(request, 'withdraw_money.html', context)

        # Convert withdraw_amount to Decimal
        withdraw_amount = Decimal(amount)

        if user_detail.account_balance < withdraw_amount:
            messages.error(request, 'Insufficient balance for this withdrawal.')
            return render(request, 'withdraw_money.html', context)

        user_detail.account_balance -= withdraw_amount
        user_detail.save()

        # Pass the updated balance to the template
        messages.success(request, f'You have successfully withdrawn ${amount}.')
        return render(request, 'withdraw_money.html', context)

    return render(request, 'withdraw_money.html', context)
def logout_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    logout(request)
    return redirect ('login')