import links; import secrets


# from django.utils import timezone
from django.shortcuts import render, redirect
from django.core.mail import send_mail
# from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives
        # EmailMessage,
import requests
import json
from decouple import config
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth.models import Group

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

# from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView


from presenter.models import Presenter
from representative.models import Representative

# from reviewer.models import Reviewer

from .models import User, tokens
from .serializers import UserSerializer #, GroupsSerializer


# from representative.serializers import RepresentativeSerializer
# from reviewer.serializers import ReviewerSerializer
AUTH_URL = config('AUTH_URL')
FRONT_URL = config('FRONT_URL')



# Funcion del Login
@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    try:
        user = User.objects.get(
            username=request.data['username'], is_active=True)
        if user:
            r = requests.post(
                f'{AUTH_URL}/o/token/',
                data={
                    'grant_type': 'password',
                    'username': request.data['username'],
                    'password': request.data['password'],
                    'client_id': config('CLIENT_ID'),
                    'client_secret': config('CLIENT_SECRET'),
                },
            )
            user.last_login = datetime.now()
            user.save()

            return Response(r.json())  # retorna el token
        else:
            return Response({'message': 'Usuario inactivo'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'status': 'Error', 'message': 'Error al iniciar sesión'}, status=status.HTTP_400_BAD_REQUEST)

# Funcion para refrescar token y no se pierda la sesion  al refrescar pagina
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):

    r = requests.post(
        f'{AUTH_URL}/o/token/',
        data={
            'grant_type': 'refresh_token',
            'refresh_token': request.data['refresh_token'],
            'client_id': config('CLIENT_ID'),
            'client_secret': config('CLIENT_SECRET'),
        },
    )
    return Response(r.json())

# Borrar token de la BD
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revoke_token(request):

    r = requests.post(
        f'{AUTH_URL}/o/revoke_token/',
        data={
            'token': request.data['token'],
            'client_id': config('CLIENT_ID'),
            'client_secret': config('CLIENT_SECRET'),
        },
    )
    if r.status_code == requests.codes.ok:
        return Response({'message': 'token revoked'}, r.status_code)
    return Response(r.json(), r.status_code)


