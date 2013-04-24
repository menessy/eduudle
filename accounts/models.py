
from django.utils.crypto import constant_time_compare, get_random_string
import hashlib, time, re, random
from django.db import models
from django.core.exceptions import *
from django.db import IntegrityError
from django.utils.crypto import constant_time_compare, get_random_string
from django.core.mail import send_mail
from django import forms
from django.http import *
from datetime import date
from django.contrib import admin
from euudle.models import *
from django_facebook.models import FacebookProfileModel
from django_facebook.models import get_user_model

class Account_Manager(models.Manager):

    error = ''

    def is_valid(self,user,passwd):
        error = ""
        p = hashlib.sha512(str(passwd)).hexdigest()
        try:
            username = self.get(email=user,password=p)
        except ObjectDoesNotExist:
            return False, 'User/Password Incorrect.'
        Sessions.objects.set_s(username)
        session = Sessions.objects.get(id_acc=username).value
        return True,session
    
    def is_valid2(self,user,passwd):
        error = ""
        try:
            username = self.get(email=user,facebook_page=passwd)
        except ObjectDoesNotExist:
            return False, 'User/Password Incorrect.'
        Sessions.objects.set_s(username)
        session = Sessions.objects.get(id_acc=username).value
        return True,session
        
    def is_valid3(self,user):
        error = ""
        try:
            username = self.get(email=user)
        except ObjectDoesNotExist:
            return False, 'User/Password Incorrect.'
        Sessions.objects.set_s(username)
        session = Sessions.objects.get(id_acc=username).value
        return True,session
        
    def set_passwd(self,pss):
        if len(pss) >= 2:
            return hashlib.sha512(str(pss)).hexdigest()
        self.error += "Password must contain: @ least 4 numbers."
        

    def set_mobile(self,mob):
        if re.match('^(\d+)$', str(mob)):
            return str(mob)
        else:
            self.error += "Invalid Mobile number."

    def set_email(self,m):
        if re.match('^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}$',str(m)):
            return str(m)
        else:
            self.error +="Invalid Email was entered."
    
    def up_date(self,na,phone,cty,address):
        self.error = ''
        m = self.set_mobile(phone)
        self.error += check_city(cty)     
        
        if self.error == '':
            try:
                user = self.get(name=na)
                user.phone = m
                user.common_address = address
                user.city = cty
                user.save()
                return True, None
            except ObjectDoesNotExist:
                return False, "User does not exist"
        return False, self.error
    
    def register(self,nam,passwor,emai):
        self.error = ''
        p = self.set_passwd(passwor)
        #if len(nam) < 3 or len(nam) > 40:
        #    self.error += 'Provide a username having @ least 3 characters.'
        #if re.search('[?!@#$%^&*()_+}{|"?><.,"-:>~]',nam):
        #    self.error += "Please enter your name correctly."
        #m = self.set_mobile(mobil)
        e = self.set_email(emai)
        #######################################
        #self.error += check_city(cty)
        if self.error == '':
            try:
                self.create(name=nam,password=p,email=e)
                return True, None
            except IntegrityError:
                self.error = "ACCOUNT EXISTS"
                return False, self.error
        else:
            return False, self.error

gender = ( 
    ( 'M', 'M' ),
    ( 'F', 'F' ),   
)

class Account(FacebookProfileModel):
    name = models.CharField(max_length=200)
    avatar = models.FileField(upload_to='avatars/',default='avatars/images.jpeg')
    user = models.OneToOneField(get_user_model(),blank=True,null=True)
    gender2 = models.CharField(max_length=10,blank=True,null=True,choices=gender)
    email = models.CharField(max_length=200,unique=True)
    password = models.CharField(max_length=255)
    birthday = models.DateField(blank=True,null=True)
    avatar2 = models.URLField(null=True,blank=True)
    facebook_data = models.TextField(null=True,blank=True)
    secret = models.CharField(max_length=255,null=True,blank=True)
    ###########################################
    facebook_page = models.CharField(max_length=255,blank=True,null=True,default='')
    twitter_account = models.CharField(max_length=255,blank=True,null=True,default='')
    linkedin_account = models.CharField(max_length=255,blank=True,null=True,default='')
    google_plus_account = models.CharField(max_length=255,blank=True,null=True,default='')
    github_account = models.CharField(max_length=255,blank=True,null=True,default='')
    
    phone = models.CharField(max_length=30,blank=True,null=True)
    city = models.CharField(max_length=250,blank=True,null=True)
    subscribe_news = models.BooleanField(default=False)
    common_address = models.TextField(blank=True,null=True,default='')
    created_on = models.DateTimeField(default=datetime.datetime.today()) 
    reviews = models.ManyToManyField(Review,blank=True,null=True)     
    description = models.TextField(blank=True,null=True,default='')
    website = models.CharField(max_length=255,null=True,blank=True,default='')
    who_voted = models.ManyToManyField(Review,null=True,blank=True,related_name='votes')
    courses = models.ManyToManyField(BaseCourse,blank=True,null=True)
    
    objects= Account_Manager()

    def __unicode__(self):
        return u'%s' % self.email
        
    def get_avatar(self):
        return self.avatar if not self.avatar2 else self.avatar     
        
    class META:
        app_label = 'accounts'


class Session_m(models.Manager):
    def set_s(self,idm):
        val = hashlib.sha256(hashlib.sha224(str(random.randint(100000,99999999999))).hexdigest()).hexdigest()
        try:
            self.create(value=val,id_acc=idm)
        except IntegrityError:
            Sessions.objects.get(id_acc=idm).delete()
            self.create(value=val,id_acc=idm)
            
    def check_session(self,val):
        try:
            m = self.get(value=val)
        except ObjectDoesNotExist:
            return None
        if int(time.time()) > m.deadline:
            m.delete()
            return None
        self.update(deadline=int(time.time())+60*15)
        return m.id_acc
        
    def get_account(self,val):
        try:
            m = self.get(value=val)
        except ObjectDoesNotExist:
            return False
        return m.id_acc  

class Sessions(models.Model):
    value = models.CharField(max_length=200)
    id_acc = models.OneToOneField(Account,primary_key=True)
    created_on = models.BigIntegerField(default=int(time.time()))
    deadline = models.BigIntegerField(default=(int(time.time())+60*20))
    objects = Session_m()
    
    def __unicode__(self):
        return self.value
        
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    if created:
        profile, new = Account.objects.get_or_create(user=instance)
        

        

    
