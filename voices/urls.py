# -*- coding: UTF-8 -*-
# urls.py
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

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'arc.views.home', name='home'),
    url(r'^qr/(?P<qr>\d+)/$', 'arc.views.room_from_qr', name='qr'),
    url(r'^voice/new/(?P<room_id>\d+)/(?P<item_id>\d+)/$', 'arc.views.new_voice', name='new_voice'),
    url(r'^voice/(?P<voice_id>\d+)/set/(?P<state_id>\d+)/$', 'arc.views.set_voice', name='set_voice'),
    url(r'^voice/(?P<voice_id>\d+)/$', 'arc.views.voice', name='voice'),
    url(r'^voices/$', 'arc.views.voices', name='voices'),
    url(r'^stats/$', 'arc.views.stats', name='stats'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}, name='login'),
)
