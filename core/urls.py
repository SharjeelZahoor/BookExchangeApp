from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import password_change_view 


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('books/', views.book_list, name='book_list'),
    path('my-books/', views.my_books, name='my_books'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),

    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/<int:book_id>/request/', views.request_exchange, name='request_exchange'),

    path('my-requests/', views.my_sent_requests, name='my_sent_requests'),
    path('requests-received/', views.my_received_requests, name='my_received_requests'),

    path('requests/handle/<int:request_id>/', views.handle_request, name='handle_request'),

    path('chat/<int:request_id>/', views.chat_view, name='chat'),

    path('requests/<int:request_id>/rate/', views.submit_rating, name='submit_rating'),
    
    #reset password
    path('password-change/', password_change_view, name='password_change'),
     

    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
