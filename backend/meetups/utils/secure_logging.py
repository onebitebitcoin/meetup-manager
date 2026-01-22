"""
Secure logging utilities that prevent sensitive data leakage
"""
import logging

# Configure secure logger
logger = logging.getLogger('meetups.security')

def _get_setting(setting_name, default=None):
    """Safely get Django setting without crashing if not configured"""
    try:
        from django.conf import settings
        return getattr(settings, setting_name, default)
    except:
        return default

def log_korean_conversion(username, action="login"):
    """
    Securely log Korean input conversion events without exposing sensitive data.
    
    Args:
        username: The username (safe to log)
        action: The action being performed (login/registration)
    """
    # Only log if not in production or if debug logging is explicitly enabled
    debug_mode = _get_setting('DEBUG', False)
    log_conversion = _get_setting('LOG_KOREAN_CONVERSION', False)

    if debug_mode or log_conversion:
        logger.info(f"Korean input conversion applied - User: {username}, Action: {action}")

    # In production, we might want to increment a metric instead of logging
    # This could be sent to monitoring systems like DataDog, NewRelic, etc.
    metrics_client = _get_setting('METRICS_CLIENT', None)
    if metrics_client:
        metrics_client.increment('korean_conversion.applied', tags=[f'action:{action}'])

def log_authentication_attempt(username, success=True, method="standard"):
    """
    Securely log authentication attempts without sensitive data.
    
    Args:
        username: The username attempting to authenticate
        success: Whether authentication succeeded
        method: Authentication method (standard, korean_converted, etc.)
    """
    debug_mode = _get_setting('DEBUG', False)
    if debug_mode:
        logger.info(f"Auth attempt - User: {username}, Success: {success}, Method: {method}")

    # Production logging - no sensitive data
    metrics_client = _get_setting('METRICS_CLIENT', None)
    if metrics_client:
        status = 'success' if success else 'failure'
        metrics_client.increment(f'auth.{status}', tags=[f'method:{method}'])

def secure_log(message, level="info", include_in_production=False):
    """
    Utility for secure logging that respects production security requirements.
    
    Args:
        message: Log message (ensure it contains no sensitive data)
        level: Log level (info, warning, error)
        include_in_production: Whether to log in production
    """
    debug_mode = _get_setting('DEBUG', False)
    if debug_mode or include_in_production:
        log_func = getattr(logger, level, logger.info)
        log_func(message)
