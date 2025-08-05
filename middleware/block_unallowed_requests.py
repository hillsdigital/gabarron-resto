# middleware/block_unallowed_requests.py
import re
import logging
from datetime import datetime
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import resolve, Resolver404, reverse
from documentos.models import BlockedIP  # Ajusta la importación según tu app

logger = logging.getLogger(__name__)

SUSPICIOUS_PATHS = [
    r"/wp-includes", r"/xmlrpc.php", r"/admin", r"/solr", r"/login", r"\.php",
    r"\.env", r"\.git/", r"\.gitignore", r"\.htaccess", r"\.config", r"/config",
    r"/etc/passwd", r"/.ssh/", r"/.env", r"/composer\.json", r"/vendor/phpunit",
    r"\bselect\b.*\bfrom\b",  # Inyección SQL
    r"\b<script\b.*\b>\b",     # XSS
    r"union.*select.*from",    # SQL Injection
]

ALLOWED_PUBLIC_PATHS = [
    r"^/$",
    r"^/acceso-privado-2024/?$",
    r"^/favicon\.ico$",
    r"^/visor-pdf/\d+/?$",   # <-- Esto permite /visor-pdf/1/ /visor-pdf/2/ etc.
]


MAX_ATTEMPTS = 3

class BlockUnallowedRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        path = request.path

        # Permitir superusuarios autenticados sin restricción
        if request.user.is_authenticated and request.user.is_superuser:
            return self.get_response(request)

        blocked_ip = self.get_or_create_ip(ip)

        # Si IP está bloqueada, denegar acceso
        if blocked_ip.is_blocked():
            return HttpResponseForbidden("Acceso denegado: Tu IP está bloqueada.")

        # Permitir rutas públicas específicas
        if any(re.match(p, path) for p in ALLOWED_PUBLIC_PATHS):
            return self.get_response(request)

        # Verificar si la ruta existe en Django
        if not self.is_allowed_url(path) or self.is_suspicious_path(path):
            self.log_unauthorized_attempt(request)
            blocked_ip.increment_attempt()
            if blocked_ip.attempts >= MAX_ATTEMPTS:
                blocked_ip.block_permanently()
                logger.warning(f"IP {ip} bloqueada permanentemente por múltiples intentos sospechosos.")
            return HttpResponseForbidden("Acceso denegado: Ruta no permitida o sospechosa.")

        # Si no está autenticado, redirigir a home y registrar intento
        if not request.user.is_authenticated:
            self.log_unauthorized_attempt(request)
            return HttpResponseRedirect(reverse('home'))

        return self.get_response(request)

    def get_or_create_ip(self, ip):
        obj, _ = BlockedIP.objects.get_or_create(ip_address=ip)
        return obj

    def is_allowed_url(self, path):
        try:
            resolve(path)
            return True
        except Resolver404:
            return False

    def is_suspicious_path(self, path):
        return any(re.search(pattern, path, re.IGNORECASE) for pattern in SUSPICIOUS_PATHS)

    def log_unauthorized_attempt(self, request):
        ip = self.get_client_ip(request)
        path = request.path
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        logger.warning(f"{timestamp} - IP: {ip} - Intento de acceso no autorizado a: {path} - User-Agent: {user_agent}")

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Considera que el primer IP es el cliente real
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
