from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    
    # Аутентификация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Дневник
    path('diary/', views.diary_view, name='diary'),
    path('entry/create/', views.entry_create, name='entry_create'),
    path('entry/<int:pk>/', views.entry_detail, name='entry_detail'),
    path('entry/<int:pk>/edit/', views.entry_edit, name='entry_edit'),
    path('entry/<int:pk>/delete/', views.entry_delete, name='entry_delete'),
    path('entry/<int:pk>/toggle-favorite/', views.entry_toggle_favorite, name='entry_toggle_favorite'),
    path('image/<int:pk>/delete/', views.image_delete, name='image_delete'),
    
    # Профиль
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Информационные страницы
    path('about/', views.about_view, name='about'),
    path('tips/', views.tips_view, name='tips'),
    path('roadmap/', views.roadmap_view, name='roadmap'),
    path('why-diary/', views.why_diary_view, name='why_diary'),
]

