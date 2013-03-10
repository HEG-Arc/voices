# -*- coding: UTF-8 -*-
# arc/tasks.py - Task scheduler (django-celery)
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


from celery.decorators import task
import xmpp
from voices.settings import GOOGLE_TALK_PASSWORD, GOOGLE_TALK_USER


@task
def send_notification(voice):
    group = voice.notification_item.group_alert
    users = group.user_set.all()
    for user in users:
        if user.userprofile.send_xmpp:
            send_xmpp(voice, user.userprofile.xmpp)


@task
def send_xmpp(voice, xmppto):
    username = GOOGLE_TALK_USER
    passwd = GOOGLE_TALK_PASSWORD
    to = xmppto
    msg = '%s\n%s-%s\n%s\nhttp://marmix.ig.he-arc.ch/voices/voice/%s/' % \
          (voice.room.floor.building.name, voice.room.room_display, voice.room.room_name, voice.notification_item.name,
           voice.id)
    client = xmpp.Client('gmail.com')
    client.connect(server=('talk.google.com', 5223))
    client.auth(username, passwd, 'TalkToUs!')
    client.sendInitPresence()
    message = xmpp.Message(to, msg)
    message.setAttr('type', 'chat')
    client.send(message)