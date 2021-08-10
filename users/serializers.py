from django.contrib.auth.password_validation import validate_password, get_password_validators
from django.conf import settings
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from accounts.models import Account
from accounts.serializers import AccountSerializer
from users.models import User
from users.signals import pre_password_reset, post_password_reset
from helpers.mailers import send_user_activation_mail
from helpers.utils import validate_token
from knox.models import AuthToken


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,
                validators=[UniqueValidator(queryset=User.objects.all(),
                message='User with this email already exists')])
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField(required=True)
    country = serializers.CharField(required=False)
    account_name = serializers.CharField(write_only=True)
    accounts = serializers.SerializerMethodField(read_only=True)


    def get_accounts(self, obj):
        accounts = obj.accounts.all()
        data = AccountSerializer(accounts, many=True).data
        return data
    
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'country', 'account_name', 'accounts']

    def create(self, validated_data):
        name = validated_data.pop('account_name')
        user = User.objects.create(**validated_data)
        account = Account.objects.create(name=name)
        user.accounts.add(account)
        AuthToken.objects.create(user=user, account=account)
        return user

class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'country']

    def update(self, instance, validated_data):       
        for attr, value in validated_data.items():
            if not value:
                value = instance.attr
            setattr(instance, attr, value) 
       
        instance.save()
        return instance    


class UserInvitationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True,
                validators=[UniqueValidator(queryset=User.objects.all(),
                message='User with this email already exists')])
    role = serializers.CharField()
    account_number = serializers.CharField()

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inviter = user

    def validate_account_number(self, value):
        try:
            account = Account.objects.get(account_number=value)
            self.account = account
            return value
        except Account.DoesNotExist:
            raise serializers.ValidationError('The account_number is not valid')    

    def invite(self):
        role = self.validated_data.pop('role') # use role for?
        self.validated_data.pop('account_number')

        user = User.objects.create(**self.validated_data, is_active=False)
        user.accounts.add(self.account)
        send_user_activation_mail(user, self.account.name)
        return user


class TokenValidateMixin:
    def validate(self, data):
        token = data.get('token')
        uid = data.get('uid')

        user, is_valid = validate_token(uid, token)
        if not (user and is_valid):
            raise serializers.ValidationError("The token entered is not valid. Please check and try again.")
        self.user = user

        password = data.get('password')
        if password:
            try:
                validate_password(
                    password=password,
                    user=self.user,
                    password_validators=get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)
                )
            except Exception as e:
                raise serializers.ValidationError(e)
        return data


class ResetPasswordConfirmSerializer(TokenValidateMixin, serializers.Serializer):
    password = serializers.CharField()
    token = serializers.CharField()
    uid = serializers.CharField()

    def reset_password(self):
        password = self.validated_data.get('password')
        
        pre_password_reset.send(sender=self.__class__, user=self.user)
    
        self.user.set_password(password)
        self.user.save()

        post_password_reset.send(sender=self.__class__, user=self.user)

        return


class ValidateTokenSerializer(TokenValidateMixin, serializers.Serializer):
    token = serializers.CharField()
    uid = serializers.CharField()


class ActivateInvitedUserSerializer(serializers.Serializer):
    uid = serializers.CharField()
    password = serializers.CharField()

    def validate_uid(self, value):
        try:
            user_id = force_text(urlsafe_base64_decode(value))
            user = User.objects.get(pk=user_id)
            self.user = user
        except User.DoesNotExist:
            raise serializers.ValidationError(detail='The uid entered is not valid')

    def validate_password(self, value):
        try:
            validate_password(
                password=value,
                user=self.user,
                password_validators=get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)
            )
        except Exception as e:
            raise serializers.ValidationError(e) 

    def activate(self):
        password = self.validated_data['password']
        self.user.is_active=True
        self.user.set_password(password)
        self.user.save()
        return self.user