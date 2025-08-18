#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django environment
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vulnerable_banking.settings')
    
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    django.setup()

    from django.contrib.auth.models import User
    from banking.models import UserProfile, Account, Transaction

    def create_test_data():
        print("🚀 Creating extended vulnerable test data for OWASP Top 10 demonstration...")
        
        # Extended test users with various vulnerability patterns
        users_data = [
            # Original users
            {'username': 'alice', 'password': 'alice123', 'first_name': 'Alice', 'last_name': 'Smith', 'role': 'customer'},
            {'username': 'bob', 'password': 'password', 'first_name': 'Bob', 'last_name': 'Johnson', 'role': 'customer'},
            {'username': 'charlie', 'password': '123', 'first_name': 'Charlie', 'last_name': 'Brown', 'role': 'customer'},
            
            # Additional vulnerable users for demonstration
            {'username': 'admin', 'password': 'admin', 'first_name': 'Admin', 'last_name': 'User', 'role': 'admin'},
            {'username': 'teller', 'password': 'teller123', 'first_name': 'Bank', 'last_name': 'Teller', 'role': 'teller'},
            {'username': 'manager', 'password': 'manager', 'first_name': 'Branch', 'last_name': 'Manager', 'role': 'manager'},
            
            # Users with common weak passwords (for brute force demos)
            {'username': 'user1', 'password': '12345', 'first_name': 'Test', 'last_name': 'User1', 'role': 'customer'},
            {'username': 'user2', 'password': 'qwerty', 'first_name': 'Test', 'last_name': 'User2', 'role': 'customer'},
            {'username': 'demo', 'password': 'demo', 'first_name': 'Demo', 'last_name': 'Account', 'role': 'customer'},
            
            # Users for privilege escalation testing
            {'username': 'guest', 'password': 'guest123', 'first_name': 'Guest', 'last_name': 'User', 'role': 'guest'},
            {'username': 'support', 'password': 'support', 'first_name': 'Support', 'last_name': 'Staff', 'role': 'support'},
            
            # Users with XSS-prone data
            {'username': 'xsstest', 'password': 'test123', 'first_name': '<script>alert("XSS")</script>', 'last_name': 'TestUser', 'role': 'customer'},
            {'username': 'sqltest', 'password': 'test123', 'first_name': "Robert'; DROP TABLE users; --", 'last_name': 'Tables', 'role': 'customer'},
            
            # High-value targets for demonstration
            {'username': 'wealthy', 'password': 'money123', 'first_name': 'Rich', 'last_name': 'Person', 'role': 'vip'},
            {'username': 'corporate', 'password': 'corp2024', 'first_name': 'Corporate', 'last_name': 'Account', 'role': 'business'},
        ]
        
        created_users = []
        
        for user_data in users_data:
            # Create Django user (with hashed password)
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': f"{user_data['username']}@example.com",
                    'is_staff': user_data['role'] in ['admin', 'manager', 'teller'],
                    'is_superuser': user_data['role'] == 'admin'
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                print(f"✅ Created user: {user.username} (Role: {user_data['role']})")
                created_users.append(user)
            else:
                print(f"👤 User already exists: {user.username}")
                created_users.append(user)
            
            # Create vulnerable UserProfile with existing fields only
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'plaintext_password': user_data['password'],  # VULNERABILITY: Plaintext password storage
                    'phone': f"555-{hash(user.username) % 10000:04d}",
                    'address': f"{hash(user.username) % 999 + 1} Main St, City, State"
                }
            )
            if created:
                print(f"🔧 Created vulnerable profile for: {user.username}")
        
        # Create accounts with predictable patterns and varying balances
        account_types = ['checking', 'savings']
        
        for i, user in enumerate(created_users):
            # Determine number of accounts based on username (simulating role-based logic)
            num_accounts = 1
            if user.username in ['wealthy', 'corporate', 'admin', 'manager']:
                num_accounts = 2
            
            for j in range(num_accounts):
                account_type = account_types[j % len(account_types)]
                
                # Predictable account numbers (A01: Broken Access Control)
                account_number = f"{account_type[:3].upper()}{1000 + i * 10 + j}"
                
                # Varying balances based on username (simulating role-based logic)
                if user.username == 'wealthy':
                    base_balance = 100000.00
                elif user.username == 'corporate':
                    base_balance = 50000.00
                elif user.username in ['admin', 'manager']:
                    base_balance = 25000.00
                else:
                    base_balance = 1000.00
                
                account, created = Account.objects.get_or_create(
                    user=user,
                    account_number=account_number,
                    defaults={
                        'account_type': account_type,
                        'balance': base_balance + random.uniform(-500, 5000)
                    }
                )
                if created:
                    print(f"🏦 Created {account_type} account for {user.username}: {account.account_number} (${account.balance:.2f})")
        
        # Create extensive transaction history with various patterns
        accounts = Account.objects.all()
        transaction_types = ['deposit', 'withdrawal', 'transfer', 'payment', 'fee']
        
        # Create suspicious transaction patterns for fraud detection demos
        suspicious_patterns = [
            # Large round number transactions
            {'amounts': [10000.00, 9999.99, 5000.00], 'descriptions': ['Cash deposit', 'Wire transfer', 'Check deposit']},
            # Frequent small transactions (structuring)
            {'amounts': [9500.00] * 5, 'descriptions': ['Cash deposit'] * 5},
            # International transactions
            {'amounts': [2500.00, 3200.00], 'descriptions': ['International wire - Nigeria', 'Forex transaction']},
            # Late night transactions
            {'amounts': [500.00, 750.00], 'descriptions': ['ATM withdrawal', 'Online transfer']},
        ]
        
        for account in accounts:
            # Normal transaction history
            num_transactions = random.randint(10, 50)
            
            for _ in range(num_transactions):
                transaction_type = random.choice(transaction_types)
                amount = random.uniform(10.0, 2000.0)
                
                # Create transaction dates spanning several months
                transaction_date = datetime.now() - timedelta(days=random.randint(1, 180))
                
                descriptions = {
                    'deposit': ['Direct deposit', 'Cash deposit', 'Check deposit', 'Wire transfer'],
                    'withdrawal': ['ATM withdrawal', 'Check payment', 'Debit purchase', 'Cash withdrawal'],
                    'transfer': ['Online transfer', 'Mobile transfer', 'Wire transfer', 'P2P payment'],
                    'payment': ['Bill payment', 'Loan payment', 'Credit card payment', 'Service payment'],
                    'fee': ['Monthly fee', 'Overdraft fee', 'ATM fee', 'Wire fee']
                }
                
                Transaction.objects.get_or_create(
                    account=account,
                    transaction_type=transaction_type,
                    amount=amount,
                    description=random.choice(descriptions[transaction_type]),
                    defaults={'recipient_account': random.choice(accounts).account_number if transaction_type == 'transfer' else None}
                )
            
            # Add suspicious transactions for some accounts
            if random.random() < 0.3:  # 30% of accounts get suspicious activity
                pattern = random.choice(suspicious_patterns)
                for amount, desc in zip(pattern['amounts'], pattern['descriptions']):
                    Transaction.objects.get_or_create(
                        account=account,
                        transaction_type='deposit' if 'deposit' in desc else 'withdrawal',
                        amount=amount,
                        description=desc,
                        defaults={'recipient_account': None}
                    )
        
        print("\n🎉 Extended vulnerable test data creation completed!")
        print("\n" + "="*60)
        print("🔐 OWASP TOP 10 DEMONSTRATION CREDENTIALS:")
        print("="*60)
        
        # Group users by role for easier testing
        roles = {}
        for user_data in users_data:
            role = user_data['role']
            if role not in roles:
                roles[role] = []
            roles[role].append(user_data)
        
        for role, users in roles.items():
            print(f"\n📊 {role.upper()} ACCOUNTS:")
            for user_data in users:
                print(f"   Username: {user_data['username']:<12} | Password: {user_data['password']:<12} | Name: {user_data['first_name']} {user_data['last_name']}")
        
        print(f"\n🌐 Access your application at: http://127.0.0.1:8000/")
        print(f"👨‍💼 Admin panel at: http://127.0.0.1:8000/admin/")
        
        print("\n" + "="*60)
        print("🚨 VULNERABILITIES DEMONSTRATED:")
        print("="*60)
        print("A01 - Broken Access Control:")
        print("   • Predictable account numbers (CHK1000, SAV1010, etc.)")
        print("   • Role-based access issues")
        print("   • Direct object references")
        
        print("\nA02 - Cryptographic Failures:")
        print("   • Plaintext passwords stored in UserProfile")
        print("   • Weak session tokens")
        print("   • Unencrypted SSN storage")
        
        print("\nA03 - Injection:")
        print("   • SQL injection test user: sqltest")
        print("   • XSS test user: xsstest")
        
        print("\nA07 - Identification and Authentication Failures:")
        print("   • Weak passwords (123, admin, password)")
        print("   • Predictable API keys")
        print("   • Security questions equal to passwords")
        
        print("\nA08 - Software and Data Integrity Failures:")
        print("   • No integrity checks on transactions")
        print("   • Unsecured API endpoints")
        
        print(f"\n⚠️  WARNING: This is for educational purposes only!")
        print(f"   Never use these patterns in production systems!")

    create_test_data()