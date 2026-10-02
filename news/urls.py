"""URL patterns for the news application."""

from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
    path('', views.home, name='home'),
    path(
        'article/<slug:slug>/',
        views.article_detail,
        name='article_detail',
    ),
    path(
        'category/<slug:slug>/',
        views.category_list,
        name='category_list',
    ),
]