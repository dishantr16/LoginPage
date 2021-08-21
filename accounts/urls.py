from django.urls import path, include, re_path
# from knox import views as knox_views
from .views import ValidatePhoneSendOTP

app_name = 'accounts'

urlpatterns = [
    re_path('^validate_phone/', ValidatePhoneSendOTP.as_view()),
]
