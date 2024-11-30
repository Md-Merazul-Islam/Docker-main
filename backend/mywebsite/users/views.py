import random
from django.core.mail import send_mail
from rest_framework import generics, status, permissions
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import UserProfile
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import authenticate, login, logout
from .serializers import UserRegisterSerializer, UserLoginSerializer, VerifyEmailSerializer, UserProfileSerializer, SendOTPSerializer, ResetPasswordSerializer, VerifiedUserSerializer
from rest_framework.permissions import AllowAny, IsAdminUser
from django.utils.html import format_html

from django.core.exceptions import ValidationError


def generate_OTP():
    return str(random.randint(100000, 999999))


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        otp = generate_OTP()
        user_profile = user.userprofile
        user_profile.otp = otp
        user_profile.is_verified = False
        user_profile.save()

        # Format the email message with HTML
        html_message = format_html(
            '<p>OTP Verification is:</p>'
            '<h1 style="font-size:24px; color:#333;">{}</h1>'
            '<p>Please use this OTP for verification within the next 5 minutes.</p>', otp
        )

        try:
            # Send the OTP email
            send_mail(
                'OTP Verification',
                '',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=html_message,
            )

        except Exception as e:
            # Handle email send error
            raise ValidationError(
                {"email": f"Error sending OTP email: {str(e)}"},
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {"message": "User registered successfully. Check your email for the OTP."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserVerifyEmailView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            try:
                user = User.objects.get(email=email)
                user_profile = user.userprofile
                if user_profile.otp == otp:
                    user_profile.is_verified = True
                    user_profile.otp = None
                    user_profile.save()
                    return Response({'message': 'Email verified successfully!'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username_or_email = serializer.validated_data['username_or_email']
        password = serializer.validated_data['password']

        # authenticate using either email or username
        user = self.authenticate_user(username_or_email, password)

        if user:
            user_profile = user.userprofile
            if user_profile.is_verified:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'user_id': user.id,
                    'user_name': user.username

                }, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Email not verified'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    def authenticate_user(self, username_or_email, password):
        """
        Authenticate user by either email or username
        """
        # First try to authenticate by username
        user = authenticate(username=username_or_email, password=password)
        if not user:
            # If no user found, try to authenticate by email
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(
                    username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        return user


class UserLogOutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            # Access 'refresh' key properly from request.data
            refresh_token = request.data.get("refresh", None)

            if refresh_token is None:
                return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token to log the user out
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidToken:
            return Response({'detail': 'Invalid token provided.'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Get currently authenticated user
        return UserProfile.objects.get(user=self.request.user)

    def get(self, request, *args, **kwargs):
        # Handle GET request to fetch the user's profile data
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class SendOTPView(generics.GenericAPIView):
    serializer_class = SendOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Save the OTP and send the email
                serializer.save()
                return Response(
                    {"detail": "OTP has been sent to your email."},
                    status=status.HTTP_200_OK
                )
            except serializers.ValidationError as e:
                # Catch and return validation errors
                return Response(
                    {"errors": e.detail},  # e.detail will give the error message
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                # Catch any general exceptions and return a 500 error
                return Response(
                    {"errors": f"An unexpected error occurred: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(
                {"errors": serializer.errors},  # Return the serializer validation errors
                status=status.HTTP_400_BAD_REQUEST
            )


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.context['user'] = user
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Password reset successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifiedUserListView(generics.ListAPIView):
    serializer_class = VerifiedUserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return User.objects.filter(userprofile__is_verified=True)
