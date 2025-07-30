from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
import random

# Utility functions for OTP
def generate_otp(length=6):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def send_otp_email(email, otp):
    subject = "Your OTP Verification Code"
    message = f"Your OTP code is: {otp}"
    from_email = "aashish1347@xavier.edu.np"  # Replace with your Gmail address
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

# Register View with OTP send
def Register(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        username = request.POST.get("username", "").strip()

        # Validate all fields
        if not all([first_name, last_name, email, password, username]):
            messages.error(request, "All fields are required.")
            return redirect("register")

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address.")
            return redirect("register")

        # Check duplicates
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        # Generate and send OTP
        otp = generate_otp()
        try:
            send_otp_email(email, otp)
        except Exception as e:
            messages.error(request, f"Failed to send OTP email: {e}")
            return redirect("register")

        # Store registration info + OTP in session
        request.session['registration_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'username': username,
            'password': password,
            'otp': otp,
        }

        messages.info(request, "OTP sent to your email. Please verify to complete registration.")
        return redirect("verify_otp")

    return render(request, "auth/register.html")

# OTP Verification View
def VerifyOTP(request):
    if request.method == "POST":
        user_otp = request.POST.get("otp", "").strip()
        registration_data = request.session.get('registration_data')

        if not registration_data:
            messages.error(request, "Session expired or no registration data found. Please register again.")
            return redirect("register")

        if user_otp == registration_data.get('otp'):
            try:
                user = User.objects.create_user(
                    username=registration_data['username'],
                    email=registration_data['email'],
                    first_name=registration_data['first_name'],
                    last_name=registration_data['last_name'],
                    password=registration_data['password'],
                )
                user.save()
                del request.session['registration_data']
                messages.success(request, "Registration complete! You can now log in.")
                return redirect("login")
            except IntegrityError:
                messages.error(request, "User already exists or invalid data.")
                return redirect("register")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return redirect("register")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect("verify_otp")

    return render(request, "auth/verify_otp.html")

# Login View
def Login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            messages.error(request, "Please fill in all fields.")
            return redirect("login")

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return redirect("login")

        # Authenticate user
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect("home")
            else:
                messages.error(request, "Invalid email or password.")
        except User.DoesNotExist:
            messages.error(request, "No user with that email found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
        return redirect("login")

    return render(request, "auth/login.html")

# Logout View
def Logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")