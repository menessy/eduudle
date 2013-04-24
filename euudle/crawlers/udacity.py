import bs4, re, ssl, os, sys, datetime
from httplib import *
from django.core.exceptions import *
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = "euudle.settings"
from euudle import settings
from euudle.models import *
from django.utils.encoding import smart_str, smart_unicode


header = {
    'Host': 'www.udacity.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20130220 Firefox/17.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive'
}

conn = HTTPSConnection("www.udacity.com",443)
conn.request("GET", "/courses", None, header)
response = bs4.BeautifulSoup(str(conn.getresponse().read()))
list_coursess = response.find('div', { 'class' : 'l-crs-li' } )

for i in list_coursess.find_all('li'):
    course_link =  'https://www.udacity.com' + i.a['href']
    try:
        udacity_course.objects.get( course=BaseCourse.objects.get(link=course_link) )
        continue
    except:
        pass
    course_number = course_link.split('/')[4]
    ############################################################################
    course_name = i.find('div' , { 'class' : 'crs-li-title' } ).string
    if course_name == None:
        course_name = str(i.find('div', { 'class' : 'crs-li-title' } )).split('>')[1].split('<')[0]
    
    ##############################################################################
    course_sub_name = i.find('div' , { 'class' : 'crs-li-sub' } ).string
    category = i.find('div' , { 'class' : 'crs-li-tags-category' } ).string
    dificulty = i.find('div' , { 'class' : 'level-widget' } ).get('title')
    short_description = i.find('div' , { 'class' : 'crs-li-text' } ).string
    image = 'http:' + i.img['src']
    conn.request("GET", course_link, None, header)
    response = bs4.BeautifulSoup(str(conn.getresponse().read()))
    ###################################################################################
    instructors = response.find_all('div' , { 'class' : 'inst-bio' } )
    INSTRUCTORS = []
    for g in instructors:
        instructor_name = g.h5.string
        instructor_title = g.h6.string
        instructor_image = 'http://' + g.img['src'][2:]
        description = g.find_all('p')[1].string
        instructor_name = smart_str(instructor_name).replace('\n','').replace('\t','')
        try:
            first_instructor = BaseInstructor.objects.get_or_create(image=instructor_image, defaults = { 'name' : instructor_name , 'title' : instructor_title , 'image' : instructor_image , 'description' : description } )[0]
            INSTRUCTORS.append(  first_instructor )
        except:
            pass
    
    details = response.find_all('span', { 'class' : 'pretty-format' } )[:3]
    
    c = BaseCourse()
    Course = udacity_course()
    try:
        c.youtube_video = 'http://www.youtube.com/embed/' + response.find('div' , { 'id' : 'overview-video' } )['video-id']
    except:
        c.youtube_video = None
        
    det = ''   
    for x in response.find_all('div' , { 'class' : 'row' } ):
        try:
            if not x.find('div', { 'class' : 'span9' } ).find('div', { 'class' : 'span4' } ):
                det = str(x.find('div', { 'class' : 'span9' } ).span)
        except:
            continue
    det = det.replace("<span class='pretty-format'>",'').replace('</span>','')
    c.course_image = image
    Course.more_details = det
    c.full_description = details[0].p.string
    c.short_description = smart_str(short_description).replace('\n','').replace('\t','')
    Course.full_prerequistes = details[1].p.string
    Course.outcome = details[2].p.string
    c.link = course_link
    c.course_id = course_number
    c.course_name = course_name
    Course.course_sub_name = course_sub_name
    Course.category = category
    Course.difficulty = dificulty
    c.engine = 'UDACITY'
    c.save()
    
    Course.course = c
    Course.save()
    
    for inst in INSTRUCTORS:
        c.instructors.add(inst)
