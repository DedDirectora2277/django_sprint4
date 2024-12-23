from django.urls import path

from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),

    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/delete/', views.post_delete_view,
         name='delete_post'),
    path('posts/<int:post_id>/edit/', views.post_edit_view, name='edit_post'),
    path('posts/create/', views.post_create_view, name='create_post'),
    path('posts/<int:post_id>/comment/',
         views.comment_create_view, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.comment_edit_view, name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.comment_delete_view, name='delete_comment'),

    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile')
]