class UserProfile(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = get_object_or_404(User, pk=request.auth.user_id)
        serializer = UserSerializer(request.user)
        # si
        s = serializer.data
        grupo = serializer.data['groups'][0]['name']
        s['gender'] = user.gender
        s['phone'] = user.phone
        return Response(s, status=status.HTTP_200_OK)

    def my_gender(self, request, data):
        user = get_object_or_404(User, pk=data.auth.user_id)
        return Response({"gender": user.profile.gender}, status=status.HTTP_200_OK)

# Obtener genero del usuario (H:♂️, M:♀️, N:?)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_gender(request):
    user = get_object_or_404(User, pk=request.auth.user_id)
    return Response({"gender": user.gender}, status=status.HTTP_200_OK)


# Dict de generos para la proxima function
genders = {'H': "o", 'M': 'a'}
# 'O': 'x'} #obsoleto porque la Eviecami es 🏳️‍⚧️ ♀️, no NB lol
# Generos pero en verbose
genders_v = {'male': genders['H'], 'female': genders['M']}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_mail(request):
    user = get_object_or_404(User, pk=request.auth.user_id)
    try:
        links.register_send_mail(user)
        return JsonResponse({'message':'Registro del usuario hecho correctamente'}, status=status.HTTP_200_OK)
    except:
        return JsonResponse({'message':'Error de registro del usuario'}, status=status.HTTP_400_BAD_REQUEST)



def check_token(request, email, token):
    tk = tokens.objects.get(
        token=token, user=User.objects.filter(email=email)[0])
    if tk.is_expired():
        return Response({"status": "error"})
    return Response({"status": "OK"})

# Funcion para recuperar contraseña


@api_view(['POST'])
@permission_classes([AllowAny])
def recovery_password(request):
    data = request.data
    no_existe = False
    # Checar que exista el usuario
    try:
        user = User.objects.filter(email=data['email'])[0]
    except User.DoesNotExist:
        return Response({"status": "error", "message": "Usuario no existente, redireccionando"})

    serializer = UserSerializer(user)
    group = serializer.data['groups'][0]['name']

    # Buscar usuario por grupo
    if group == 'admin':  # No es necesario volver a buscar
        _user = user
    elif group == 'representative':
        try:
            _user = Representative.objects.get(email__exact=data['email'])
        except User.DoesNotExist:
            no_existe = True
    elif group == 'presenter':
        try:
            _user = Presenter.objects.get(email__exact=data['email'])
        except User.DoesNotExist:
            no_existe = True
    elif group == 'reviewer':
        try:
            _user = Representative.objects.get(email__exact=data['email'])
        except User.DoesNotExist:
            no_existe = True
    if no_existe:
        return Response({"status": "error", "message": "Usuario no existente, redireccionando"})
    # Generar Nombre completo
    try:
        fn = f'{_user.first_name} {_user.last_name}'
    except:
        fn = "Estimado Usuario"
    # return Response({"status":"error","message":"Usuario no existente, redireccionando"}, status=status.HTTP_400_BAD_REQUEST)
    # Buscar la existencia de un registro token
    try:
        tk = tokens.objects.get(user=user)
    # Caso contrario, crearle un campo
    except:
        tk = tokens(user=user)
    # Generarlo si o si
    tk.generate()

    """
	TODO:
		Hacer un template para el envio de correo, para que no se
		vea muy feito
	"""
    # Modificar parametros al gusto
    email = EmailMultiAlternatives(
        subject='JucUAS - Recuperación de contraseña', from_email="",
        body=f'<h1>Hola, {fn}</h1>\n <p>Tu código de recuperación es {tk.token},\
entra a <a href="{FRONT_URL}/auth/portal_recovery/token?mail={user.email}&token={tk.token}">\
este enlace</a> para cambiar su contraseña directamente</p>',
        to=[data['email']]
    )

    email.attach_alternative(email.body, "text/html")
    email.send()
    return Response({"status": "OK", "message": "El correo de recuperacion ha sido enviado correctamente, redireccionando"})


def get_gender_by_obj(_user):
    try:
        g = genders[_user.gender]
    except:
        g = genders_v[get_gender_by_name(_user.first_name)]
    finally:
        return g

# Funcion que regresa el genero de la persona por su nombre
# Ejemplo 1: I = Jose; O = male
# Ejemplo 2: I = Evie; O = female
# Ejemplo 3: I = MinMin; O = female


def get_gender_by_name(name): return requests.get(
    f'https://api.genderize.io/?name={name}'.replace(' ', '')).json()['gender']


# Deprecated
def send_reset_password_email(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = User.objects.get(email=email)
        if user:
            # Genera un token aleatorio seguro de 20 caracteres
            token = secrets.token_hex(10)

            # Crea un registro en la base de datos para el token
            reset_token = tokens(user=user, token=token, expired=False)
            reset_token.save()

            # Envía el correo electrónico
            subject = 'Recuperación de contraseña'
            message = f'Tu código de recuperación de contraseña es: {token}'
            from_email = 'noreply@example.com'
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)

            # Redirige a una página de confirmación
            return redirect('pagina_de_confirmacion')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_password(request): return update_pass(request)


def get(id): return User.objects.get(pk=id)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_name(request):
    try:
        data = request.data
        user = get(data['id'])
        user.first_name = data['fn']
        user.last_name = data['ln']
        user.save()
        return Response({"status": "OK", "message": ""})
    except:
        return Response({"status": "error", "message": "Ha ocurrido un error"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_email(request):
    # d: {id: presentador email: correo nuevo}
    # _u: usuario general
    # u: presentador

    d = request.data
    u = get(d['id'])
    # Intenta ver si existe un usuario con el correo
    try:
        user = User.objects.get(email=d['email'])
    except:
        # Si no, lo asigna
        u.email = d['email']
        u.save()
        return Response({"status": "OK"})
    return Response({"status": "error", "message": "correo ya vinculado a otra cuenta"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_gender(request):
    try:
        data = request.data
        user = get(data['id'])
        user.gender = data['gender']
        user.save()
        return Response({"status": "OK"})
    except:
        return Response({"status": "error", "message": "Ha ocurrido un Error"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_phone(request):

    d = request.data
    u = get(d['id'])
    try:
        user = User.objects.get(phone=d['phone'])
    except:
        # Si no, lo asigna
        u.phone = d['phone']
        u.save()
        return Response({"status": "OK"})
    return Response({"status": "error", "message": "telefono ya vinculado a otra cuenta"})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def verify_exist(request):
    data = {request.data.get('type'): request.data.get('data')}
    return Response({'exists': User.objects.filter(**data).exists()},
                    status=status.HTTP_200_OK)


def validate_token(request, email, token):
    return JsonResponse(_validate_token(email, token), status=status.HTTP_200_OK)


def _validate_token(email, token):
    tk = tokens.objects.get(user=User.objects.get(email=email))

    data = tk.validate(token)
    if data['valid']:
        return {'status': 'OK'}
    return {'status': 'Error', 'reason': data['reason']}

# Actualizar la contraseña cuando no tienes nada


def verificar_token(request, email):
    token = tokens.objects.filter(user=User.objects.filter(email=email)[0])[0]
    if token.is_expired():
        print(0)
        return JsonResponse({"status": "0"})
    print('OK')
    return JsonResponse({"status": "OK"})


@api_view(['POST'])
@permission_classes([AllowAny])
def change_password_with_token(request):
    data = request.data
    return update_pass_token(data)


def update_pass_token(data):
    user = User.objects.get(email=data['email'])
    token = data['token']
    newPassword = data['pass1']
    confirmPassword = data['pass2']
    # print('user: '+str(user))
    # print('token: '+token)
    # print('New pass2: '+confirmPassword)
    # print('New pass1: '+newPassword)

    validacion = validate_password(newPassword, confirmPassword)
    # print('validacion: '+str(validacion))
    if validacion[0]['status'] == 'Error':
        return Response(validacion[0], status=validacion[1])
    try:
        tk = tokens.objects.get(user=user)
        _token = tk.validar(token)
        if not _token['valid']:
            return Response({'status': 'error', 'message': 'Token no valido'}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'status': 'error', 'message': 'Token no existente'}, status=status.HTTP_400_BAD_REQUEST)

    change_password(user, newPassword)
    tk.expirate()
    return Response({'status': 'OK', 'message': 'Contraseña modificada correctamente'}, status=status.HTTP_200_OK)

# Actualizar contraseña teniendola a la mano logeado


def update_pass(request):
    '''
    Method to update user password.
    {"actual_password": "password", "passwd1": "password1" , "passwd2": "password1"}
    '''
    data = request.data
    user = get_object_or_404(User, pk=request.auth.user_id)
    actual_password = str(data.get('actual_password', ''))
    passwd1 = str(data.get('passwd1', ''))
    passwd2 = str(data.get('passwd2', ''))

    if not user.check_password(data.get('actual_password', None)):
        return Response({'status': 'Error', 'message': 'Contraseña incorrecta'}, status=status.HTTP_400_BAD_REQUEST)

    validacion = validate_password(passwd1, passwd2)
    if validacion[0]['status'] == 'error':
        return Response(validacion[0], status=validacion[1])
    if passwd1 == actual_password:
        return Response({'status': 'Error', 'message': 'La nueva contraseña es igual a la anterior'}, status=status.HTTP_400_BAD_REQUEST)

    change_password(user, passwd1)
    return Response({'status': 'OK', 'message': 'Contraseña modificada correctamente'}, status=status.HTTP_200_OK)
# http://localhost:4200/auth/portal_recovery/token?mail=pcvvblah@gmail.com&token=082640


def validate_password(passwd1, passwd2):
    if (passwd1 != passwd2) and (passwd1 != '') and (passwd2 != ''):
        return [{'status': 'Error', 'message': 'Las contraseñas no coinciden'}, status.HTTP_400_BAD_REQUEST]
    elif (passwd1 == ''):
        return [{'status': 'Error', 'message': 'Campo passwd1 vacio'}, status.HTTP_400_BAD_REQUEST]
    elif (passwd2 == ''):
        return [{'status': 'Error', 'message': 'Campo passwd2 vacio'}, status.HTTP_400_BAD_REQUEST]

    return [{'status': 'OK'}, status.HTTP_200_OK]


def change_password(user, pw):
    user.set_password(pw)
    user.save()

