# posts/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug>/', views.posts, name='posts'),

    # Профайл пользователя
    path('profile/<str:username>/', views.profile, name='profile'),

    # Просмотр записи
    path('posts/<post_id>/', views.post_detail, name='post_detail'),

    # Создание записи
    path('create/', views.post_create, name='post_create'),

    # Изменение записи
    path('posts/<post_id>/edit/', views.post_edit, name='post_edit'),

    # Комментарий к записи
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),

]

handler404 = 'core.views.page_not_found'
 
# в режиме DEBUG=True брать картинки из директории, указанной в MEDIA_ROOT
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    