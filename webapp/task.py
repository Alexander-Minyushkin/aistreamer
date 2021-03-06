

from google.appengine.ext import ndb
import time


class Task(ndb.Model):
    """Models an individual Task entry."""
    created = ndb.DateTimeProperty(auto_now_add=True)
    pulled = ndb.DateTimeProperty()
    is_completed = ndb.BooleanProperty()
    task_type = ndb.StringProperty()
    video_address = ndb.StringProperty()
    comment = ndb.StringProperty(indexed=False)
    result = ndb.StringProperty()

    @classmethod
    def latest(cls):
        return cls.query().order(-cls.created).fetch(10)

    @classmethod
    def pull(cls, timeout_sec=10*60):
        return cls.query().order(cls.created).filter(Task.).fetch(1)
