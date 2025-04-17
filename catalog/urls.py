from django.urls import path
from .views import product_list

from django.http import HttpResponse

urlpatterns = [
    path('', product_list, name='product_list'),
    path('health', lambda request: HttpResponse('OK'), name='health_check')
]
