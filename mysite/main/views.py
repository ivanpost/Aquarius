import django.db.models
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Controller, Channel, Program, UserExtension
from operator import add
from datetime import datetime, time, timedelta
import time
from ControllerManagers import ControllerV2Manager
import json

DAYS = {'monday': 'Понедельник',
        'tuesday': 'Вторник',
        'wednesday': 'Среда',
        'thursday': 'Четверг',
        'friday': 'Пятница',
        'saturday': 'Суббота',
        'sunday': 'Воскресенье'}

@login_required
def index(request):
    try:
        saved_controllers = request.user.userextension.saved_controllers
    except:
        uex = UserExtension(user=request.user, saved_controllers="[]")
        uex.save()
        saved_controllers = "[]"
    if saved_controllers is None:
        saved_controllers = []
    else:
        saved_controllers = json.loads(saved_controllers)
    print(saved_controllers)
    if request.method == "POST":
        values = request.POST.dict()
        if "user" in values.keys() and "password" in values.keys():
            if ControllerV2Manager.check_auth(values["user"], values["password"]):
                if ControllerV2Manager.add(values["user"], values["password"]):
                    saved_controllers.append([values["user"], values["password"]])


    controllers = []
    _remove = []
    for c in saved_controllers:
        if ControllerV2Manager.check_auth(c[0], c[1]):
            controllers.append(ControllerV2Manager.get_instance(c[0]).data_model)
        else:
            _remove.append(c)
    [saved_controllers.remove(c) for c in _remove]
    response = render(request, 'main/index.html',
                    {
                        'controllers': controllers
                    })
    request.user.userextension.saved_controllers = json.dumps(saved_controllers)
    request.user.userextension.save()
    return response

@login_required
def reports(request):
    return render(request, 'main/reports.html')

@login_required
def manual_activation(request, prefix, chn, minutes=0):
    if not ControllerV2Manager.check_auth(prefix=prefix, user=request.user):
        return redirect("/")

    chn = int(chn)

    channel = Channel.objects.filter(controller__prefix=prefix, number=chn)
    if len(channel) > 0:
        channel = channel[0]
    else:
        return redirect("/")
    cont = Controller.objects.get(prefix=prefix)
    instance: ControllerV2Manager = ControllerV2Manager.get_instance(prefix)

    if minutes > 0:
        instance.command_turn_on_channel(chn, minutes)
        instance.command_get_state()
        return redirect("controller", prefix=prefix)

    return render(request,
                  "main/manual_activation.html",
                  {
                      "prefix": prefix,
                      "cont": cont,
                      "chn": chn,
                  })


@login_required
def manual_activation_selector(request, prefix, turn_off_all=False):
    if not ControllerV2Manager.check_auth(prefix=prefix, user=request.user):
        return redirect("/")

    channels = Channel.objects.filter(controller__prefix=prefix)
    cont = Controller.objects.get(prefix=prefix)

    instance: ControllerV2Manager = ControllerV2Manager.get_instance(prefix)
    instance.command_get_state()
    if turn_off_all:
        if instance is not None:
            instance.turn_off_all_channels()
            instance.command_get_state()
            return redirect("controller", prefix=prefix)

    return render(request,
                  "main/manual_activation_selector.html",
                  {
                      "prefix": prefix,
                      'channels_state_json': json.dumps([i.state for i in channels]),
                      "cont": cont,
                  })

@login_required
def controller(request, prefix):
    if not ControllerV2Manager.check_auth(prefix=prefix, user=request.user):
        return redirect("/")
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

    instance = ControllerV2Manager.get_instance(prefix)
    if instance is not None:
        instance.command_get_state()

    programs = Program.objects.filter(channel__controller__prefix=prefix)
    channels = Channel.objects.filter(controller__prefix=prefix)
    cont = Controller.objects.get(prefix=prefix)

    class Line:
        def __init__(self, status, data):
            self.status = status
            self.data = data

    lines = []
    for chn in channels:
        lines.append(Line(chn.state, get_week(chn)))

    return render(request, 'main/controller.html',
                  {
                      'prefix': prefix,
                      'lines_week': lines,
                      'cont': cont,
                      'day': list(DAYS.values())[cont.day-1],
                      'channels_state_json': json.dumps([i.status for i in lines])
                    })

