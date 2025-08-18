from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db import connection
from django.contrib import messages
import logging

from .models import UserProfile, Account, Transaction, SecurityLog
from .forms import LoginForm, TransferForm

# FLAW 5: Security logging disabled
security_logger = logging.getLogger('security')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # FLAW 2: Plaintext password comparison - VULNERABILITY
            try:
                user_profile = UserProfile.objects.get(user__username=username)
                if user_profile.plaintext_password == password:
                    user = user_profile.user
                    login(request, user)
                    return redirect('dashboard')
                else:
                    # FLAW 5: No logging of failed login attempts - VULNERABILITY
                    # security_logger.warning(f"Failed login attempt for user: {username} from IP: {request.META.get('REMOTE_ADDR')}")
                    messages.error(request, 'Invalid credentials')
            except UserProfile.DoesNotExist:
                # FLAW 5: No logging of failed login attempts - VULNERABILITY
                # security_logger.warning(f"Login attempt for non-existent user: {username} from IP: {request.META.get('REMOTE_ADDR')}")
                messages.error(request, 'Invalid credentials')
            
            # FIX for FLAW 2: Use Django's built-in authentication
            # user = authenticate(request, username=username, password=password)
            # if user is not None:
            #     login(request, user)
            #     security_logger.info(f"Successful login for user: {username} from IP: {request.META.get('REMOTE_ADDR')}")
            #     return redirect('dashboard')
            # else:
            #     security_logger.warning(f"Failed login attempt for user: {username} from IP: {request.META.get('REMOTE_ADDR')}")
            #     messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()
    
    return render(request, 'banking/login.html', {'form': form})

@login_required
def dashboard(request):
    accounts = Account.objects.filter(user=request.user)
    return render(request, 'banking/dashboard.html', {'accounts': accounts})

@login_required
def account_details(request, account_id):
    # FLAW 1: Broken Access Control - No authorization check - VULNERABILITY
    account = get_object_or_404(Account, id=account_id)
    
    # FIX for FLAW 1: Check if user owns the account
    # if account.user != request.user:
    #     security_logger.warning(f"Unauthorized access attempt by {request.user.username} to account {account_id} from IP: {request.META.get('REMOTE_ADDR')}")
    #     messages.error(request, 'Access denied')
    #     return redirect('dashboard')
    
    transactions = Transaction.objects.filter(account=account)[:20]
    return render(request, 'banking/account_details.html', {
        'account': account,
        'transactions': transactions
    })

@login_required
def transfer_money(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            from_account_id = form.cleaned_data['from_account']
            to_account_number = form.cleaned_data['to_account']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            
            # FLAW 1: No access control check - VULNERABILITY
            from_account = get_object_or_404(Account, id=from_account_id)
            
            # FIX: Check if user owns the from_account
            # if from_account.user != request.user:
            #     security_logger.warning(f"Unauthorized transfer attempt by {request.user.username} from account {from_account_id}")
            #     messages.error(request, 'Access denied')
            #     return redirect('dashboard')
            
            try:
                to_account = Account.objects.get(account_number=to_account_number)
                
                if from_account.balance >= amount:
                    from_account.balance -= amount
                    to_account.balance += amount
                    from_account.save()
                    to_account.save()
                    
                    # Create transaction records
                    Transaction.objects.create(
                        account=from_account,
                        transaction_type='transfer',
                        amount=amount,
                        description=f"Transfer to {to_account_number}: {description}",
                        recipient_account=to_account_number
                    )
                    
                    messages.success(request, 'Transfer completed successfully')
                else:
                    messages.error(request, 'Insufficient funds')
            except Account.DoesNotExist:
                messages.error(request, 'Recipient account not found')
        
        return redirect('dashboard')
    else:
        user_accounts = Account.objects.filter(user=request.user)
        form = TransferForm()
        return render(request, 'banking/transfer.html', {
            'form': form,
            'accounts': user_accounts
        })

@login_required
def search_transactions(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # FLAW 3: SQL Injection vulnerability - VULNERABILITY
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM banking_transaction WHERE description LIKE '%{query}%'"
            cursor.execute(sql)
            results = cursor.fetchall()
        
        # FIX for FLAW 3: Use parameterized queries
        # with connection.cursor() as cursor:
        #     cursor.execute(
        #         "SELECT * FROM banking_transaction WHERE description LIKE %s",
        #         [f'%{query}%']
        #     )
        #     results = cursor.fetchall()
        
        # FLAW 5: No logging of search queries - VULNERABILITY
        # security_logger.info(f"Transaction search by {request.user.username}: '{query}' from IP: {request.META.get('REMOTE_ADDR')}")
    
    return render(request, 'banking/search.html', {
        'query': query,
        'results': results
    })

def logout_view(request):
    # FLAW 5: No logging of logout events - VULNERABILITY
    # security_logger.info(f"User logout: {request.user.username} from IP: {request.META.get('REMOTE_ADDR')}")
    logout(request)
    return redirect('login')