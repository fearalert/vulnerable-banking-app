<!-- @format -->

# Cybersecurity Project Essay: Banking Application Security Analysis

**LINK:** [https://github.com/fearalert/vulnerable-banking-app](https://github.com/fearalert/vulnerable-banking-app)

**Installation Instructions:**

1. Clone the repository: `git clone https://github.com/fearalert/vulnerable-banking-app`
2. Navigate to project directory: `cd vulnerable-banking-app`
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`
6. Setup test data: `python setup_test_data.py`
7. Run server: `python manage.py runserver`

Access the application at [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and use test credentials: alice/alice123, bob/password, charlie/123.

---

## FLAW 1: A01:2021 – Broken Access Control

**Source Link:** `https://github.com/fearalert/vulnerable-banking-app/blob/master/banking/views.py#L45`

**Description of Flaw:**
The application suffers from a critical broken access control vulnerability in the `account_details` view. The function retrieves account information solely based on the `account_id` parameter from the URL without verifying ownership. As a result, users can modify the account ID in the URL to access other users' financial data.

This violates the principle of least privilege, which states that users should only access resources necessary for their role \[1].

**How to Fix:**
Implement proper authorization checks:

```python
if account.user != request.user:
    security_logger.warning(f"Unauthorized access attempt by {request.user.username} to account {account_id}")
    messages.error(request, 'Access denied')
    return redirect('dashboard')
```

This aligns with OWASP’s recommendation to enforce strict access control validations \[1].

---

## FLAW 2: A02:2021 – Cryptographic Failures

**Source Link:** `https://github.com/fearalert/vulnerable-banking-app/blob/master/banking/models.py#L8`

**Description of Flaw:**
User passwords are stored in plaintext, violating basic cryptographic principles. This flaw exposes users to credential theft if the database is compromised. Furthermore, the app bypasses Django’s built-in password hashing system \[2].

**How to Fix:**
Use Django’s secure authentication system:

```python
user = authenticate(request, username=username, password=password)
if user is not None:
    login(request, user)
    return redirect('dashboard')
```

Django’s authentication system uses PBKDF2 with SHA256 by default, providing strong password hashing resistant to brute-force attacks \[2]\[3].

---

## FLAW 3: A03:2021 – Injection (SQL Injection)

**Source Link:** `https://github.com/fearalert/vulnerable-banking-app/blob/master/banking/views.py#L97`

**Description of Flaw:**
The `search_transactions` view is vulnerable to SQL injection because it directly interpolates user input into SQL queries. Attackers can inject payloads such as:

```sql
'; DROP TABLE banking_account; --
```

This could lead to full database compromise, data exfiltration, or denial of service. SQL injection remains one of the most severe and widely exploited vulnerabilities \[1].

**How to Fix:**
Use parameterized queries:

```python
with connection.cursor() as cursor:
    cursor.execute(
        "SELECT * FROM banking_transaction WHERE description LIKE %s",
        [f'%{query}%']
    )
    results = cursor.fetchall()
```

Parameterized queries separate code from data, fully mitigating SQL injection risks \[4].

---

## FLAW 4: A07:2021 – Identification and Authentication Failures

**Source Link:** `https://github.com/fearalert/vulnerable-banking-app/blob/master/vulnerable_banking/settings.py#L62`

**Description of Flaw:**
Authentication is weakened due to:

- Disabled password validators (allowing weak passwords)
- Excessive session duration (1 year)
- Disabled CSRF protection

These failures increase risks of brute-force attacks, session hijacking, and CSRF exploitation \[1].

**How to Fix:**
Enable Django’s built-in validators and security features:

```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

SESSION_COOKIE_AGE = 1800  # 30 minutes
'django.middleware.csrf.CsrfViewMiddleware',
```

This follows Django’s recommended authentication practices \[2]\[3].

---

## FLAW 5: A09:2021 – Security Logging and Monitoring Failures

**Source Link:** `https://github.com/fearalert/vulnerable-banking-app/blob/master/banking/views.py#L30`

**Description of Flaw:**
The application lacks logging of security-related events such as failed logins, unauthorized access attempts, and suspicious activity. Without monitoring, breaches remain undetected, violating best practices for incident detection and response \[1].

**How to Fix:**
Enable detailed logging:

```python
security_logger.warning(f"Failed login attempt for user: {username} from IP: {request.META.get('REMOTE_ADDR')}")
security_logger.warning(f"Unauthorized access attempt by {request.user.username} to account {account_id}")
security_logger.info(f"Successful login for user: {username} from IP: {request.META.get('REMOTE_ADDR')}")
```

Security logging enables forensic analysis, threat detection, and compliance with auditing requirements \[5].

---

## Conclusion

The vulnerabilities identified — broken access control, plaintext password storage, SQL injection, authentication failures, and lack of monitoring — represent severe threats to the confidentiality, integrity, and availability of the banking application.

By applying OWASP guidelines, Django best practices, and secure coding principles, the application can be hardened against exploitation, ensuring better protection of user data and system reliability.

---

## References

\[1] OWASP Foundation, _OWASP Top 10:2021 – The Ten Most Critical Web Application Security Risks_. Available: [https://owasp.org/Top10/](https://owasp.org/Top10/)

\[2] Django Software Foundation, _Authentication in Django_. Available: [https://docs.djangoproject.com/en/stable/topics/auth/](https://docs.djangoproject.com/en/stable/topics/auth/)

\[3] Django Software Foundation, _Password management in Django_. Available: [https://docs.djangoproject.com/en/stable/topics/auth/passwords/](https://docs.djangoproject.com/en/stable/topics/auth/passwords/)

\[4] OWASP Foundation, _SQL Injection Prevention Cheat Sheet_. Available: [https://owasp.org/www-community/attacks/SQL_Injection](https://owasp.org/www-community/attacks/SQL_Injection)

\[5] OWASP Foundation, _Logging Cheat Sheet_. Available: [https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

---
