import bs4, re, ssl, os, sys, datetime
from httplib import *
from django.core.exceptions import *
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = "euudle.settings"
from models import *
from django.utils.encoding import smart_str, smart_unicode
import re

def clear_div_span(html):
    html = re.sub('(<div(.*)>)|(</div>)','',html)
    html = re.sub("<span class='pretty-format'>",'',html)
    html = re.sub('<span class="pretty-format">','',html)
    return re.sub("</span>",'',html)


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
        cosmatic = BaseCourse.objects.get_or_create(link=course_link)[0]
        udacity_course.objects.get( course=cosmatic )
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
    #short_description = i.find('div' , { 'class' : 'crs-li-text' } ).string
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
            first_instructor = BaseInstructor.objects.get_or_create(image=instructor_image, defaults = { 'name' : instructor_name , 'title' : instructor_title , 'image' : instructor_image , 'description' : description, 'engine' : 'UDACITY' } )[0]
            INSTRUCTORS.append(  first_instructor )
        except:
            pass
    
    details = response.find_all('span', { 'class' : 'pretty-format' } )[:3]
    try:
        c = BaseCourse.objects.get(link=course_link)
    except:
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
    c.language1 = lang.objects.get_or_create(language2='en')[0]
    Course.more_details = det
    c.short_description = smart_str(details[0].p.string)
    c.full_description = clear_div_span(smart_str(response.find('div', { 'class' : 'row-fluid syllabus' } )))
    
    c.link = course_link
    c.course_id = course_number
    c.course_name = course_name
    
    c.university = common_university.objects.get_or_create(name='UDACITY',engine='UDACITY')[0]
    
    c.engine = 'UDACITY'
    c.availability = 'Self-paced'
    c.save()
    
    Course.full_prerequistes = smart_str(details[1].p.string)
    Course.outcome = smart_str(details[2].p.string)
    Course.difficulty = smart_str(dificulty)
    Course.course_sub_name = smart_str(course_sub_name)
    Course.course = c
    Course.save()
    
    try:
        g = common_category.objects.get_or_create(category_name=smart_str(category))[0]
    except:
        g = common_category.objects.filter(category_name=smart_str(category))[0]
    c.categories.add(g)
    
    for inst in INSTRUCTORS:
        c.instructors.add(inst)
        
    
