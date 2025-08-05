from django.db import models

from django.contrib.auth.models import User
# Create your models here.

class DocumentoPDF(models.Model):
    titulo = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='pdfs/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Empleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    es_admin = models.BooleanField(default=False)  # Puedes marcar aquí si es admin

    def __str__(self):
        return self.user.username
    


class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    attempts = models.IntegerField(default=0)
    permanently_blocked = models.BooleanField(default=False)

    def increment_attempt(self):
        """Incrementa el contador de intentos fallidos."""
        self.attempts += 1
        self.save()

    def reset_attempts(self):
        """Restablece los intentos de la IP a 0."""
        self.attempts = 0
        self.save()

    def is_blocked(self):
        """Devuelve True si la IP debe ser bloqueada permanentemente."""
        return self.permanently_blocked

    def block_permanently(self):
        """Marca la IP como permanentemente bloqueada."""
        self.permanently_blocked = True
        self.save()

    def __str__(self):
        return f"{self.ip_address} - Attempts: {self.attempts} - Blocked: {self.permanently_blocked}"
