
import datetime
from django.db import models
from django_facebook.models import FacebookProfileModel
from django_facebook.models import get_user_model
from django.db.models import Max
#from accounts.model import *


class Review(models.Model):
    agree = models.IntegerField(default=0)
    disagree = models.IntegerField(default=0)
    created_on = models.DateTimeField(default=datetime.datetime.today())
    review = models.TextField()


    class META:
        app_label = 'euudle'

ENGINE = (
    ( 'COURSERA' , 'COURSERA' ),
    ( 'EDX' , 'EDX' ),
    ( 'UDACITY' , 'UDACITY' ),
)

AVAILABILITY = (
    ( 'Self-paced', 'Self-paced' ),
    ( 'Currently' , 'Currently' ),
    ( 'Upcomming' , 'Upcomming' ),
    ( 'Long', 'Long' ),   
    ( 'TBD' , 'TBD' ),
)
#                           Shared Properties
##############################################################################     
############################################################################## 
##############################################################################

class common_university(models.Model):
    name = models.CharField(max_length=250,null=True,blank=True)
    home_link = models.URLField(null=True,blank=True)
    url_icon = models.URLField(null=True,blank=True)
    engine = models.CharField(max_length=50,choices=ENGINE)
    last_update = models.DateField(default=datetime.datetime.today())
    uni_id = models.IntegerField(null=True,blank=True)
    short_name = models.CharField(max_length=250,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    
    class META:
        app_label = 'euudle'
        
    def __unicode__(self):
        return u'%s' % self.name


class common_category(models.Model):
    category_id = models.IntegerField(null=True,blank=True)
    category_name = models.CharField(max_length=250)
    last_update = models.DateField(default=datetime.datetime.today())
    
    def __unicode__(self):
        return u'%s' % self.category_name
        
    class META:
        verbose_name_plural = 'categories'
        app_label = 'euudle' 

    
class BaseInstructor(models.Model):
    name = models.CharField(max_length=250)
    image = models.URLField(null=True,blank=True)
    title = models.CharField(max_length=250,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    last_update = models.DateField(default=datetime.datetime.today())
    inst_id = models.IntegerField(null=True,blank=True)
    short_name = models.CharField(max_length=50,null=True,blank=True)
    engine = models.CharField(max_length=50,choices=ENGINE)

    def __unicode__(self):
        return u'%s' % self.name
        
    class META:
        app_label = 'euudle'

class lang(models.Model):
    language2 = models.CharField(max_length=30,default='en')


class BaseCourse(models.Model):
    course_id = models.CharField(max_length=20,blank=True,null=True)
    course_name = models.CharField(max_length=250,blank=True,null=True)
    course_image = models.URLField(blank=True,null=True)
    link = models.URLField()
    ##################################################
    rating = models.FloatField(default=0)
    rating_n = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    content_rich = models.FloatField(default=0)
    content_rich_n = models.IntegerField(default=0)
    enjoyable = models.FloatField(default=0)
    enjoyable_n = models.IntegerField(default=0)
    career_oriented = models.FloatField(default=0)
    career_oriented_n = models.IntegerField(default=0)
    engaging = models.FloatField(default=0)
    engaging_n = models.IntegerField(default=0)
    categories = models.ManyToManyField(common_category)
    cost = models.IntegerField(default=0)
    coursewall_number = models.IntegerField(default=0)
    ##################################################
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    duration = models.CharField(max_length=50,null=True,blank=True)
    ############################################
    language1 = models.ForeignKey(lang)
    last_update = models.DateField(default=datetime.datetime.today())
    short_description = models.TextField(blank=True,null=True)
    full_description = models.TextField(blank=True,null=True)
    instructors = models.ManyToManyField(BaseInstructor)
    youtube_video = models.URLField(blank=True,null=True)
    university = models.ForeignKey(common_university,null=True,blank=True)
    availability = models.CharField(max_length=50,choices=AVAILABILITY)
    engine = models.CharField(max_length=50,choices=ENGINE) 
    reviews = models.ManyToManyField(Review,blank=True,null=True) 
    featured = models.BooleanField(default=False)  
    
    def __unicode__(self):
        return u'%s' % self.course_name
        
    def get_max_review(self):
        review = self.reviews.all().aggregate(Max('agree'))#['agree__max']    
        try:
            return Review.objects.filter(agree=review)[0]
        except:
            return None
            
    def get_max_three_reviews(self):
        return self.reviews.all().order_by('-agree')[:3]
            
    class META:
        app_label = 'euudle'
  

##############################################################################      
#################################UDACITY######################################  
##############################################################################

class udacity_course(models.Model):
    course = models.OneToOneField(BaseCourse)
    course_sub_name =  models.CharField(max_length=250)
    #category = models.CharField(max_length=250,null=True,blank=True)
    difficulty = models.CharField(max_length=100,null=True,blank=True)
    outcome = models.TextField(null=True,blank=True)
    full_prerequistes = models.TextField(null=True,blank=True)
    more_details = models.TextField(null=True,blank=True)
    
    def __unicode__(self):
        return u'%s - %s' % ( self.course.course_id , self.course.course_name )

    class META:
        app_label = 'euudle'    

##############################################################################      
################################COURSERA######################################  
##############################################################################


class coursera_course(models.Model):
    course = models.OneToOneField(BaseCourse)
    course_icon = models.URLField(null=True,blank=True)
    work_load = models.CharField(max_length=200,null=True,blank=True)
    ####################################
    
    def __unicode__(self):
        return u'%s' % self.course.course_name
        
    class META:
        app_label = 'euudle'   

##############################################################################
#####################################EDX######################################  
############################################################################## 

class edx_course(models.Model):
    course = models.OneToOneField(BaseCourse)
    short_prerequistes = models.CharField(max_length=200,null=True,blank=True)
    full_prerequistes = models.TextField(null=True,blank=True)
    work_load = models.CharField(max_length=200,null=True,blank=True)
    
    def __unicode__(self):
        return u'%s - %s' % ( self.course.course_id , self.course.course_name)


############################################################################################################################################################       
#######################################################################GENERAL#API##########################################################################  
############################################################################################################################################################

class statistical_data(models.Model):
    ip = models.CharField(max_length=50,unique=True,blank=False,null=False)
    header = models.CharField(max_length=40)
    created_on = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u'%s' % self.ip


