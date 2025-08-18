<!-- @format -->

# Cybersecurity Project Essay: Banking Application Security Analysis

**LINK:** https://github.com/fearalert/vulnerable-banking-app

**Installation Instructions:**

1. Clone the repository: `git clone https://github.com/fearalert/vulnerable-banking-app`
2. Navigate to project directory: `cd vulnerable-banking-app`
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`
6. Setup test data: `python setup_test_data.py`
7. Run server: `python manage.py runserver`

Access the application at http://127.0.0.1:8000/ and use test credentials: alice/alice123, bob/password, charlie/123.

## FLAW 1: A01:2021 – Broken Access Control

**Source Link:** `https://github.com/fearalert/vulnerable-banking-app/blob/main/banking/views.py#L45`

**Description of Flaw:**
The application suffers from a critical broken access control vulnerability in the `account_details` view. The function retrieves account information based solely on the `account_id` parameter from the URL without verifying if the authenticated user owns that account. This allows any logged-in user to access other users' sensitive financial information by simply modifying the account ID in the URL.

The vulnerable code uses `get_object_or_404(Account, id=account_id)` without any ownership verification. An attacker can navigate to `/account/2/` while logged in as user 1, gaining unauthorized access to another user's account balance, transaction history, and personal information. This violates the principle of least privilege and breaks the fundamental security assumption that users should only access their own data.

**How to Fix:**
The fix involves implementing proper authorization checks before allowing access to account data. The corrected code should verify that the requested account belongs to the authenticated user:

```python
if account.user != request.user:
    security_logger.warning(f"Unauthorized access attempt by {request.user.username} to account {account_id}")
    messages.error(request, 'Access denied')
    return redirect('dashboard')
```

**Fix Source Link:** `https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/banking/views.py#L48`

This fix ensures that users can only view accounts they own, logging unauthorized access attempts for security monitoring. The same principle should be applied to the `transfer_money` view to prevent unauthorized transfers from other users' accounts.

## FLAW 2: A02:2021 – Cryptographic Failures

**Source Link:** `https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/banking/models.py#L8`

**Description of Flaw:**
The application stores user passwords in plaintext within the `UserProfile` model's `plaintext_password` field. This represents a severe cryptographic failure that exposes all user credentials if the database is compromised. The login mechanism in `views.py` performs direct string comparison between the submitted password and the stored plaintext value, completely bypassing Django's built-in password hashing system.

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

**Fix Source Link:** `https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/banking/views.py#L40`

Django automatically handles password hashing using PBKDF2 with SHA256, making passwords computationally expensive to crack even if the database is compromised.

## FLAW 3: A03:2021 – Injection (SQL Injection)

**Source Link:** `https://github.com/fearalert/vulnerable-banking-app/blob/main/banking/views.py#L97`

**Description of Flaw:**
The `search_transactions` view contains a critical SQL injection vulnerability where user input is directly concatenated into a SQL query without sanitization. The vulnerable code constructs a raw SQL query using f-string formatting: `f"SELECT * FROM banking_transaction WHERE description LIKE '%{query}%'"`. This allows attackers to inject malicious SQL code that gets executed by the database server.

An attacker can input strings like `'; DROP TABLE banking_account; --` to delete database tables, or use UNION attacks like `' UNION SELECT username,password FROM auth_user --` to extract sensitive data from other tables. This vulnerability could lead to complete database compromise, data theft, or data destruction.

**How to Fix:**
The fix uses parameterized queries that separate SQL code from user data, preventing injection attacks:

```python
with connection.cursor() as cursor:
    cursor.execute(
        "SELECT * FROM banking_transaction WHERE description LIKE %s",
        [f'%{query}%']
    )
    results = cursor.fetchall()
```

**Fix Source Link:** `https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/banking/views.py#L101`

Parameterized queries ensure that user input is treated as data only, not as executable SQL code, completely eliminating the injection vector.

## FLAW 4: A07:2021 – Identification and Authentication Failures

**Source Link:** `https://github.com/fearalert/vulnerable-banking-app/blob/main/vulnerable_banking/settings.py#L62`

**Description of Flaw:**
The application exhibits multiple authentication failures. First, all Django password validators are commented out, allowing users to set extremely weak passwords like "123" or "password". Second, the session timeout is set to one year (`SESSION_COOKIE_AGE = 86400 * 365`), creating persistent sessions that remain active indefinitely. Third, CSRF protection is disabled by commenting out `CsrfViewMiddleware`, making the application vulnerable to cross-site request forgery attacks.

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

- Password validation: `https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/vulnerable_banking/settings.py#L65`
- Session timeout: `https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/vulnerable_banking/settings.py#L81`
- CSRF protection: `https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/vulnerable_banking/settings.py#L24`

## FLAW 5: A09:2021 – Security Logging and Monitoring Failures

**Source Link:** `https://github.com/fearalert/vulnerable-banking-app/blob/fix-vulnerabilities/banking/views.py#L30`

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

**Fix Source Links:** Multiple locations throughout `banking/views.py` where logging statements are commented out, starting at line 30, 52, 87, and 134.

The fixes create a comprehensive audit trail that enables security monitoring, incident response, and compliance reporting.

## Conclusion

These five vulnerabilities represent critical security failures that could lead to complete application compromise. Each flaw targets a different aspect of application security: access control, cryptography, input validation, authentication, and monitoring. The fixes provided address the root causes rather than merely hiding the symptoms, creating a more secure application that follows security best practices and protects user data effectively.
