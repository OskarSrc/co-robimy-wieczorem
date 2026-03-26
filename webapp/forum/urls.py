from django.urls import path
from . import views # from current folder import the neighbour file views for views methods usage

app_name = 'forum'

urlpatterns = [
    path('', views.index, name='index'),
    path('new-post/', views.post_new, name='new-post'),
    path('post/<int:post_id>/', views.post_detail, name='detail'),
]
