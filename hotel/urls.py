from django.urls import path
from . import views


app_name = 'hotel'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('index/', views.IndexView.as_view(), name='index'),
    path('blog/', views.PostListView.as_view(), name='blog'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow,name='unfollow'),
    path('like/', views.like_post, name='like-post'),
    path('user/<str:username>/', views.UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/new', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('contact/', views.contact, name='contact'),
    path('notifications/', views.NotificationsView.as_view(), name='notifications'),
    path('about_us/', views.About_usView.as_view(), name='about_us'),
    path('stay/', views.StayView.as_view(), name='stay'),
    path('gallery/', views.GalleryView.as_view(), name='gallery'),
    path('unforgettable_location/', views.Unforgettable_locationView.as_view(), name='unforgettable_location'),
    path('extraordinary_moments/', views.Extraordinary_momentsView.as_view(), name='extraordinary_moments'),
    path('exciting_attractions/', views.Exciting_attractionsView.as_view(), name='exciting_attractions'),
    path('unbelievable_offers/', views.Unbelievable_offersView.as_view(), name='unbelievable_offers'),

    path('inbox/', views.inbox, name='messages_inbox'),
    path('outbox/', views.outbox, name='messages_outbox'),
    path('compose/', views.compose, name='messages_compose'),
    path('compose/<recipient>/', views.compose, name='messages_compose_to'),
    path('reply/<message_id>/', views.reply, name='messages_reply'),
    path('view/<message_id>/', views.view, name='messages_detail'),
    path('delete/<message_id>/', views.delete, name='messages_delete'),
    path('undelete/<message_id>/', views.undelete, name='messages_undelete'),
    path('trash/', views.trash, name='messages_trash'),
]