# -*- coding: UTF-8 -*-
# views.py
#
# Copyright (C) 2013 HES-SO // Haute école de gestion Arc
#
# Author: Cédric Gaspoz <cedric@gaspoz-fleiner.com>
#
# This file is part of voices.
#
# voices is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# voices is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with voices.  If not, see <http://www.gnu.org/licenses/>.

from django.shortcuts import render_to_response, redirect, HttpResponseRedirect
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from arc.models import Room, NotificationItem, Voice, URGENCY_CHOICES, VoiceState, QRcode, QRsnap
from arc.tasks import send_notification
from django import forms
import datetime


class VoiceForm(forms.Form):
    urgency = forms.ChoiceField(choices=URGENCY_CHOICES, label='Urgence de la notification', initial=2)
    message = forms.CharField(widget=forms.Textarea, label='Remarques (facultatif)', required=False)


# Create your views here.

def home(request):
    return render_to_response('home.html', context_instance=RequestContext(request))


def room_from_qr(request, qr):
    qrcode = QRcode.objects.get(qr__exact=int(qr))
    qrcode.snap += 1
    qrcode.save()
    qrsnap = QRsnap(qr=qrcode)
    qrsnap.save()
    room = qrcode.room
    return render_to_response('room.html', {"room": room, }, context_instance=RequestContext(request))


def voice(request, voice_id):
    voice = Voice.objects.get(pk=int(voice_id))
    return render_to_response('voice.html', {"voice": voice, 'new': False}, context_instance=RequestContext(request))


def voices(request):
    voices = Voice.objects.all().order_by('state')
    return render_to_response('voices.html', {"voices": voices, }, context_instance=RequestContext(request))


def set_voice(request, voice_id, state_id):
    voice = Voice.objects.get(pk=int(voice_id))
    state = VoiceState.objects.get(pk=int(state_id))
    voice.state = state
    voice.save()
    return render_to_response('voice.html', {"voice": voice, 'new': False}, context_instance=RequestContext(request))


def new_voice(request, room_id, item_id):
    room = Room.objects.get(pk=int(room_id))
    item = NotificationItem.objects.get(pk=int(item_id))
    state = VoiceState.objects.get(pk=1)
    if request.method == 'POST':  # If the form has been submitted...
        form = VoiceForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            voice = Voice()
            voice.urgency = form.cleaned_data['urgency']
            voice.message = form.cleaned_data['message']
            voice.room = room
            voice.notification_item = item
            voice.state = state
            if request.user.is_authenticated():
                voice.user = request.user
            voice.save()
            send_notification.delay(voice)
            return HttpResponseRedirect(reverse('voice', kwargs={'voice_id': voice.id,}))
    else:
        form = VoiceForm()  # An unbound form
    return render_to_response('new_voice.html', {"room": room, "item": item, "form": form},
                              context_instance=RequestContext(request))


def stats(request):
    date_start = datetime.date.today()
    date_end = datetime.date.today() + datetime.timedelta(1)
    sday = Voice.objects.filter(creation_date__range=(date_start, date_end)).count()
    date_start = datetime.date.today() - datetime.timedelta(datetime.date.today().weekday())
    sweek = Voice.objects.filter(creation_date__range=(date_start, date_end)).count()
    date_start = datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
    smonth = Voice.objects.filter(creation_date__range=(date_start, date_end)).count()
    sall = Voice.objects.all().count()
    voices = {'day': sday, 'week': sweek, 'month': smonth, 'all': sall}
    states = VoiceState.objects.all()
    return render_to_response('stats.html', {"voices": voices, "states": states},
                              context_instance=RequestContext(request))