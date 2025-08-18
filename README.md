<!-- @format -->

# Vulnerable Banking Web Application - Security Project

This project demonstrates 5 security vulnerabilities from the OWASP Top 10 (2021) list in a Django web application, along with their fixes.

## OWASP Top 10 (2021) Vulnerabilities Implemented

1. **A01:2021 – Broken Access Control** - Users can access other users' accounts
2. **A02:2021 – Cryptographic Failures** - Passwords stored in plaintext
3. **A03:2021 – Injection** - SQL Injection in transaction search
4. **A07:2021 – Identification and Authentication Failures** - No session timeout, weak password policy
5. **A09:2021 – Security Logging and Monitoring Failures** - No logging of security events

## Project Structure

```
vulnerable-banking-app/
├── manage.py
├── requirements.txt
├── README.md
├── screenshots/
├── vulnerable-banking/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── banking/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── forms.py
    └── templates/
        └── banking/
            ├── base.html
            ├── login.html
            ├── dashboard.html
            ├── transfer.html
            └── search.html
```

## Installation Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Windows

1. Install Python from https://python.org
2. Open Command Prompt
3. Navigate to project directory
4. Run: `pip install -r requirements.txt`
5. Run: `python manage.py migrate`
6. Run: `python manage.py createsuperuser`
7. Run: `python manage.py runserver`

### Linux/Mac

1. Install Python 3.8+ using your package manager or from python.org
2. Open Terminal
3. Navigate to project directory
4. Run: `pip3 install -r requirements.txt`
5. Run: `python3 manage.py migrate`
6. Run: `python3 manage.py createsuperuser`
7. Run: `python3 manage.py runserver`

### Creating Test Users

After running the server, access the admin panel at http://127.0.0.1:8000/admin/ and create some test users with bank accounts.

## Security Flaws Documentation

### Flaw 1: A01:2021 – Broken Access Control

**Location**: `banking/views.py` - `account_details` view
**Issue**: Users can access any account by manipulating the account_id parameter
**Impact**: Unauthorized access to other users' financial information

### Flaw 2: A02:2021 – Cryptographic Failures

**Location**: `banking/models.py` - User model password field
**Issue**: Passwords stored in plaintext in database
**Impact**: Complete exposure of user credentials if database is compromised

### Flaw 3: A03:2021 – Injection

**Location**: `banking/views.py` - `search_transactions` view
**Issue**: SQL injection through unsanitized search input
**Impact**: Potential database compromise, data theft

### Flaw 4: A07:2021 – Identification and Authentication Failures

**Location**: `banking/views.py` - Login system
**Issue**: No session timeout, weak password validation
**Impact**: Session hijacking, weak passwords allowed

### Flaw 5: A09:2021 – Security Logging and Monitoring Failures

**Location**: Throughout application
**Issue**: No logging of failed logins, suspicious activities
**Impact**: Inability to detect and respond to attacks

## Screenshots Required

- `flaw-1-before-1.png` - Accessing another user's account
- `flaw-1-after-1.png` - Access denied after fix
- `flaw-2-before-1.png` - Plaintext password in database
- `flaw-2-after-1.png` - Hashed password after fix
- `flaw-3-before-1.png` - SQL injection successful
- `flaw-3-after-1.png` - SQL injection blocked
- `flaw-4-before-1.png` - Weak password accepted
- `flaw-4-after-1.png` - Strong password required
- `flaw-5-before-1.png` - No log entries for failed login
- `flaw-5-after-1.png` - Security events logged

## Testing the Vulnerabilities

1. **Access Control**: Try accessing `/account/2/` when logged in as user 1
2. **Plaintext Passwords**: Check database or admin panel for password values
3. **SQL Injection**: Try search terms like `'; DROP TABLE banking_account; --`
4. **Weak Authentication**: Try logging in with password "123"
5. **No Logging**: Check for absence of security logs after failed attempts
