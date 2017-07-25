

from google.appengine.ext import ndb
import datetime


class Task(ndb.Model):
    """Models an individual Task entry."""
    created = ndb.DateTimeProperty(auto_now_add=True)
    task_type = ndb.StringProperty()
    task = ndb.StringProperty()
    video_address = ndb.StringProperty()
    comment = ndb.StringProperty(indexed=False)
