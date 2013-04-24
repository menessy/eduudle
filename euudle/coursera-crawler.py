#!/usr/bin/env python2.6

#-*- encoding=UTF-8 -*-
from httplib import *
import os, ssl, json, sys
from django.core.exceptions import *
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = "euudle.settings"
#from euudle import settings
from models import *
from django.utils.encoding import smart_str, smart_unicode
import datetime, re
import bs4


def clean_html(html):
    cleaned = re.sub(r"<div>", "", html)
    cleaned = re.sub(r"</div>", "", cleaned)
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    return cleaned.strip()

def clean_me(st):
    return smart_str(st).replace('\n','').replace('\t','')

def isupcomming(duration,start_date):
    try:
        if duration != None or start_date != None or duration.strip().split() != []:
            week = int(str(duration.strip().split()[0]))
            end = start_date + datetime.timedelta(weeks=week)
            if start_date <= datetime.date.today() <= end:
                return 'Currently'
            elif end - datetime.timedelta(weeks=4) <= datetime.date.today() and end  >= datetime.date.today():
                return 'Upcomming'
            else:
                return 'Long'
        return 'TBD'
    except:
        return 'TBD'

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
        
        institutions = instance['unis']
        categories = instance.get('cats',[])
        Categories_Result = []
        for g in categories:
            temp = find_in_dict(coursera_doc['cats'],g)
            Categories_Result.append(common_category.objects.get_or_create(category_id=g, defaults = { 'category_name' : temp['name'] } )[0] )
        
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
        print more_details
        c.full_description = clean_html(clean_me(more_details['about_the_course']))
        if more_details['course_syllabus'] != '':
            c.full_description += '<br /><br /><strong>Syllabus</strong><br />' + clean_html(clean_me(more_details['course_syllabus']))
        if more_details['suggested_readings'] != '':
            c.full_description += '<br /><br /><strong>Suggested Readings</strong><br />' + clean_html(clean_me(more_details['suggested_readings']))
        if more_details['recommended_background'] != '':
            c.full_description += '<br /><br /><strong>Recommended Background</strong><br />' + clean_html(clean_me(more_details['recommended_background']))
            
        if more_details['faq'] != '':
            c.full_description += '<br /><br /><strong>FAQ</strong><br />' + clean_html(clean_me(more_details['faq']))
            
        if more_details['other_description'] != '':
            c.full_description += '<br /><br /><br />' + clean_html(clean_me(more_details['other_description']))
            
            
        for g in instructors:
            temp = find_in_dict(coursera_doc['insts'],g)
            #print 'docs' + smart_str(coursera_doc['insts'])
            inst_name = temp['first_name'] + ' '+ temp['middle_name'] + ' ' + temp['last_name']
            inst_name = clean_me(inst_name)
            conn.request('GET','/maestro/api/user/instructorprofile?id='+str(temp['id']), None, header)
            iii = dict(json.loads(conn.getresponse().read())[0])
            xx = BaseInstructor.objects.get_or_create(inst_id=int(temp['id']),defaults={ 'name': inst_name, 'description' : smart_str(iii['bio']) , 'title' : smart_str(iii['title']), 'image' : iii['photo'] , 'short_name' : temp['short_name'], 'engine' : 'COURSERA' })[0] 
            Instructors_Result.append(xx)
        
        print '#################################################################'
        
        
        univv = dict(more_details['universities'][0])
        gimp = univv['logo']
        if not gimp:
            gimp =  univv['class_logo']
        c_university = common_university.objects.get_or_create(url_icon=gimp,name=univv['name'], defaults= { 'home_link':univv['home_link'] , 'short_name' : univv['abbr_name'] , 'engine' : 'COURSERA' } )[0]
        ################################################################3
        c.youtube_video = 'http://www.youtube.com/embed/' + more_details['video']
        c.course_image = more_details['photo']
        
        much_more = dict(more_details['courses'][0])
        c.duration = much_more['duration_string']
        try:
            xf = datetime.date(int(much_more['start_year']) , int(much_more['start_month']), int(much_more['start_day']) )
            c.start_date = xf
        except:
            xf = None
            pass
        c.short_description = clean_html(more_details['short_description'])
        the_course.work_load = more_details['estimated_class_workload']
        
        c.language1 = lang.objects.get_or_create(language2=str(instance['language']))[0]
        c.engine = 'COURSERA'
        c.university = c_university
        ############################################################# availability
        
        c.availability = isupcomming(much_more['duration_string'],xf)
        
        c.save()
        the_course.course = c
        
            
        the_course.save()
        
        
        for g in Instructors_Result:  
            c.instructors.add(g)
        
            
        for g in Categories_Result:
            c.categories.add(g)
            
        


