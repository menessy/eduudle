from django.shortcuts import render_to_response
from django.template import Context, loader, RequestContext
from django.views.decorators.csrf import csrf_exempt
from euudle.search import categorize_search , RapidSearch, transformQuery, get_universities_from_courses, another_redundant_layer
from euudle.models import *
from django.http import *
from accounts.models import *
import re, time, datetime
from django.db.models import Count
from random import choice
from get_rating import *
from django import forms


def log(view):
    def new_view(request, *args, **kwargs):
        ip_r = request.META.get('REMOTE_ADDR','')
        heade_r = request.META.get('HTTP_USER_AGENT','')
        try:
            statistical_data.objects.create(ip=ip_r,header=heade_r)
        except:
            pass
        return view(request, *args, **kwargs)
    return new_view

@csrf_exempt
def logout(request):
    return HttpResponseRedirect('/')

@csrf_exempt
def promote(request, status):
    
    r = request.POST
    review = Review.objects.get( id=r.get('review') )
    
    if not request.META['account']:
        return HttpResponse(str(review.agree+review.disagree))
    
    if review in request.META['account'].who_voted.all():
        return HttpResponse(str(review.agree+review.disagree))
    
    request.META['account'].who_voted.add(review)
    if status == 'agree':
        review.agree += 1
    elif status == 'disagree':
        review.disagree += 1
    review.save()
    return HttpResponse(str(review.agree+review.disagree))
    
def check(d):
    if int(d) in [ 1,2,3,4,5 ]:
        return int(d)
    return False

def cal_rate(previous,number_of_votes,recent):
    return ( previous  + recent )/ (number_of_votes+1)

@csrf_exempt
def review(request):
    r = request.POST
    course = BaseCourse.objects.get(id=r.get('course_id',None))
  
    
    if course.reviews.filter(account=request.META['account']):
        return HttpResponse('You already commented')
    else:
        #################################################################
        cr = check(r.get('cr',None))
        
        if cr:
            course.content_rich = cal_rate(course.content_rich , course.content_rich_n , cr)
            course.content_rich_n += 1
        interactive = check(r.get('interactive',None)) 
        if interactive:
            course.engaging = cal_rate(course.engaging , course.engaging_n , interactive)
            course.engaging_n += 1
        enjoyable = check(r.get('enjoyable',None))
        if enjoyable:
            course.enjoyable = cal_rate(course.enjoyable, course.enjoyable_n, enjoyable)
            course.enjoyable_n += 1
        co = check(r.get('co',None))
        if co:
            course.career_oriented = cal_rate(course.career_oriented, course.career_oriented_n, co)
            course.career_oriented_n += 1
        #return HttpResponse(cr + ' ' + co + ' ' + enjoyable + ' ' + interactive)
        if r.get('text',None):
            rev = Review.objects.create(review = r.get('text',None) )    
            request.META['account'].reviews.add(rev)
            course.reviews.add(rev)
            
        course.save()
    return HttpResponseRedirect( '/course/'+r.get('course_id',None) )

@csrf_exempt
def register(request):
    r = request.GET
    email = r.get('email')
    try:
        name = re.match(r"(.*)@", email).group(0)[:-1]
    except:
        name = 'Anonymous'
    password = r.get('password')
    
    x , y = Account.objects.register(name,password,email)
    if not x:
        return HttpResponse(y)
    
    request.META['authenticated2'] = Account.objects.is_valid(email,password)[1]
    
    return HttpResponseRedirect('/coursewall')

@csrf_exempt
def login(request):
    return HttpResponseRedirect('/coursewall')

    
@csrf_exempt
def profile(request):
    
    if request.method == 'POST':
        r = request.POST
        usr = request.META['account']
        usr.gender2 = r.get('gender','')
        usr.name = r.get('name','')
        usr.website = r.get('web','')
        usr.common_address = r.get('loc','')
        usr.description = r.get('about','')
        
        usr.facebook_page = r.get('fb','')
        usr.twitter_account = r.get('tw','')
        usr.linkedin_account = r.get('ln','')
        usr.google_plus_account = r.get('google','')
        usr.github_account = r.get('gh','')
        
        try:
            usr.birthday = datetime.date( int(r.get('year')) , int(r.get('month')) , int(r.get('day')) )
        except:
            pass
        try:
            usr.avatar = request.FILES['file_img']
        except:
            pass
        usr.save()
        
    return render_to_response("profile.html", { 'logged' : request.META['account'] } , RequestContext(request) )

@csrf_exempt
def home(request):
    if Sessions.objects.check_session(request.COOKIES.get('SEHS')) != None:
        return HttpResponseRedirect('/coursewall')
        
    featured = BaseCourse.objects.filter(featured=True)
    f1 = featured[:3]
    f2 = featured[3:6]
    f3 = featured[6:9]
    return render_to_response("home.html", { 'number_of_courses' : BaseCourse.objects.all().count(),'logged' : request.META['account'], 'f1' : f1, 'f2': f2, 'f3' : f3 }, RequestContext(request))
    
