#!</path/to/venv>

from wsgiref.handlers import CGIHandler
from app import app

CGIHandler().run(app)