from django.urls import path
from .views import create_account
#myapp\urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# myapp\urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',  views.movie_list, name='home'),  # Главная страница
    path('authorization', views.create_account, name='authorization'),
    path('login/', views.authorization3, name='login'),
    path('add_movie/', views.add_movie, name='add_movie'),
    path('logout/', views.user_logout, name='logout'),
    path('movies/<int:movie_id>/', views.movie_details, name='movie_details'),
    path('sessions/<int:session_id>/', views.session_details, name='session_details'),
    path('book-seats/<int:session_id>/', views.book_seat, name='book_seat'),
    # path('book_seat/', views.book_seat, name='book_seat'),
    # URL для выхода из системы
    # Страница авторизации
    # Другие URL-маршруты вашего приложения
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


