from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout

from src.settings import DEBUG



class UserMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
              
        response = self.get_response(request)
        
        return response
