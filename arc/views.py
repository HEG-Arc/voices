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
from arc.models import Room, NotificationItem, Voice, URGENCY_CHOICES, VoiceState, QRcode, QRsnap, Building
from arc.tasks import send_notification
from voices import settings
from django import forms
import datetime
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors





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


def desktop_home(request):

    return render_to_response('desktop_home.html', context_instance=RequestContext(request))


def desktop_printqr(request, building_id=None):
    buildings = Building.objects.all()
    if building_id:
        rooms = Room.objects.filter(floor__building__id__exact=int(building_id)).order_by('floor__floor_number', 'room_number')
        filtered = int(building_id)
    else:
        rooms = Room.objects.all().order_by('floor__building__short_name', 'floor__floor_number', 'room_number')
        filtered = False
    return render_to_response('print.html', {"rooms": rooms, 'buildings': buildings, 'filtered': filtered}, context_instance=RequestContext(request))


def print_poster_A4(request, qr_id):
    qrcode = QRcode.objects.get(pk=int(qr_id))
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="posterA4-%s.pdf"; size=A4' % (str(qrcode.room.room_number))

    p = canvas.Canvas(response)
    p.drawImage('/home/cgaspoz/Dev/voices/static/templates/talk_to_us_A4.jpg', 0, 0, width=210*mm, height=297*mm)

    qr_size = 90.5*mm
    qr_x = 60*mm
    qr_y = 63*mm

    qrw = QrCodeWidget(settings.HTTP_URL + "qr/" + str(qrcode.qr) + "/")
    qrw.barHeight = qr_size
    qrw.barWidth = qr_size
    qrw.barLevel = 'Q'  # M, L, H, Q
    qrw.barBorder = 0

    d = Drawing(qr_size, qr_size)
    d.add(qrw)
    d.add(Rect(5.6*mm, 5.6*mm, 8*mm, 8*mm, strokeColor=colors.CMYKColor(1, 0, 0, 0), fillColor=colors.CMYKColor(1, 0, 0, 0)))
    d.add(Rect(76.9*mm, 76.9*mm, 8*mm, 8*mm, strokeColor=colors.CMYKColor(1, 0, 0, 0), fillColor=colors.CMYKColor(1, 0, 0, 0)))
    d.add(Rect(5.6*mm, 76.9*mm, 8*mm, 8*mm, strokeColor=colors.CMYKColor(1, 0, 0, 0), fillColor=colors.CMYKColor(1, 0, 0, 0)))

    renderPDF.draw(d, p, qr_x, qr_y)

    p.showPage()

    text = p.beginText()
    text.setTextOrigin(12*mm,277*mm)
    text.setFillGray(0.5)
    text.setFont("Helvetica", 10)
    text.textLines('''
        Talk to us! @ HE-Arc
        Campus: %s
        Building: %s
        Floor: %s
        Room: %s-%s
        QR-Code: %s''' % (qrcode.room.floor.building.campus.name, qrcode.room.floor.building.name,
                          qrcode.room.floor.floor_display, qrcode.room.room_number, qrcode.room.room_name, qrcode.qr))
    p.drawText(text)

    p.showPage()

    p.save()

    return response