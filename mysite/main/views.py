from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, 'main/index.html')

@login_required
def reports(request):
    return render(request, 'main/reports.html')

@login_required
def pump(request):
    return render(request, 'main/pump.html')