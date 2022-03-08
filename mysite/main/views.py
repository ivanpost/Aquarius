from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Controller, Channel, Program
from operator import add

DAYS = {'monday': 'Понедельник',
        'tuesday': 'Вторник',
        'wednesday': 'Среда',
        'thursday': 'Четверг',
        'friday': 'Пятница',
        'saturday': 'Суббота',
        'sunday': 'Воскресенье'}

@login_required
def index(request):
    return render(request, 'main/index.html',
                  {
                      'controllers': Controller.objects.all()
                  })

@login_required
def reports(request):
    return render(request, 'main/reports.html')


@login_required
def controller(request, prefix):
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
                    if out[int(d) - 1][i] == 0:
                        out[int(d) - 1][i] += h

        return out

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
    def get_m(t):
        out = t // 5
        if t % 5 > 0:
            out += 1
        return out

    def get_time(h, m, t):
        start = [h, get_m(m)]
        stop = [h + t // 60, get_m(m + t % 60)]
        return start, stop

    channels = Channel.objects.filter(controller__prefix=prefix)
    lines = []
    for i in range(len(channels)):
        lines.append([])
        for j in range(24):
            lines[i].append([])
            for g in range(12):
                lines[i][j].append(0)
    day_num = list(DAYS.keys()).index(day) + 1
    programs = Program.objects.filter(channel__controller__prefix=prefix, days__contains=str(day_num))


    for p in programs:
        start = [p.hour, p.minute // 5]
        if p.minute % 5 > 0:
            start[1] += 1
        stop = [p.hour + (p.t_max // 60), (p.minute + (p.t_max % 60)) // 5]
        if (p.minute + (p.t_max % 60)) % 5 > 0:
            stop[1] += 1
        for h in range(0, 24):
            for m in range(0, 12):
                if h == start[0] and m >= start[1] and not start[0] == stop[0]:
                    if lines[p.channel.id-1][h][m] == 0:
                        lines[p.channel.id-1][h][m] = 1
                elif start[0] < h < stop[0]:
                    if lines[p.channel.id-1][h][m] == 0:
                        lines[p.channel.id-1][h][m] = 1
                elif h == stop[0] and m <= stop[1]:
                    if lines[p.channel.id-1][h][m] == 0:
                        lines[p.channel.id-1][h][m] = 1
    print(lines)

    return render(request, 'main/controller_day.html',
                  {
                      'prefix': prefix,
                      'day': DAYS[day],
                      'hours_total': [i for i in range(24)],
                      'lines_day': lines
                   })
