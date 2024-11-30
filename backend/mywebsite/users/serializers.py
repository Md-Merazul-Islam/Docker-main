from django.contrib.auth.models import User
from rest_framework import serializers, status
from .models import UserProfile
import random
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.html import format_html


class UserRegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password1', 'password2', 'phone_number', 'address', 'image']

        def validate(self, data):
            # Check if passwords match
            if data['password1'] != data['password2']:
                raise ValidationError(
                    {"password": "Passwords do not match."},
                    code=status.HTTP_400_BAD_REQUEST
                )

            # Check if the email already exists
            if User.objects.filter(email=data['email']).exists():
                raise ValidationError(
                    {'email': "Email already exists!"},
                    code=status.HTTP_409_CONFLICT
                )

            return data

    def create(self, validated_data):
        password = validated_data.pop('password1')
        validated_data.pop('password2')

        phone_number = validated_data.pop('phone_number', None)
        address = validated_data.pop('address', None)
        image = validated_data.pop('image', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=password
        )

        # Update UserProfile
        user_profile = user.userprofile
        user_profile.phone_number = phone_number
        user_profile.address = address
        user_profile.image = image
        user_profile.is_verified = False
        user_profile.save()

        return user


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class UserLoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        fields = ['username_or_email', 'password']


class UserProfileSerializer(serializers.ModelSerializer):
    # Including user fields from the User model
    first_name = serializers.CharField(
        source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email',
                  'phone_number', 'address', 'image']

    def update(self, instance, validated_data):
        # Update user fields
        user_data = validated_data.pop('user', {})
        if 'first_name' in user_data:
            instance.user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            instance.user.last_name = user_data['last_name']
        if 'email' in user_data:
            instance.user.email = user_data['email']

        # Update UserProfile fields
        instance.phone_number = validated_data.get(
            'phone_number', instance.phone_number)
        instance.address = validated_data.get('address', instance.address)
        instance.image = validated_data.get('image', instance.image)

        # Save both user and user profile instances
        instance.user.save()
        instance.save()
        return instance


def generate_otp():
    return str(random.randint(200000, 999999))


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Validates the email to check if a user exists with that email.
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('No user is associated with this email address.')
        return value

    def save(self):
        email = self.validated_data['email']
        try:
            user = User.objects.get(email=email)
            otp = generate_otp()

            user_profile = user.userprofile
            user_profile.otp = otp
            user_profile.otp_timestamp = timezone.now()
            user_profile.save()

            html_message = format_html(
                '<p>Your One Time Password (OTP) is:</p>'
                '<h1 style="font-size:24px;">{}</h1>'
                '<p>Please use this OTP within 5 minutes, or it will expire.</p>', otp
            )

            send_mail(
                'Your new password OTP',
                '',
                'noreply@example.com',
                [email],
                fail_silently=False,
                html_message=html_message,
            )

        except User.DoesNotExist:
            # Handle the case where the user is not found
            raise serializers.ValidationError(
                'No user is associated with this email address.')
        except Exception as e:
            # Handle any other errors that may occur (e.g., issues with sending email)
            raise serializers.ValidationError(
                f"An error occurred while sending the OTP: {str(e)}")


class ResetPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_otp(self, value):
        try:
            user_profile = UserProfile.objects.get(otp=value)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError('Invalid OTP.')

        if timezone.now() > user_profile.otp_timestamp + timedelta(minutes=5):
            raise serializers.ValidationError('OTP Expired.')
        self.context['user_profile'] = user_profile
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError('Passwords do not match.')
        return attrs

    def save(self):
        user_profile = self.context['user_profile']
        new_password = self.validated_data['new_password']
        user = user_profile.user
        user.set_password(new_password)
        user.save()

        # Clear OTP fields after password reset
        user_profile.otp = None
        user_profile.otp_timestamp = None
        user_profile.save()


class VerifiedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
