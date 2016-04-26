#!/usr/bin/env python
# -*- coding: utf-8 -*-

from werkzeug.serving import run_simple
from avatar import application

run_simple('localhost', 8080, application, use_reloader=True)