@login_required
def controller_day(request, prefix, day):
    if not ControllerV2Manager.check_auth(prefix=prefix, user=request.user):
        return redirect("/")
    def get_m(t):
        out = t // 2
        if t % 2 > 0:
            out += 1
        return out

    def get_time(h, m, t):
        start = [h, get_m(m)]
        stop = [h + t // 60, get_m((m + t % 60) % 60)]
        stop[0] += (m + t % 60) // 60
        return start, stop

    channels = Channel.objects.filter(controller__prefix=prefix)
    lines = []
    for i in range(len(channels)):
        lines.append([])
        for j in range(24):
            lines[i].append([])
            for g in range(30):
                lines[i][j].append(0)
    day_num = list(DAYS.keys()).index(day) + 1
    programs = Program.objects.filter(channel__controller__prefix=prefix, days__contains=str(day_num))


    for p in programs:
        start, stop = get_time(p.hour, p.minute, p.t_max)
        if (p.minute + (p.t_max % 60)) % 2 > 0:
            stop[1] += 1
        for h in range(0, 24):
            for m in range(0, 30):
                if h == start[0] and m >= start[1] and not start[0] == stop[0]:
                    if lines[p.channel.id-1][h][m] == 0:
                        lines[p.channel.id-1][h][m] = 1
                elif start[0] < h < stop[0]:
                    if lines[p.channel.id-1][h][m] == 0:
                        lines[p.channel.id-1][h][m] = 1
                elif h == stop[0] and m <= stop[1]:
                    if lines[p.channel.id-1][h][m] == 0:
                        lines[p.channel.id-1][h][m] = 1

    return render(request, 'main/controller_day.html',
                  {
                      'prefix': prefix,
                      'day': DAYS[day],
                      'hours_total': [i for i in range(24)],
                      'lines_day': lines
                   })

@login_required()
def channels(request, prefix):
    if not ControllerV2Manager.check_auth(prefix=prefix, user=request.user):
        return redirect("/")

    channels = Channel.objects.filter(controller__prefix=prefix)

@login_required
def channel(request, prefix, chn):
    if not ControllerV2Manager.check_auth(prefix=prefix, user=request.user):
        return redirect("/")
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

    def norm_time(h, m):
        nh = '0' * (2 - len(str(h))) + str(h)
        nm = '0' * (2 - len(str(m))) + str(m)
        out = f'{nh}:{nm}'
        return out

    class PrgData:
        id = 0
        header = ""
        d1 = 0
        d2 = 0
        d3 = 0
        d4 = 0
        d5 = 0
        d6 = 0
        d7 = 0
        t_start = ""
        t_stop_min = ""
        t_stop_max = ""

        def __init__(self, id, days, hour, minute, t_min, t_max):
            self.id = id
            self.d1 = '1' in days
            self.d2 = '2' in days
            self.d3 = '3' in days
            self.d4 = '4' in days
            self.d5 = '5' in days
            self.d6 = '6' in days
            self.d7 = '7' in days
            self.t_start = norm_time(hour, minute)
            self.t_stop_min = norm_time(t_min // 60, t_min % 60)
            self.t_stop_max = norm_time(t_max // 60, t_max % 60)
            self.header = f"{days} | {self.t_start} - {self.t_stop_max}"

    chan = Channel.objects.get(controller__prefix=prefix, id=chn)
    programs = Program.objects.filter(channel=chan)
    lines = []
    prgs = []
    lines.append(get_week(chan))
    for pr in programs:
        prgs.append(PrgData(pr.id, pr.days, pr.hour, pr.minute, pr.t_min, pr.t_max))
    if request.method == 'POST':
        data = request.POST.dict()
        if "create" in data.keys():
            prg = Program()
            prg.channel = chan
            prg.days = ''.join([str(i+1) for i in range(7) if f'days_{i}' in data.keys()])
            if (prg.days != ''):
                prg.hour = int(data['time_start'][:2])
                prg.minute = int(data['time_start'][3:])
                t_start = timedelta(hours=prg.hour, minutes=prg.minute)
                t_end_min = timedelta(hours=int(data['time_end_min'][:2]), minutes=int(data['time_end_min'][3:]))
                t_end_max = timedelta(hours=int(data['time_end_max'][:2]),
                                      minutes=int(data['time_end_max'][3:]))
                prg.t_min = (t_end_min-t_start).total_seconds()//60
                prg.t_max = (t_end_max - t_start).total_seconds() // 60
                prg.save()
                return redirect('channel', prefix=prefix, chn=chn)
        elif "id" in data.keys():
            prg = Program.objects.get(channel=chan, id=data['id'])
            if "delete" in data.keys():
                prg.delete()
                return redirect('channel', prefix=prefix, chn=chn)
            prg.days = ''.join([str(i+1) for i in range(7) if f'days_{i}' in data.keys()])
            if (prg.days != ''):
                prg.hour = int(data['time_start'][:2])
                prg.minute = int(data['time_start'][3:])
                t_start = timedelta(hours=prg.hour, minutes=prg.minute)
                t_end_min = timedelta(hours=int(data['time_end_min'][:2]), minutes=int(data['time_end_min'][3:]))
                t_end_max = timedelta(hours=int(data['time_end_max'][:2]),
                                      minutes=int(data['time_end_max'][3:]))
                prg.t_min = (t_end_min-t_start).total_seconds()//60
                prg.t_max = (t_end_max - t_start).total_seconds() // 60
                prg.save()
                return redirect('channel', prefix=prefix, chn=chn)

    return render(request, 'main/channel.html',
                  {
                      'prefix': prefix,
                      'lines_week': lines,
                      'chn': int(chn),
                      'prgs': prgs
                   })

