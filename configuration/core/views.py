from typing import Any

from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib import messages
class IndexView(TemplateView):
    template_name = "core/index.html"
    
