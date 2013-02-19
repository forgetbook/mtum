from django.conf.urls import patterns, include, url
# from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # url(r'^$', TemplateView.as_view(template_name='base.html')),

    # Examples:
    # url(r'^$', '{{ project_name }}.views.home', name='home'),
    # url(r'^{{ project_name }}/', include('{{ project_name }}.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)


urlpatterns += patterns(
    '',
    url(r'^register$', 'account.views.register', name='register'),
    url(r'^login$', 'account.views.login', name='login'),
    url(r'^logout$', 'account.views.logout', name='logout'),
    url(r'^forgot_password$', 'account.views.forgot_password',
        name='forgot_password')
)

urlpatterns += patterns(
    'dashboard.views',
    url(r'^$', 'index', name='index'),
    url(r'^search$', 'search', name='search'),
    url(r'^tagged/(?P<keyword>[-\w]+)$', 'search_result', name='tagged'),

    url(r'^dashboard$', 'dashboard', name='dashboard'),
    url(r'^mine$', 'dashboard', {'posts_filter': 'mine'}, name='mine'),
    url(r'^likes$', 'dashboard', {'posts_filter': 'likes'}, name='likes'),
    url(r'^following$', 'dashboard', {'posts_filter': 'following'},
        name='following'),

    url(r'^new/text$', 'new_text', name='new_text'),
    url(r'^new/photo$', 'new_photo', name='new_photo'),
    url(r'^new/video$', 'new_video', name='new_video'),
    # url(r'^settings$', 'settings', name='settings'),
    # url(r'^new-text$', 'post.views.new_post', name='new_post_text'),
    url(r'^delete/(?P<post_id>\d+)$', 'delete_post', name='delete_post'),
)

urlpatterns += patterns(
    'post.views',
    url(r'^like/(?P<post_id>\d+)$', 'like', name='like'),
    url(r'^unlike/(?P<post_id>\d+)$', 'unlike', name='unlike'),
    url(r'^reblog/(?P<post_id>\d+)$', 'reblog', name='reblog'),
    url(r'^follow/(?P<user_slug>[-\w+]+)$', 'follow', name='follow'),
    url(r'^unfollow/(?P<user_slug>[-\w+]+)$', 'unfollow', name='unfollow'),

    url(r'^blog/(?P<user_slug>[-\w]+)$', 'user_index', name='user_index'),
    url(r'^blog/(?P<user_slug>[-\w]+)/tagged/(?P<tag_slug>[-\w]+)$',
        'user_index', name='user_tag'),
    url(r'^blog/(?P<user_slug>[-\w]+)/random$', 'random_post', name='random'),

    url(r'^blog/(?P<user_slug>[-\w]+)/search$', 'user_search',
        name='user_search'),
    url(r'^blog/(?P<user_slug>[-\w]+)/search/(?P<keyword>[ -\+\w]+)$',
        'user_search_result', name='user_search_result'),

    url(r'^blog/(?P<user_slug>[-\w]+)/post/(?P<post_id>\d+)$',
        'detail', name='post_detail'),
    url(r'^blog/(?P<user_slug>[-\w]+)/post/(?P<post_id>\d+)/'
        + r'(?P<post_slug>[-\w]+)$', 'detail', name='post_detail_slug'),
)
