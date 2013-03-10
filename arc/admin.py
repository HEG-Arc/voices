# -*- coding: UTF-8 -*-
# arc/admin.py - Register models for the admin interface
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


from arc.models import Building, Campus, Floor, NotificationCategory, NotificationGroup, NotificationItem, Room, \
    UserProfile, Voice, VoiceState, VoiceStateHistory, QRcode, QRsnap

from django.contrib import admin

admin.site.register(Building)
admin.site.register(Campus)
admin.site.register(Floor)
admin.site.register(NotificationCategory)
admin.site.register(NotificationGroup)
admin.site.register(NotificationItem)
admin.site.register(Room)
admin.site.register(UserProfile)
admin.site.register(Voice)
admin.site.register(VoiceState)
admin.site.register(VoiceStateHistory)
admin.site.register(QRcode)
admin.site.register(QRsnap)