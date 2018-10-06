from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from core.constants import MESSAGES
from core.enums import StatusCode
from core.utils import get_site_url


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    def get_email(self, obj):
        return obj.email
    class Meta:
        model = User
        exclude = ('password', 'last_login', 'created', 'modified', 'is_active', 'is_admin')

    def to_internal_value(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')
        if data.get('is_admin'):
            data['is_admin'] = False
        if data.get('password'):
            raise serializers.ValidationError(
                {'message': MESSAGES[StatusCode.NEW_PASSWORD_IS_INVALID], 'code': StatusCode.NEW_PASSWORD_IS_INVALID.value})
        if not phone_number:
            raise serializers.ValidationError(
                {'message': MESSAGES[StatusCode.PHONE_NUMBER_IS_INVALID], 'code': StatusCode.PHONE_NUMBER_IS_INVALID.value})
        if not first_name:
            raise serializers.ValidationError(
                {'message': MESSAGES[StatusCode.FIRST_NAME_IS_EMPTY], 'code': StatusCode.FIRST_NAME_IS_EMPTY.value})
        if not last_name:
            raise serializers.ValidationError(
                {'message': MESSAGES[StatusCode.LAST_NAME_IS_EMPTY], 'code': StatusCode.LAST_NAME_IS_EMPTY.value})
        elif not email:
            raise serializers.ValidationError(
                {'message': MESSAGES[StatusCode.EMAIL_ADDRESS_IS_EMPTY], 'code': StatusCode.EMAIL_ADDRESS_IS_EMPTY.value})
        data['email'] = email
        return data


class NewUserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key

    def get_email(self, obj):
        return obj.email

    def get_profile_picture(self, obj):
        return '%s%s%s'%(get_site_url(),settings.MEDIA_URL,obj.profile_picture)

    class Meta:
        model   = User
        exclude = ('password', 'is_active', 'last_login','created', 'modified', 'is_admin')