# Cybersecurity Project Essay: Banking Application Security Analysis

This project demonstrates 5 security vulnerabilities from the OWASP Top 10 (2021) list in a Django web application, along with their fixes.

## OWASP Top 10 (2021) Vulnerabilities Implemented

1. **A01:2021** – Broken Access Control - Users can access other users' accounts
2. **A02:2021** – Cryptographic Failures - Passwords stored in plaintext
3. **A03:2021** – Injection - SQL Injection in transaction search
4. **A07:2021** – Identification and Authentication Failures - No session timeout, weak password policy
5. **A09:2021** – Security Logging and Monitoring Failures - No logging of security events

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

**Repository:** https://github.com/fearalert/vulnerable-banking-app

### Quick Setup Commands
```bash
git clone https://github.com/fearalert/vulnerable-banking-app
cd vulnerable-banking-app
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python setup_test_data.py
python manage.py runserver
```

Access the application at http://127.0.0.1:8000/ and use test credentials: alice/alice123, bob/password, charlie/123.

## Testing the Vulnerabilities

1. **Access Control:** Try accessing `/account/2/` when logged in as user 1
2. **Plaintext Passwords:** Check database or admin panel for password values
3. **SQL Injection:** Try search terms like `'; DROP TABLE banking_account; --`
4. **Weak Authentication:** Try logging in with password "123"
5. **No Logging:** Check for absence of security logs after failed attempts

## Vulnerability Analysis

### 1. FLAW 1: A01:2021 – Broken Access Control

**Source Link:** https://github.com/fearalert/vulnerable-banking-app/blob/master/banking/views.py#L60

**Description of Flaw:**
The application suffers from a critical broken access control vulnerability in the account_details view. The function retrieves account information based solely on the account_id parameter from the URL without verifying if the authenticated user owns that account. This allows any logged-in user to access other users' sensitive financial information by simply modifying the account ID in the URL.

The vulnerable code uses `get_object_or_404(Account, id=account_id)` without any ownership verification. An attacker can navigate to `/account/2/` while logged in as user 1, gaining unauthorized access to another user's account balance, transaction history, and personal information. This violates the principle of least privilege and breaks the fundamental security assumption that users should only access their own data.

**How to Fix:**
The fix involves implementing proper authorization checks before allowing access to account data. The corrected code should verify that the requested account belongs to the authenticated user.

```python
if account.user != request.user:
    security_logger.warning(f"Unauthorized access attempt by {request.user.username} to account {account_id}")
    messages.error(request, 'Access denied')
    return redirect('dashboard')
```

**Fix Source Link:** https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/banking/views.py#L56

This fix ensures that users can only view accounts they own, logging unauthorized access attempts for security monitoring. The same principle should be applied to the transfer_money view to prevent unauthorized transfers from other users' accounts. This aligns with OWASP's recommendation to enforce strict access control validations [1].

### 2. FLAW 2: A02:2021 – Cryptographic Failures

**Description of Flaw:**
The application stores user passwords in plaintext within the UserProfile model's plaintext_password field. This represents a severe cryptographic failure that exposes all user credentials if the database is compromised. The login mechanism in views.py performs direct string comparison between the submitted password and the stored plaintext value, completely bypassing Django's built-in password hashing system.

This vulnerability means that database administrators, anyone with database access, or attackers who gain database access can immediately see all user passwords. The flaw is compounded by the custom authentication logic that ignores Django's secure password handling mechanisms, leaving passwords completely unprotected.

**How to Fix:**
The fix involves removing the plaintext password field entirely and utilizing Django's built-in authentication system with proper password hashing:

```python
# Remove plaintext_password field from UserProfile model
# Replace custom authentication with Django's secure system
user = authenticate(request, username=username, password=password)
if user is not None:
    login(request, user)
    return redirect('dashboard')
```

**Fix Source Link:** https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/banking/models.py#L25

Django's authentication system uses PBKDF2 with SHA256 by default, providing strong password hashing resistant to brute-force attacks [2][3].

### 3. FLAW 3: A03:2021 – Injection (SQL Injection)

**Source Link:** https://github.com/fearalert/vulnerable-banking-app/blob/master/banking/views.py#L133

**Description of Flaw:**
The search_transactions view contains a critical SQL injection vulnerability where user input is directly concatenated into a SQL query without sanitization. The vulnerable code constructs a raw SQL query using f-string formatting: `f"SELECT * FROM banking_transaction WHERE description LIKE '%{query}%'"`. This allows attackers to inject malicious SQL code that gets executed by the database server.

