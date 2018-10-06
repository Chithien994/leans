from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import gettext as _
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import csrf_exempt
from rest_framework.authtoken.models import Token

from api.serializers import NewUserSerializer
from core.enums import StatusCode
from core.constants import MESSAGES
from core.utils import get_site_url, is_email, \
    send_email, validate_user_data, iHttpResponse, objectResponse

User = get_user_model()

def userResponse(user):
  	return objectResponse(NewUserSerializer(user).data)

@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def signup(request):
	"""
	Signup new user
	With body: 
	{
	    "country_code":"string",
	    "phone_number":"string",
	    "email":"string",
	    "password":"string",
	    "first_name":"string",
	    "last_name":"string"
	}
	"""
	email = request.data.get('email')
	password = request.data.get('password')
	phone_number = request.data.get('phone_number')
	first_name = request.data.get('first_name')
	last_name = request.data.get('last_name')
	code, message = validate_user_data(request.data)
	if code and message:
	    return iHttpResponse(code,message)
	if User.objects.filter(email=email).exists():
	    return iHttpResponse(400,'This email already exists in our system')

	if not User.objects.filter(phone_number=phone_number).exists():
	    user = User.objects.create_user(
	        email, first_name, last_name, phone_number, password)
	    obj={"email":user.email,"phone_number":user.phone_number}
	    return objectResponse(obj)
	return iHttpResponse(400,'This phone number already exists in our system')

@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def login(request):
	"""
	Login
	With body: 
	{
	    "phone_number":"string",
	    "password":"string"
	}
	"""
	phone_number = request.data.get('phone_number')

	if User.objects.filter(phone_number=phone_number).exists():
	    password = request.data.get('password')
	    user = User.objects.get(phone_number=phone_number)
	    if user.check_password(password):
	        return userResponse(user)
	    else:
	        return iHttpResponse(StatusCode.PASSWORD_IS_INVALID.value,MESSAGES[StatusCode.PASSWORD_IS_INVALID])
	else:
	    return iHttpResponse(StatusCode.PHONE_NUMBER_IS_INVALID.value,MESSAGES[StatusCode.PHONE_NUMBER_IS_INVALID])


@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.AllowAny,))
def forgotpassword(request):
    """
    forgot password
    With body: 
    {
        "email":"string"
    }
    """
    print('forgotpassword', settings.EMAIL_HOST_PASSWORD, settings.EMAIL_HOST_USER)
    SITE_URL = get_site_url()
    email_address = request.data.get('email')
    code, message = None, None
    if not email_address:
        code = StatusCode.EMAIL_ADDRESS_IS_EMPTY.value
        message = MESSAGES[StatusCode.EMAIL_ADDRESS_IS_EMPTY]
    elif email_address and not is_email(email_address):
        code = StatusCode.EMAIL_ADDRESS_IS_INVALID.value
        message = MESSAGES[StatusCode.EMAIL_ADDRESS_IS_INVALID]
    else:
        if User.objects.filter(email=email_address).exists():
            user = User.objects.get(email=email_address)
            subject = "Password Reset"
            message_html = "email/reset_password.html"
            email_from = ""
            email_to = [user.email]

            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            obj_model = {
                'phone_number': user.phone_number,
                'full_name': user.full_name,
                'reset_pass_url': SITE_URL + reverse('resetpassword',
                                                     kwargs={'uidb64': str(uidb64, 'utf-8'), 'token': token})
            }
            print('reset_pass_url', obj_model['reset_pass_url'])
            send_email(subject, message_html, email_from, email_to, obj_model)
            code = 200
            message = _('Please check your email to get the new password!')
        else:
            code = StatusCode.EMAIL_ADDRESS_IS_INVALID.value
            message = MESSAGES[StatusCode.EMAIL_ADDRESS_IS_INVALID]
    return iHttpResponse(code, message)

@api_view(['POST'])
@csrf_exempt
@permission_classes((permissions.IsAuthenticated,))
def changepassword(request):
    """
    change password
    With body: 
    {
        "old_password":"string",
        "new_password":"string"
    }
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    code, message = None, None
    if not old_password or not user.check_password(old_password):
        code = StatusCode.OLD_PASSWORD_IS_INVALID.value
        message = MESSAGES[StatusCode.OLD_PASSWORD_IS_INVALID]
    elif not new_password:
        code = StatusCode.NEW_PASSWORD_IS_INVALID.value
        message = MESSAGES[StatusCode.NEW_PASSWORD_IS_INVALID]
    else:
        code, message = 200, _('Your password has been changed successfully!')
        user.set_password(new_password)
        user.save()
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        obj = "{'code': code, 'message': message, 'token': token.key}"
        return objectResponse(obj)
    return iHttpResponse(code, message)