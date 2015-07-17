from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),

    (r'^test$','atap.views.test'),

    (r'^$', 'atap.views.list_tools'),
    (r'^accounts/login/$',  'atap.views.login'),
    (r'^accounts/logout/$', "atap.views.logout"),
    (r'^accounts/changepwd/$', 'atap.views.changepwd'),

    url(r'^tools/$', 'atap.views.list_tools', name="tool-list-page"),
    url(r'^tool/add/$', 'atap.views.add_tool', name="tool-add-page"),
    url(r'^tool/(\d+)/$', 'atap.views.modify_tool', name='tool-modify-page'),
    url(r'^view/(\d+)/$', 'atap.views.view_tool', name="tool-detail-page"),
    url(r'^init/(\d+)/$', 'atap.views.init', name="init-tool"),
    url(r'^del/(\d+)/$','atap.views.delete_tool', name="del-tool"),


    url(r'^tool/(\d+)/input/add/$', 'atap.views.add_input', name="input-add-page"),
    url(r'^tool/(\d+)/input/(\d+)/$', 'atap.views.modify_input', name="input-modify-page"),
    url(r'^tool/(\d+)/input/(\d+)/del$','atap.views.delete_input',name="input-delete-page"),

    url(r'^tool/(\d+)/param/add/$', 'atap.views.add_param', name="param-add-page"),
    url(r'^tool/(\d+)/param/(\d+)/$', 'atap.views.modify_param', name="param-modify-page"),
    url(r'^tool/(\d+)/param/(\d+)/del$', 'atap.views.delete_param', name="param-delete-page"),

    url(r'^tool/(\d+)/output/add/$', 'atap.views.add_output', name="output-add-page"),
    url(r'^tool/(\d+)/output/(\d+)/$', 'atap.views.modify_output', name="output-modify-page"),
    url(r'^tool/(\d+)/output/(\d+)/del$', 'atap.views.delete_output', name="output-delete-page"),

)


