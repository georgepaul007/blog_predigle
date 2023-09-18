from django.urls import path
from .views import create_post, get_posts, get_three_posts, update_post, delete_post, get_by_filter

urlpatterns = [
    path('<slug:slug>', create_post),
    path('', get_posts),
    path('get_three_recent/', get_three_posts),
    path('update/<slug:slug>/', update_post),
    path('delete/<slug:slug>', delete_post),
    path('filter/', get_by_filter)
]