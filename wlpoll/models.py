from django.db import models
from django.contrib.auth.models import User
import datetime

# lambda couldn't be used in field default and for python2 it must be declared
# in module body
# NOCOMM franku: The lambda won't work; why not return the result?
def closed_date_default():
    #return lambda: datetime.datetime.now() + datetime.timedelta(days=90)
    return datetime.datetime.now() + datetime.timedelta(days=90)

class PollManager(models.Manager):
    def open(self):
        return self.all().exclude(closed_date__lte=datetime.datetime.now)

class Poll(models.Model):
    name = models.CharField(max_length=256)
    pub_date = models.DateTimeField("date published", default = datetime.datetime.now)
    closed_date = models.DateTimeField("date closed", default = closed_date_default,
                                       blank=True, null=True)

    objects = PollManager()
        
    def total_votes(self):
        return self.choices.all().aggregate(models.Sum("votes"))["votes__sum"]

    def has_user_voted(self, u):
        return u.poll_votes.filter(poll=self).count() > 0

    def is_closed(self):
        if self.closed_date is None:
            return False
        return self.closed_date < datetime.datetime.now()

    @models.permalink
    def get_absolute_url(self):
        return ('wlpoll_detail', (), {'pk': self.id})

    def __unicode__(self):
        return self.name

class Choice(models.Model):
    poll = models.ForeignKey(Poll, related_name="choices")
    choice = models.CharField(max_length=256)
    votes = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return u"%i:%s" % (self.votes,self.choice)

class Vote(models.Model):
    user = models.ForeignKey(User, related_name="poll_votes")
    poll = models.ForeignKey(Poll)
    choice = models.ForeignKey(Choice)
    date_voted = models.DateTimeField("voted at", default = datetime.datetime.now)


