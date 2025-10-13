# Security Guide

This document outlines the security measures, best practices, and guidelines for the EPMS application.

## Security Overview

The EPMS application implements multiple layers of security to protect sensitive employee data and ensure system integrity.

## Authentication & Authorization

### JWT Authentication
- **Access Tokens**: Short-lived (1 hour) for API access
- **Refresh Tokens**: Long-lived (7 days) for token renewal
- **Token Rotation**: Refresh tokens are rotated on each use
- **Token Blacklisting**: Revoked tokens are blacklisted

### Role-Based Access Control (RBAC)
```python
# Role hierarchy
EMPLOYEE = 1    # Basic access to own data
MANAGER = 2     # Access to team data
HR = 3          # Access to all employee data
ADMIN = 4       # Full system access
```

### Permission System
- **Object-level permissions**: Users can only access their own data
- **Field-level permissions**: Sensitive fields restricted by role
- **Action permissions**: Role-based action restrictions

## Data Protection

### Encryption at Rest
- **Database**: PostgreSQL with encryption enabled
- **File Storage**: Encrypted file system for media files
- **Backups**: Encrypted backup storage

### Encryption in Transit
- **HTTPS**: All communication encrypted with TLS 1.2+
- **API**: JWT tokens for secure API communication
- **WebSocket**: Secure WebSocket connections (WSS)

### Sensitive Data Handling
```python
# PII Data Classification
class DataClassification:
    PUBLIC = "public"           # Employee name, role
    INTERNAL = "internal"       # Department, manager
    CONFIDENTIAL = "confidential"  # Performance data, reviews
    RESTRICTED = "restricted"   # Personal details, salary
```

## Input Validation & Sanitization

### Backend Validation
```python
# Django model validation
class User(models.Model):
    email = models.EmailField(validators=[validate_email])
    phone = models.CharField(
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    
    def clean(self):
        super().clean()
        if self.start_date >= self.end_date:
            raise ValidationError('Invalid date range')
```

### Frontend Validation
```javascript
// Client-side validation
const validateGoal = (goalData) => {
  const errors = {}
  
  if (!goalData.title || goalData.title.length < 3) {
    errors.title = 'Title must be at least 3 characters'
  }
  
  if (!goalData.target_date || new Date(goalData.target_date) <= new Date()) {
    errors.target_date = 'Target date must be in the future'
  }
  
  return errors
}
```

### SQL Injection Prevention
- **ORM Usage**: Django ORM prevents SQL injection
- **Parameterized Queries**: All database queries use parameters
- **Input Sanitization**: All user inputs are sanitized

### XSS Prevention
```python
# Django template auto-escaping
{{ user_input|escape }}

# JSON responses
return JsonResponse(data, safe=False)
```

## API Security

### Rate Limiting
```python
# API rate limiting
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

### CORS Configuration
```python
# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
CORS_ALLOW_CREDENTIALS = True
```

### Request Validation
```python
# API request validation
class GoalSerializer(serializers.ModelSerializer):
    def validate_target_date(self, value):
        if value <= timezone.now().date():
            raise serializers.ValidationError(
                "Target date must be in the future"
            )
        return value
```

## Session Management

### Secure Session Configuration
```python
# Django session settings
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

### CSRF Protection
```python
# CSRF protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
```

## File Upload Security

### File Type Validation
```python
# File upload validation
def validate_file_type(file):
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    if file.content_type not in allowed_types:
        raise ValidationError('Invalid file type')
    
    # Check file size (max 5MB)
    if file.size > 5 * 1024 * 1024:
        raise ValidationError('File too large')
```

### Secure File Storage
```python
# Secure file upload
class SecureFileField(models.FileField):
    def __init__(self, *args, **kwargs):
        kwargs['upload_to'] = 'secure_uploads/'
        super().__init__(*args, **kwargs)
```

## Logging & Monitoring

### Security Event Logging
```python
# Security logging
import logging

security_logger = logging.getLogger('security')

def log_security_event(event_type, user, details):
    security_logger.warning(f"{event_type}: {user} - {details}")
```

### Audit Trail
```python
# Audit trail for sensitive operations
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
```

### Monitoring Alerts
- **Failed Login Attempts**: Alert after 5 failed attempts
- **Unusual Access Patterns**: Alert on suspicious activity
- **Data Export**: Log all data export activities
- **Permission Changes**: Log all permission modifications

## Data Privacy

### GDPR Compliance
```python
# Data retention policies
class DataRetentionPolicy:
    USER_DATA = 7 * 365  # 7 years
    LOG_DATA = 1 * 365   # 1 year
    AUDIT_DATA = 3 * 365 # 3 years
```

### Data Anonymization
```python
# Data anonymization for exports
def anonymize_user_data(user_data):
    return {
        'id': hash(user_data['id']),
        'role': user_data['role'],
        'department': user_data['department'],
        # Remove PII
    }
```

