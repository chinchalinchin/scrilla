from django.shortcuts import render
from django.http import JsonResponse

def risk_return(request):
    return JsonResponse({'message': 'test successful'}, safe=False)

def optimize(request):
    return JsonResponse({'message': 'other test successful'}, safe=False)