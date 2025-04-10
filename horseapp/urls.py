from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('fixtures/<int:year>/<int:fixture_id>/', views.fixture_detail, name='fixture_detail'),
]