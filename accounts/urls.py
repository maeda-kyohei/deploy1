from django.urls import path
from django.conf import settings  # Import settings module
from django.conf.urls.static import static 
from .views import (
    RegistUserView,  UserLoginView,
    UserLogoutView, MyView, FriendPostView, MyPostView, DetailPostView, CreatePostView, UpdatePostView,
    DeletePostView, LikeHomeView, LikeDetailView, FollowHomeView, FollowDetailView, FollowListView, ProfileEditView,
    PinPostView, UnpinPostView, BookCountView, NoticeView, CommentCreateView
)

app_name = 'accounts'
urlpatterns = [
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user_logout/', UserLogoutView.as_view(), name='user_logout'),
    path('mypage/', MyView.as_view(), name='mypage'),
    path('friendpost/', FriendPostView.as_view(), name='friendpost'),
    path('mypost/', MyPostView.as_view(), name='mypost'),
    path('detail/<int:pk>', DetailPostView.as_view(), name='detail'),
    path('detail/<int:pk>/update', UpdatePostView.as_view(), name='update'),
    path('detail/<int:pk>/delete', DeletePostView.as_view(), name='delete'),
    path('create/', CreatePostView.as_view(), name='create'),
    path('like-home/<int:pk>', LikeHomeView.as_view(), name='like-home'),
    path('like-detail/<int:pk>', LikeDetailView.as_view(), name='like-detail'),
    path('follow-home/<int:pk>', FollowHomeView.as_view(), name='follow-home'),
    path('follow-detail/<int:pk>', FollowDetailView.as_view(), name='follow-detail'),
    path('follow-list/', FollowListView.as_view(), name='follow-list'),
    path('edit_profile/', ProfileEditView.as_view(), name='edit_profile'),
    path('pin/<int:pk>', PinPostView.as_view(), name='pin-post'),
    path('unpin/<int:pk>', UnpinPostView.as_view(), name='unpin-post'),
    path('book_count/', BookCountView.as_view(), name='book_count'),
    path('notice/', NoticeView.as_view(), name='notice'),
    path('detail/<int:pk>/comment/', CommentCreateView.as_view(), name='comment'),

]
