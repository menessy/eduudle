import bs4, re, ssl, os, sys, datetime
from httplib import *
from django.core.exceptions import *
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = "euudle.settings"
from euudle import settings
from euudle.models import *
from django.utils.encoding import smart_str, smart_unicode


def sub_page(page):
    soup = bs4.BeautifulSoup(page)  
    interesting = soup.find('ol', { 'class' : 'important-dates' } )
    try:
        al =  interesting.find_all('span',{ 'class' : 'start-date' } )
    except:
        al = None
    #print interesting
    try:
        Prerequisites_short = al[2].string
    except:
        Prerequisites_short = None
    try:
        end_course_date = str(interesting.find('span', { 'class' : 'final-date' } ).string)
    except:
        end_course_date = None
    try:
        work_load = al[1].string
    except:
        work_load = None

    all_description = soup.find('section', { 'class' : 'about' } )
    full_description = str(all_description.find_all('p'))

    instructors = soup.find_all('article', { 'class' : 'teacher' } )
    Intructors = []
    for inst in instructors:
        try:
            image = 'https://www.edx.org/' + inst.img['src']
        except:
            image = None
        descc = smart_str(inst.p.string)
        Intructors.append(BaseInstructor.objects.get_or_create(name=str(inst.h3.string.encode('utf-8')), defaults = { 'image' : image, 'description' : descc })[0])
    try:
        Prerequisites_full = str(soup.find('section', { 'class' : 'prerequisites' } ).p.string)
    except:
        Prerequisites_full = None
    #print Prerequisites_full
    if end_course_date:
        try:
            end_course_date = datetime.datetime.strptime(end_course_date , '%b %d, %Y')
        except ValueError:
            try:
                end_course_date = datetime.datetime.strptime(end_course_date[:-1] , '%b %d, %Y')
            except ValueError:
                try:
                    end_course_date = datetime.datetime.strptime(end_course_date[:-1] , '%B %d, %Y')
                except:
                    end_course_date = None
        except:
            end_course_date = None
    try:
        video = soup.find('section', { 'id' : 'video-modal' } ).iframe['src']
    except:
        video = None
    return [ Prerequisites_full, Prerequisites_short, end_course_date, work_load, full_description , video, Intructors ]

header = {
    'Host': 'www.edx.org',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20130220 Firefox/17.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive'
}

conn = HTTPSConnection("www.edx.org",443)
conn.request("GET","/",None,header)

soup = bs4.BeautifulSoup(conn.getresponse().read())
lista = soup.find_all('article' , { 'class' : 'course' } )


for i in lista:
    m = re.match(r'<h2><span class="course-number">(?P<n1>.*)</span>(?P<n2>.*)</h2>',str(i.find('h2'))) 
    course_number =  m.group('n1')
    try:
        BaseCourse.objects.get( link='https://www.edx.org' + str(i.a['href']) )
        continue
    except ObjectDoesNotExist: 
        course_name = m.group('n2').replace('&amp;','&')
        if course_name[0] == ' ':
            course_name = course_name[1:]
                
        m = re.match(r'<img src="(?P<name>.*)"/>' , str(i.img) )
        course_image = m.group('name')
        university = i.find('div', { 'class' :'bottom' } )
        m = re.match(r'<p>(?P<des>.*).(.*)', str(i.find('div', { 'class' : 'desc' } ).p) )
        des =  m.group('des').split('.<')
        
        university = str(university.find('a').string)
        
        short_description = des[0]                                ## short description
        starting_date = str(i.find('span', { 'class': 'start-date' } ).string)     ## starting date
        course_link =  str(i.a['href']) ## course_link
        
        conn2 = HTTPSConnection("www.edx.org",443)
        conn2.request("GET",course_link,None,header)
        lista = sub_page(conn2.getresponse().read())
        
        try:
            start_date = datetime.datetime.strptime(starting_date , '%b %d, %Y')  
        except:
            start_date = datetime.datetime.strptime(starting_date , '%B %d, %Y')  
            
        c = BaseCourse(course_id=course_number,course_name=course_name,link='https://www.edx.org' +course_link,course_image='https://www.edx.org' +course_image,short_description=short_description)    
        Course = edx_course(start_date=start_date)
        Course.end_date = lista[2]
        Course.short_prerequistes = lista[1]
        Course.full_prerequistes = lista[0]
        Course.work_load = lista[3]
        
        
        url = 'https://www.edx.org/university_profile/' + university
        try:
            uni = common_university.objects.get(home_link=url)
            #uni = edx_university.objects.get(university=uni2)
        except:    
            conn.request("GET","/university_profile/" + university,None,header)
            sss = bs4.BeautifulSoup(conn.getresponse().read())
            image = 'https://www.edx.org' + sss.find('div', { 'class' : 'logo' } ).img['src']
            uni = common_university.objects.create(home_link=url,url_icon = image, name=university,engine='EDX')
            #uni = edx_university.objects.create(university=uni2)
        
        c.university = uni
        c.full_description = smart_str(lista[4])[1:-1]
        c.youtube_video = lista[5]
        c.engine = 'EDX'
        c.save()
        Course.course = c
        Course.save()
        for inst in lista[6]:
            c.instructors.add(inst)




