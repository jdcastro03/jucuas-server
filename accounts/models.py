from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets
from django.utils import timezone


""" TODO:
Aqui:
    Meter el campo gender
En el front:
    ver si el usuario global no tiene, para que pueda completarlo
    asignarle uno en base a su(s) nombre(s)
"""

class User(AbstractUser):
    gender = models.CharField(
        default='N',
        blank=True,
        null=True,
        max_length=1,
        choices=(
            ('M', 'Mujer'),
            ('H', 'Hombre'),
            ('O', 'Otro'),
            ('N', 'No asignado'),

        )
    )
    phone = models.CharField(default="Asigna uno",max_length=10, blank=True, null=True, verbose_name='Telefono')
    


cooldown = 300
# NOTE: Pruebas para la recuperacion de contraseña
"""
def test():
    usuario = User.objects.get(pk=3775)
    token = tokens(user=usuario)
    token.generar()
    return token
"""


class tokens(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=True)

    # FIXME (COMPLETED): agregar un bool de expirado

    # Generar token
    def generate(self):
        # Genera un token aleatorio seguro de 6 caracteres
        self.token = ''.join(str(secrets.randbelow(10)) for _ in range(6))
        self.created_at = timezone.now()  # Establece la fecha y hora de creación
        self.expired = False
        self.save()

    def is_expired(self):
        now = timezone.now()
        time_difference = now - self.created_at
        return time_difference.total_seconds() >= cooldown

    def check_token(self, token):
        if not self.is_expired():
            if self.token == token:
                return "Valido"
            else:
                return "no valido"
        else:
            return "expirado"

    def validate(self, _token):
        # Contar el tiempo en segundos
        # y si es igual

        _ = {'valid': False, 'reason': 'Token '}
        _rz = self.check_token(_token)
        _['reason'] += _rz
        _['valid'] = _rz == 'Valido'
        # Si expiró automaticamente, ya retornar expirado
        return _

    # Expira el token si o si
    def expirate(self):
        self.expired = True;
        self.save()

    # Por si al proximo programador se le ocurre testear con funciones en español
    generar = lambda self: self.generate()
    validar = lambda self, token: self.validate(token)
    expirar = lambda self, token: self.expirate()

    def __str__(self):
        # generar(self)
        return f'El token de {self.user.first_name} {self.user.last_name} es {self.token} y es un {self.validate(self.token)["reason"]}'