from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('racecourse/<int:course_id>/<str:fixture_date>/<str:course_name>/', views.racecourse_redirect_to_fixture, name='racecourse_redirect'),
    path('fixtures/<int:year>/<int:fixture_id>/<str:course_name>/', views.fixture_detail, name='fixture_detail'),
    re_path(r'^race/(?P<year>[0-9]+)/(?P<race_id>[0-9]+)/(?P<race_name>.+)/$', views.race_detail, name='race_detail'),
]