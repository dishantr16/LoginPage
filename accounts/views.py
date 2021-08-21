from django.shortcuts import render
from django.http import HttpResponse
import http.client
# Create your views here.
import json
import requests
import ast

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status, generics
# from forms import UserForm
from .models import User, PhoneOTP
from django.shortcuts import get_object_or_404, redirect
import random
# from .serializer import CreateUserSerializer, LoginSerializer
# from knox.views import LoginView as KnoxLoginView
# from knox.auth import TokenAuthentication
# from rest_framework.authentication import SessionAuthentication, BasicAuthentication
# from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import login, logout

conn = http.client.HTTPConnection("2factor.in")


class ValidatePhoneSendOTP(APIView):

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        password = request.data.get('password', False)
        username = request.data.get('username', False)
        email = request.data.get('email', False)

        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact=phone)
            if user.exists():
                return Response({
                    'status': False,
                    'detail': 'Phone number already exists'
                })

            else:
                key = send_otp(phone)
                if key:
                    old = PhoneOTP.objects.filter(phone__iexact=phone)
                    if old.exists():
                        old = old.first()
                        count = old.count
                        if count > 10:
                            return Response({
                                'status': False,
                                'detail': 'Sending otp error. Limit Exceeded. Please Contact Customer support'
                            })

                        old.count = count + 1
                        old.save()
                        print('Count Increase', count)

                        conn.request("GET",
                                     "https://2factor.in/API/R1/?module=SMS_OTP&apikey=f0c241f6-025e-11ec-a13b-0200cd936042=" + phone + "&otpvalue=" + str(
                                         key) + "&templatename=Casper")
                        res = conn.getresponse()

                        data = res.read()
                        data = data.decode("utf-8")
                        data = ast.literal_eval(data)

                        if data["Status"] == 'Success':
                            old.otp_session_id = data["Details"]
                            old.save()
                            print('In validate phone :' + old.otp_session_id)
                            return Response({
                                'status': True,
                                'detail': 'OTP sent successfully'
                            })
                        else:
                            return Response({
                                'status': False,
                                'detail': 'OTP sending Failed'
                            })




                    else:

                        obj = PhoneOTP.objects.create(
                            phone=phone,
                            otp=key,
                            email=email,
                            username=username,
                            password=password,
                        )
                        conn.request("GET",
                                     "https://2factor.in/API/R1/?module=SMS_OTP&apikey=f0c241f6-025e-11ec-a13b-0200cd936042=" + phone + "&otpvalue=" + str(
                                         key) + "&templatename=Casper")
                        res = conn.getresponse()
                        data = res.read()
                        print(data.decode("utf-8"))
                        data = data.decode("utf-8")
                        data = ast.literal_eval(data)

                        if data["Status"] == 'Success':
                            obj.otp_session_id = data["Details"]
                            obj.save()
                            print('In validate phone :' + obj.otp_session_id)
                            return Response({
                                'status': True,
                                'detail': 'OTP sent successfully'
                            })
                        else:
                            return Response({
                                'status': False,
                                'detail': 'OTP sending Failed'
                            })


                else:
                    return Response({
                        'status': False,
                        'detail': 'Sending otp error'
                    })

        else:
            return Response({
                'status': False,
                'detail': 'Phone number is not given in post request'
            })


def send_otp(phone):
    if phone:
        key = random.randint(999, 9999)
        print(key)
        return key
    else:
        return False
