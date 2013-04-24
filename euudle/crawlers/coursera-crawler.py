#!/usr/bin/env python2.6

#-*- encoding=UTF-8 -*-
from httplib import *
import os, ssl, json, sys
from django.core.exceptions import *
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = "euudle.settings"
from euudle import settings
from euudle.models import *
from django.utils.encoding import smart_str, smart_unicode
import datetime


def clean_me(st):
    return smart_str(st).replace('\n','').replace('\t','')

header = {
    'Host': 'www.coursera.org',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20130220 Firefox/17.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.coursera.org/courses'
}

conn = HTTPSConnection("www.coursera.org",443)
conn.request("GET","/maestro/api/topic/list2",None,header)
coursera_doc =  json.loads(conn.getresponse().read())

def find_in_dict(dic,key):
    temp = {}
    for i in dic:
        try:
            if key == dict(i)['instructor_id']:
                return dict(i)
        except:
            if key == dict(i)['id']:
                return dict(i)
    return None


for i in coursera_doc['topics']:
    instance = coursera_doc['topics'][i]
    try:
        course = coursera_course.objects.get(course=BaseCourse.objects.get(course_id=i))                               ## course exists
        #if course.link != 'https://www.coursera.com/' + instance['short_name']:
        #    raise ObjectDoesNotExist   
    except ObjectDoesNotExist:                                                          ## before adding the course, check the existance of the instructor
        instructors = instance.get('insts',[])
        Instructors_Result = []
        for g in instructors:
            #print coursera_doc['insts']
            temp = find_in_dict(coursera_doc['insts'],g)
            inst_name = temp['first_name'] + ' '+ temp['middle_name'] + ' ' + temp['last_name']
            inst_name = clean_me(inst_name)
            Instructors_Result.append(BaseInstructor.objects.get_or_create(inst_id=g,defaults={ 'name': inst_name, 'short_name' : temp['short_name'] })[0])
        institutions = instance['unis']
        Institutions_Result = []
        for g in institutions:
            temp = find_in_dict(coursera_doc['unis'],g)
            Institutions_Result.append( common_university.objects.get_or_create(url_icon=temp['favicon'],name=temp['name'], defaults= { 'uni_id' : temp['id'] , 'home_link':temp['home_link'] , 'short_name' : temp['short_name'] , 'engine' : 'COURSERA' } )[0] )
        categories = instance.get('cats',[])
        Categories_Result = []
        for g in categories:
            temp = find_in_dict(coursera_doc['cats'],g)
            Categories_Result.append(coursera_category.objects.get_or_create(category_id=g, defaults = { 'category_name' : temp['name'] } )[0] )
        
        c = BaseCourse()
        the_course = coursera_course()
        c.course_id = i
        c.course_name = clean_me(instance['name'])
        the_course.course_icon = instance['small_icon_hover']
        c.link = 'https://www.coursera.org/course/' + instance['short_name']
        #################################################################################################### here is the other http request
        conn.request('GET','/maestro/api/topic/information?topic-id=' + instance['short_name'] , None, header)
        more_details = json.loads(conn.getresponse().read())
        #####################################################################################################'
        c.full_description = clean_me(more_details['about_the_course'])
        c.youtube_video = 'http://www.youtube.com/embed/' + more_details['video']
        c.course_image = more_details['photo']
        
        much_more = dict(more_details['courses'][0])
        the_course.duration = much_more['duration_string']
        try:
            the_course.start_date = datetime.date(int(much_more['start_year']) , int(much_more['start_month']), int(much_more['start_day']) )
        except:
            pass
        c.short_description = more_details['short_description']
        the_course.work_load = more_details['estimated_class_workload']
        
        the_course.language = instance['language']
        c.engine = 'COURSERA'
        c.save()
        the_course.course = c
        for g in Institutions_Result:
            the_course.course.university = g
            break
            
        the_course.save()
        
        
        for g in Instructors_Result:  
            c.instructors.add(g)
        
            
        for g in Categories_Result:
            the_course.categories.add(g)
            
        


