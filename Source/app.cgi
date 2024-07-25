#!/home/plz/public_html/Video-School-CMS-main/.venv/bin/python

from wsgiref.handlers import CGIHandler
from app import app

CGIHandler().run(app)
