from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('racecourse/<int:course_id>/<str:fixture_date>/<str:course_name>/', views.racecourse_redirect_to_fixture, name='racecourse_redirect'),
    path('fixtures/<int:year>/<int:fixture_id>/<str:course_name>/', views.fixture_detail, name='fixture_detail'),
    path('race/<int:year>/<int:race_id>/<str:race_name>/', views.race_detail, name='race_detail'),
]