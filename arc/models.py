# -*- coding: UTF-8 -*-
# arc/models.py - Main model of the application
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

from django.db import models
from django.contrib.auth.models import User, Group
from voices import settings

URGENCY_CHOICES = (
    (1, u'Haute'),
    (2, u'Moyenne'),
    (3, u'Basse'),
    (4, u'Information'),
)

# Create your models here.


class Campus(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10)
    #order = models.IntegerField(default=99)

    def __unicode__(self):
        return self.short_name


class Building(models.Model):
    campus = models.ForeignKey(Campus)
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10)
    #order = models.IntegerField(default=99)

    def __unicode__(self):
        return self.short_name


class Floor(models.Model):
    building = models.ForeignKey(Building)
    floor_display = models.CharField(max_length=10)
    floor_number = models.IntegerField()

    def __unicode__(self):
        return self.floor_display


class NotificationCategory(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=15)
    category_weight = models.IntegerField()

    def __unicode__(self):
        return self.short_name


class NotificationItem(models.Model):
    category = models.ForeignKey(NotificationCategory)
    name = models.CharField(max_length=50)
    description = models.TextField()
    short_name = models.CharField(max_length=15)
    item_weight = models.IntegerField()
    group_alert = models.ForeignKey(Group)

    def __unicode__(self):
        return self.short_name


class NotificationGroup(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=15)
    items = models.ManyToManyField(NotificationItem)

    def __unicode__(self):
        return self.short_name


class Room(models.Model):
    floor = models.ForeignKey(Floor)
    room_name = models.CharField(max_length=50)
    room_display = models.CharField(max_length=10)
    room_number = models.IntegerField()
    notification_groups = models.ManyToManyField(NotificationGroup)
    geo = models.CommaSeparatedIntegerField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    picture_height = models.IntegerField(blank=True)
    picture_weight = models.IntegerField(blank=True)
    picture = models.ImageField(upload_to=settings.MEDIA_ROOT + '/room', height_field=picture_height, width_field=picture_weight, blank=True)

    def __unicode__(self):
        return self.room_display + " " + self.room_name


class QRcode(models.Model):
    qr = models.IntegerField()
    room = models.ForeignKey(Room)
    snap = models.IntegerField(default=0)


class QRsnap(models.Model):
    qr = models.ForeignKey(QRcode)
    date = models.DateTimeField(auto_now_add=True)


class VoiceState(models.Model):
    state = models.CharField(max_length=15)
    css_color = models.CharField(max_length=7)
    css_class = models.CharField(max_length=15)

    def __unicode__(self):
        return self.state


class Voice(models.Model):
    notification_item = models.ForeignKey(NotificationItem)
    room = models.ForeignKey(Room)
    urgency = models.IntegerField(choices=URGENCY_CHOICES, default=2)
    message = models.TextField(blank=True)
    user = models.ForeignKey(User, null=True)
    state = models.ForeignKey(VoiceState)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_change_date = models.DateTimeField(auto_now=True)
    closing_date = models.DateTimeField(null=True, blank=True)


class VoiceStateHistory(models.Model):
    voice = models.ForeignKey(Voice)
    state = models.ForeignKey(VoiceState)
    date = models.DateTimeField(auto_now=True)
    comment = models.TextField(blank=True)
    user = models.ForeignKey(User)


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)
    # Other fields here
    sms = models.CharField(max_length=11, blank=True)
    voip = models.CharField(max_length=11, blank=True)
    xmpp = models.CharField(max_length=100, blank=True)
    send_sms = models.BooleanField()
    send_email = models.BooleanField()
    send_voip = models.BooleanField()
    send_xmpp = models.BooleanField()