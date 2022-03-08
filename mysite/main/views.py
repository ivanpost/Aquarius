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

def get_day_sum(prgs, day):
    return map(add, )

@login_required
def controller(request, prefix):
    programs = Program.objects.filter(channel__controller__prefix=prefix)
    channels = Channel.objects.filter(controller__prefix=prefix)
    lines = [[[0] * 24] * 7] * len(channels)
    chns = []
    '''
    print(programs)
    for pr in programs:
        days = list(pr.days)
        print(days)
        for d in days:
            l = pr.t_max // 60
            if pr.t_max % 60 > 0:
                l += 1
            print(l)
            for h in range(pr.hour, pr.hour + l + 1):
                lines[pr.channel.id-1][int(d)-1][h] = 1

    for line in lines:
        print(line)
    '''
    return render(request, 'main/controller.html',
                  {
                      'prefix': prefix,
                      'lines_week': lines
                   })