An attacker can input strings like `'; DROP TABLE banking_account; --` to delete database tables, or use UNION attacks like `' UNION SELECT username,password FROM auth_user --` to extract sensitive data from other tables. This vulnerability could lead to complete database compromise, data theft, or data destruction.

**How to Fix:**
The fix uses parameterized queries that separate SQL code from user data, preventing injection attacks.

```python
with connection.cursor() as cursor:
    cursor.execute(
        "SELECT * FROM banking_transaction WHERE description LIKE %s",
        [f'%{query}%']
    )
    results = cursor.fetchall()
```

**Fix Source Link:** https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/banking/views.py#L133

Parameterized queries ensure that user input is treated as data only, not as executable SQL code, completely eliminating the injection vector. Parameterized queries separate code from data, fully mitigating SQL injection risks [4].

### 4. FLAW 4: A07:2021 – Identification and Authentication Failures

**Source Link:** https://github.com/fearalert/vulnerable-banking-app/blob/master/vulnerable_banking/settings.py#L62

**Description of Flaw:**
The application exhibits multiple authentication failures. First, all Django password validators are commented out, allowing users to set extremely weak passwords like "123" or "password". Second, the session timeout is set to one year (`SESSION_COOKIE_AGE = 86400 * 365`), creating persistent sessions that remain active indefinitely. Third, CSRF protection is disabled by commenting out CsrfViewMiddleware, making the application vulnerable to cross-site request forgery attacks.

These weaknesses collectively undermine the application's authentication security. Weak passwords are easily brute-forced, long-lived sessions increase the window for session hijacking attacks, and missing CSRF protection allows attackers to perform unauthorized actions on behalf of authenticated users.

**How to Fix:**
Enable comprehensive authentication security measures:

```python
# Enable password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Set reasonable session timeout
SESSION_COOKIE_AGE = 1800  # 30 minutes

# Enable CSRF protection
'django.middleware.csrf.CsrfViewMiddleware',  # Uncomment in MIDDLEWARE
```

**Fix Source Links:**
- Password validation: https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/vulnerable_banking/settings.py#L65
- Session timeout: https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/vulnerable_banking/settings.py#L83
- CSRF protection: https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/vulnerable_banking/settings.py#L27

This follows Django's recommended authentication practices [2][3].

### 5. FLAW 5: A09:2021 – Security Logging and Monitoring Failures

**Source Link:** https://github.com/fearalert/vulnerable-banking-app/blob/master/banking/views.py#L31

**Description of Flaw:**
The application completely lacks security event logging. All security-related logging statements are commented out throughout the codebase, including failed login attempts, unauthorized access attempts, suspicious search queries, and logout events. This creates a blind spot where security incidents go undetected and unrecorded, making it impossible to identify attack patterns, conduct forensic analysis, or respond to security breaches effectively.

Without proper logging, administrators cannot detect brute-force attacks, monitor for suspicious behavior, or maintain audit trails required for compliance. The absence of security monitoring transforms successful attacks from detectable incidents into invisible breaches.

**How to Fix:**
Implement comprehensive security logging throughout the application:

```python
# Log failed login attempts
security_logger.warning(f"Failed login attempt for user: {username} from IP: {request.META.get('REMOTE_ADDR')}")

# Log unauthorized access attempts
security_logger.warning(f"Unauthorized access attempt by {request.user.username} to account {account_id}")

# Log successful authentications
security_logger.info(f"Successful login for user: {username} from IP: {request.META.get('REMOTE_ADDR')}")
```

**Fix Source Links:** Multiple locations throughout banking/views.py (in fix-vulnerabilities branch) where logging statements are commented out.
https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/banking/views.py

The fixes create a comprehensive audit trail that enables security monitoring, incident response, and compliance reporting. Security logging enables forensic analysis, threat detection, and compliance with auditing requirements [5].

## Conclusion

These five vulnerabilities represent critical security failures that could lead to complete application compromise. Each flaw targets a different aspect of application security: access control, cryptography, input validation, authentication, and monitoring. The fixes provided address the root causes rather than merely hiding the symptoms, creating a more secure application that follows security best practices and protects user data effectively.

## References

[1] OWASP Foundation, OWASP Top 10:2021 – The Ten Most Critical Web Application Security Risks. Available: https://owasp.org/Top10/

[2] Django Software Foundation, Authentication in Django. Available: https://docs.djangoproject.com/en/stable/topics/auth/

[3] Django Software Foundation, Password management in Django. Available: https://docs.djangoproject.com/en/stable/topics/auth/passwords/

[4] OWASP Foundation, SQL Injection Prevention Cheat Sheet. Available: https://owasp.org/www-community/attacks/SQL_Injection

[5] OWASP Foundation, Logging Cheat Sheet. Available: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
