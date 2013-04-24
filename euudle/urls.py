from django.conf.urls import patterns, include, url
import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^$', 'euudle.views.home', name='home'),
    url(r'^login$', 'euudle.views.login' ),
    url(r'^logout$', 'euudle.views.logout' ),
    url(r'^ajaxsearch$', 'euudle.views.ajaxsearch'),
    url(r'^search', 'euudle.views.search'),
    url(r'^register$' , 'euudle.views.register'),
    url(r'^drop_course/(?P<course>.*)$', 'euudle.views.drop_course'),   ## not yet
    url(r'^review$', 'euudle.views.review'),
    url(r'^coursewall$', 'euudle.views.coursewall'),
    url(r'^profile$', 'euudle.views.profile'),
    url(r'^promote/(?P<status>.*)$', 'euudle.views.promote'),
    url(r'^course/(?P<course>.*)$', 'euudle.views.course'),
    
    url(r'^add_to_coursewall/(?P<course>.*)$', 'euudle.views.add_coursewall'),
    url(r'^check_ratings$' , 'euudle.views.check_ratings'),
    url(r'^facebook/', include('django_facebook.urls')),
    url(r'^accounts/', include('django_facebook.auth_urls')),
    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.STATIC_ROOT}),
)


if settings.MODE == 'userena':
    urlpatterns += patterns('',(r'^accounts/', include('userena.urls')),)
elif settings.MODE == 'django_registration':
    urlpatterns += patterns('',(r'^accounts/', include('registration.backends.default.urls')), )

