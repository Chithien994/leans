# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import permission_classes
from rest_framework import exceptions, filters, viewsets, permissions
from rest_framework.authentication import BasicAuthentication, \
    SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from core.forms import ChangePasswordForm
from core.utils import get_site_url, iHttpResponse
from api.serializers import UserSerializer
from api.permissions import IsOwnerOrReadOnly

User = get_user_model()

class CustomTokenAuthentication(TokenAuthentication):
    model = Token
    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (token.user, token)
		

class UserViewSet(viewsets.ModelViewSet):
    queryset                = User.objects.none()
    serializer_class        = UserSerializer
    permission_classes      = [IsOwnerOrReadOnly]
    authentication_classes  = [CustomTokenAuthentication,
    						SessionAuthentication, BasicAuthentication]
    filter_backends         = (filters.OrderingFilter,)
    ordering_fields         = '__all__'

    def get_queryset(self):
        try:
            user = self.request.user
            if user.is_admin:
                return User.objects.all()
            return User.objects.filter(pk=user.id)
        except Exception as e:
            print(e)
        return User.objects.none()
        


def reset_password(request, uidb64, token):
    user_id = urlsafe_base64_decode(uidb64)
    user    = User.objects.get(pk=user_id)
    password_change_form = ChangePasswordForm()
    msg     = ''
    if not user:
        return render(request, 'frontend/reset_password_invalid.html', {})

    math = default_token_generator.check_token(user, token)
    if not math:
        return render(request, 'frontend/reset_password_invalid.html', {})
    if request.method == 'POST':
        password_change_form = ChangePasswordForm(request.POST)
        if password_change_form.is_valid():
            password = request.POST.get('password', '').strip()
            if user:
                math = default_token_generator.check_token(user, token)
                if math:
                    user.set_password(password)
                    user.save()
                    return render(request, 'frontend/reset_password_successfully.html', {})

    return render(request, 'frontend/reset_password.html',
                  {'uidb64': uidb64, 'token': token, 'msg': msg, 'password_change_form': password_change_form})
