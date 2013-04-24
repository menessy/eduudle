import re
from euudle.models import *
from django.db.models import Q
from django.db.models.query import EmptyQuerySet
import ast

def transformQuery(x):
    weDict = {}
    price = []
    university = []
    rating = []
    subject = []
    availability = []
    course_level = []
    lang = []
    other = []
    sorting = []
    listOfStrings = []
    listOfStrings.append(x[7:])
    for i in range(len(x)):
        if x[i] == '&':
            listOfStrings.append(x[i + 1:])
    newL = [r[:r.find('""')].split('="') for r in listOfStrings]
    for s in newL:
        if s[0] == 'pricerange':
            weDict['pricerange'] = s[1]
        elif s[0] == 'term':
            weDict['term'] = s[1]
        elif s[0] == 'price':
            price.append(s[1])
        elif s[0] == 'university':
            university.append(s[1])
        elif s[0] == 'rating':
            rating.append(s[1])
        elif s[0] == 'subject':
            subject.append(s[1])
        elif s[0] == 'availability':
            availability.append(s[1])
        elif s[0] == 'course_level':
            course_level.append(s[1])
        elif s[0] == 'lang':
            lang.append(s[1])
        elif s[0] == 'other':
            other.append(s[1])
        elif s[0] =='sorting':
            sorting.append(s[1])
    
    if price:
        weDict['price'] = price
    if university:
        weDict['university'] = university
    if rating:
        weDict['rating'] = rating
    if subject:
        weDict['subject'] = subject
    if availability:
        weDict['availability'] = availability
    if course_level:
        weDict['course_level'] = course_level
    if lang:
        weDict['lang'] = lang
    if other:
        weDict['other'] = other
    if sorting:
        weDict['sorting'] = sorting[-1]
    if 'term' not in weDict.keys():
        weDict['term'] = ''
    
    return weDict


class RapidSearch(object):
    
    def term(self, name, base):
        lista = name.split(' ')
        if base != None:
            #return base.filter( Q(course_name__icontains=name) | Q(full_description__icontains=name) | Q(short_description__icontains=name) )
            
            return base.filter( reduce(lambda x, y: x & y, [Q(course_name__icontains=word) for word in lista]) | reduce(lambda x, y: x & y, [Q(short_description__icontains=word) for word in lista]) | reduce(lambda x, y: x & y, [Q(full_description__icontains=word) for word in lista]) ) 
                
        
        return BaseCourse.objects.filter( reduce(lambda x, y: x & y, [Q(course_name__icontains=word) for word in lista]) | reduce(lambda x, y: x & y, [Q(short_description__icontains=word) for word in lista]) | reduce(lambda x, y: x & y, [Q(full_description__icontains=word) for word in lista])  )
        
        
    def price(self, name, base):
        st = name.split(';')
        if base != None: 
            return base.filter(cost__gte=st[0]).filter(cost__lte=st[1] )
        
        return BaseCourse.objects.filter(cost__gte=st[0]).filter(cost__lte=st[1] )
        
        
    def pricerange(self, name, base):
        st = name.split(';')
        if base != None: 
            return base.filter(cost__gte=st[0]).filter(cost__lte=st[1] )
        
        return BaseCourse.objects.filter(cost__gte=st[0]).filter(cost__lte=st[1] )
        
    def university(self, pk, base):
        if base != None:
            return base.filter(university__pk__in = ast.literal_eval(pk) )
        
        return BaseCourse.objects.filter(university__pk__in = ast.literal_eval(pk) ) 
        
    def subject(self, name, base):                                      
    
        if base != None:
            g = BaseCourse.objects.none()
            for x in ast.literal_eval(name):
                temp = base & common_category.objects.get(id=x).basecourse_set.all()
                g = g | temp
            return g
            
        g = BaseCourse.objects.none()
        for x in ast.literal_eval(name):
            g = g | common_category.objects.get(id=x).basecourse_set.all()
        return g
    
    def lang(self, name, base):                                         
        if base != None:
            g = BaseCourse.objects.none()
            for x in ast.literal_eval(name):
                temp = base & lang.objects.get(language2=x).basecourse_set.all()
                g = g | temp
            return g
            
        g = BaseCourse.objects.none()
        for x in ast.literal_eval(name):
            g = g | lang.objects.get(language2=x).basecourse_set.all()
        return g
        
    def availability(self, name, base):
        if base != None:
            return base.filter(availability__in=ast.literal_eval(name))
            
        return BaseCourse.objects.filter(availability__in=ast.literal_eval(name))
        
        
    def rating(self,name ,base):
    
        if base != None:
            return base.filter(rating__in=ast.literal_eval(name))
            
        return BaseCourse.objects.filter(rating__in=ast.literal_eval(name))
        
    def sorting(self, name, base):
        pass
        
         
def another_redundant_layer(q,term):
    lista = term.split(' ')
    course_name = q.filter( reduce(lambda x, y: x & y, [Q(course_name__icontains=word) for word in lista]) ) 
    short = q.filter( reduce(lambda x, y: x & y, [Q(short_description__icontains=word) for word in lista] ) ) 
    full = q.filter( reduce(lambda x, y: x & y, [Q(full_description__icontains=word) for word in lista])  )
    
    result = []
    for x in course_name:
        if x not in result:
            result.append(x)
    for x in short:
        if x not in result:
            result.append(x)
    for x in full:
        if x not in result:
            result.append(x)
        
    return result
        
def get_universities_from_courses(q):
    start = []
    lista = []
    for i in q:
        if i.university not in lista:
            numbers = q.filter(university=i.university).count()
            start.append( [ i.university.id, i.university.name , numbers ] )
            lista.append( i.university )
    return sorted( start , key = lambda x:x[2] ,reverse=True)

    
def categorize_search(string):
    filters = [ 'term' , 'price' , 'university', 'rating', 'subject', 'availability' , 'duration' , 'level' , 'lang' , 'other' ]
    c = {}
    for i in filters:
        start = string.find(i)
        if start != -1:
            end = string.find('&',start+1)
            true_end =  string.find('&',end+1)
            if re.search('=',true_end):
                c[i] = string[start+len(i):end]
            else:
                c[i] = string[start+len(i):true_end]                
    return c
        
    
