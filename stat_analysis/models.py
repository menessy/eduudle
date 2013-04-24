from django.db import models

# Create your models here.


class keyword(models.Model):
    word = models.CharField(max_length=250,unique=True)
    occurance = models.IntegerField(default=1)
    
    def __unicode__(self):
        return u'%s - %s times' % ( self.word , self.occurance )