### Right to be Forgotten
```python
# Data deletion implementation
def delete_user_data(user_id):
    # Anonymize instead of delete for audit purposes
    user = User.objects.get(id=user_id)
    user.first_name = 'Deleted'
    user.last_name = 'User'
    user.email = f'deleted_{user_id}@deleted.com'
    user.is_active = False
    user.save()
```

## Infrastructure Security

### Network Security
- **Firewall**: Restrict access to necessary ports only
- **VPN**: Secure access for administrators
- **Load Balancer**: SSL termination and DDoS protection

### Server Security
```bash
# Server hardening
# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Configure firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# 3. Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# 4. Enable fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### Database Security
```sql
-- Database security configuration
-- 1. Create dedicated database user
CREATE USER epms_user WITH PASSWORD 'strong_password';

-- 2. Grant minimal required permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO epms_user;

-- 3. Enable SSL
ALTER SYSTEM SET ssl = on;
```

### Container Security
```dockerfile
# Secure Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Install security updates
RUN apt-get update && apt-get upgrade -y

# Copy application
COPY . /app
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000
```

## Security Headers

### HTTP Security Headers
```nginx
# Nginx security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Django Security Settings
```python
# Django security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

## Vulnerability Management

### Dependency Scanning
```bash
# Scan for vulnerabilities
pip install safety
safety check

# Update dependencies
pip install --upgrade package_name
```

### Code Security Scanning
```bash
# Static code analysis
pip install bandit
bandit -r backend/

# Security linting
pip install flake8-security
flake8 --select=S backend/
```

### Penetration Testing
- **OWASP ZAP**: Automated security testing
- **Burp Suite**: Manual security testing
- **Nmap**: Network security scanning

## Incident Response

### Security Incident Response Plan
1. **Detection**: Automated monitoring and alerting
2. **Assessment**: Determine severity and impact
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threats and vulnerabilities
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Document and improve

### Incident Response Team
- **Security Lead**: Overall incident coordination
- **Technical Lead**: Technical response and remediation
- **Communication Lead**: Stakeholder communication
- **Legal/Compliance**: Regulatory requirements

### Emergency Contacts
```yaml
# Emergency contact list
security_team:
  - name: "Security Lead"
    email: "security@company.com"
    phone: "+1-555-0123"
  
technical_team:
  - name: "Technical Lead"
    email: "tech@company.com"
    phone: "+1-555-0124"
```

## Security Training

### Developer Training
- **Secure Coding Practices**: OWASP guidelines
- **Authentication & Authorization**: JWT and RBAC
- **Input Validation**: Preventing injection attacks
- **Error Handling**: Secure error messages

### User Training
- **Password Security**: Strong password requirements
- **Phishing Awareness**: Recognizing phishing attempts
- **Data Handling**: Proper data handling procedures
- **Incident Reporting**: How to report security issues

## Compliance

### SOC 2 Compliance
- **Security**: Implement security controls
- **Availability**: Ensure system availability
- **Processing Integrity**: Accurate data processing
- **Confidentiality**: Protect sensitive data
- **Privacy**: Protect personal information

### ISO 27001 Compliance
- **Information Security Management System (ISMS)**
- **Risk Assessment and Management**
- **Security Controls Implementation**
- **Continuous Monitoring and Improvement**

### Regular Security Audits
- **Quarterly Security Reviews**: Assess security posture
- **Annual Penetration Testing**: External security testing
- **Compliance Audits**: Regulatory compliance verification
- **Vulnerability Assessments**: Regular vulnerability scanning

## Security Checklist

### Development
- [ ] Input validation implemented
- [ ] Output encoding applied
- [ ] Authentication required for all endpoints
- [ ] Authorization checks in place
- [ ] Error handling doesn't leak information
- [ ] Logging implemented for security events
- [ ] Dependencies updated regularly

### Deployment
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Firewall rules in place
- [ ] Database access restricted
- [ ] File uploads secured
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery tested

### Operations
- [ ] Regular security updates applied
- [ ] Access logs monitored
- [ ] Incident response plan tested
- [ ] Security training completed
- [ ] Vulnerability scanning scheduled
- [ ] Penetration testing performed
- [ ] Compliance requirements met

## Security Resources

### Documentation
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Vue.js Security](https://vuejs.org/guide/best-practices/security.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### Tools
- [OWASP ZAP](https://www.zaproxy.org/)
- [Burp Suite](https://portswigger.net/burp)
- [Nmap](https://nmap.org/)
- [Bandit](https://bandit.readthedocs.io/)

### Standards
- [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html)
- [SOC 2](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/aicpasoc2report)
- [GDPR](https://gdpr.eu/)
- [CCPA](https://www.oag.ca.gov/privacy/ccpa)