def coursewall(request):
    c = {}
    c['logged'] = request.META['account']
    c['featured'] = choice(BaseCourse.objects.filter(featured=True))
    return render_to_response("coursewall.html", c , RequestContext(request) )    
    
def course(request, course):

    Course = BaseCourse.objects.get(pk=course)
    user = Sessions.objects.check_session(request.COOKIES.get('SEHS'))
    Course.clicks += 1
    Course.save()
    return render_to_response("courseDetail.html", { 'course' : Course, 'logged': user  } , RequestContext(request))


@csrf_exempt
def add_coursewall(request, course):
    
    account = request.META['account']
    try:
        f_course = BaseCourse.objects.get(pk=course)
        if f_course in account.courses.all():
            return HttpResponse('no')
        f_course.coursewall_number += 1
        f_course.save()
        account.courses.add(f_course)
        return HttpResponse('yes')
    except:
        pass
    return HttpResponse('no')
    
    
    
@csrf_exempt 
def check_ratings(request):
    
    course_number = request.POST.get('course_number','1')
    n_votes , rating = getrating(course_number)
    course = BaseCourse.objects.get(pk=course_number)
    course.rating = rating
    course.rating_n = n_votes
    course.save()
        
    return HttpResponse()

@csrf_exempt   
def ajaxsearch(request):
    filter_dict = transformQuery(request.POST['query'])
    try:
        if filter_dict['term'] == 'I want to learn...':
            filter_dict['term'] = ''
    except:
        filter_dict['term'] = ''
    result = None
    #return HttpResponse(str(filter_dict))
    for element in filter_dict:
        result = getattr(RapidSearch, element)( RapidSearch() , str(filter_dict[element]), result )
    
    res = {}
    sorting = filter_dict.get('sorting','')
    term = filter_dict.get('term','')
    
    if sorting == 'rating':
        res = { 'courses' : result.order_by('-rating') }
    elif sorting == 'date':
        res = { 'courses' : result.order_by('start_date') }
    elif sorting == 'price':
        res = { 'courses' : result.order_by('cost') }
    elif sorting == 'addcount':
        res = { 'courses' : result.order_by('coursewall_number') }
    else:
        res = { 'courses' : another_redundant_layer( result, term ) }

    return render_to_response("ajaxsearch.html", res , RequestContext(request))

@csrf_exempt   
def drop_course(request, course):
    
    account = request.META['account']
    try:
        f_course = BaseCourse.objects.get(pk=course)
        if f_course in account.courses.all():
            f_course.coursewall_number -= 1
            f_coourse.save()
            account.courses.remove(f_course)
            return HttpResponseRedirect('/coursewall')
        return HttpResponse('no')
    except:
        pass
    return HttpResponse('no')

@log
def search(request):
    r = request.GET        
    result = None
    
        
    if r.get('term') != 'I want to learn...':
        for element in r:
            result = getattr(RapidSearch, element)( RapidSearch() , str(r[element]), result ) 
            
    else:
        result = BaseCourse.objects.all()
    result = result.order_by('engine')    ############## here the sorting
    if r.get('term') != 'I want to learn...':
        res = { 'courses' : another_redundant_layer( result, r.get('term','') ) }
    else:
        res = { 'courses' : another_redundant_layer( result, '' ) }
    #return HttpResponse(result)
    all_universities = get_universities_from_courses(result)
    res['universities1'] = all_universities[:5]
    res['universities2'] = all_universities[5:]
    #distinct_universities.annotate(basecourse_count=Count('basecourse')).order_by('-basecourse_count')
    res['price_range'] = ['0','100']
    res['ratings'] = [ ( i , result.filter(rating=i).count() ) for i in [5,4,3,2,1,0] ]
    res['logged'] = request.META['account']
    
    langs = []
    cats1 = []
    cats2 = []
    langs2 = []
    al_lang = 0
    for x in result:
        if x.language1.language2 not in langs2:
            temp = result.filter(language1__language2=x.language1.language2).count()
            langs.append( [ x.language1.language2 , temp ] )
            langs2.append(x.language1.language2)
            al_lang += temp
    
    for x in result:
        for g in x.categories.all():
            if g not in cats2:
                cats1.append( [ g.id ,  g.category_name , result.filter(categories=g).count() ] )
                cats2.append(g)
            
    res['al_lang'] = al_lang
    res['languages'] = langs
    res['crs_avail_s'] =  [  (x[0] , result.filter(availability=x[0]).count() )  for x in AVAILABILITY ]
    res['subjects'] = cats1 
    res['count_courses'] = result.count()
    res['term'] = r.get('term','')
    
    return render_to_response("search.html", res, RequestContext(request))
    
