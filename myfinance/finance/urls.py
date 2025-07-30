from django.urls import path
from .views import Posttranisiton, Loginuser,dashboard,bar_graph,pie_chart,single_transitionpage
from .auth_views import *

urlpatterns = [
    path("create/", Posttranisiton),
    path("register/", Register, name="register"),
    path("verify_otp/", VerifyOTP, name="verify_otp"),  # Added OTP verification URL
    path("login/", Login, name="login"),
    path("logout/", Logout, name="logout"),
    path('dashboard/', dashboard, name='dashboard'),
    path('barchart/',bar_graph,name='bar_graph'),
    path('piechart/',pie_chart,name='pie_chart'),
    path('transaction/<int:transaction_id>/',single_transitionpage, name='single_transaction'),
    path('', dashboard, name='home')
]
