
from django.urls import path
from django.conf.urls import include
from . import views
from tagrebte.views import delete_own_comment
from rest_framework import routers


post = routers.DefaultRouter()
post.register('PostAPI',views.Post_api)


user = routers.DefaultRouter()
user.register('UserAPI',views.User_api)

comment = routers.DefaultRouter()
comment.register('CommentsAPI',views.Comments_api)





urlpatterns = [
  
    path('',views.types ,name = 'types'),
    path('about/', views.about, name="about"),
    path('<int:id>/',views.index,name = 'index'),
    path('detail/<int:post_id>/', views.post_detail, name="detail"),
    path('detail/<int:pk>/update/', views.PostUpdateView.as_view(), name="post_update"),
    path('detail/<int:pk>/delete/', views.PostDeleteView.as_view(), name="post_delete"),
    path('<int:comment_id>*<int:post_id>*', delete_own_comment, name='delete_comment'),
    path('register/', views.register, name="register"),
    path('login/', views.login_user, name="login"),
    path('logout/', views.logout_user, name="logout"),
    path('profile/', views.profile, name="profile"),
    path('profile_update/', views.profile_update, name="profile_update"),


      #api

    path('mypost_api/', include(post.urls), name='1'),
    path('myuser_api/', include(user.urls), name='2'),
    path('mycomment_api/', include(comment.urls), name='3'),

   
]
