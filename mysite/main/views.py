from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Controller, Channel, Program
from operator import add

@login_required
def index(request):
    return render(request, 'main/index.html',
                  {
                      'controllers': Controller.objects.all()
                  })

@login_required
def reports(request):
    return render(request, 'main/reports.html')

def get_day(start, l):
    out = []
    for i in range(24):
        if start <= i < (start + l):
            out.append(1)
        else:
            out.append(0)
    return out

def get_h_len(t_max):
    l = t_max // 60
    if t_max % 60 > 0:
        l += 1
    return l

def get_week(chn):
    prgs = Program.objects.filter(channel=chn)
    out = []
    for i in range(7):
        out.append([])
        for j in range(24):
            out[i].append(0)
    for p in prgs:
        days = list(p.days)
        for d in days:
            for i, h in enumerate(get_day(p.hour, get_h_len(p.t_max))):
                if out[int(d)-1][i] == 0:
                    out[int(d) - 1][i] += h

    return out


@login_required
def controller(request, prefix):
    programs = Program.objects.filter(channel__controller__prefix=prefix)
    channels = Channel.objects.filter(controller__prefix=prefix)
    lines = []
    for chn in channels:
        lines.append(get_week(chn))



    return render(request, 'main/controller.html',
                  {
                      'prefix': prefix,
                      'lines_week': lines
                   })

@login_required
def controller_day(request, prefix, day):
    render(request, 'main/controller_day')
