from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import DiaryEntry, UserProfile, EntryImage
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    DiaryEntryForm,
    UserProfileForm
)


def home(request):
    """Главная страница (лендинг)"""
    if request.user.is_authenticated:
        return redirect('diary')
    return render(request, 'diary_app/home.html')


def register_view(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('diary')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Добро пожаловать в MeMind!')
            return redirect('diary')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'diary_app/register.html', {'form': form})


def login_view(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('diary')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('diary')
        else:
            messages.error(request, 'Неверный логин или пароль')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'diary_app/login.html', {'form': form})


def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')


@login_required
def diary_view(request):
    """Главная страница дневника со списком записей"""
    entries = DiaryEntry.objects.filter(user=request.user).prefetch_related('images')
    
    # Фильтрация
    search_query = request.GET.get('search', '')
    mood_filter = request.GET.get('mood', '')
    favorite_filter = request.GET.get('favorite', '')
    
    if search_query:
        entries = entries.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    if mood_filter:
        entries = entries.filter(mood=mood_filter)
    
    if favorite_filter == 'true':
        entries = entries.filter(is_favorite=True)
    
    # Пагинация
    paginator = Paginator(entries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Статистика
    total_entries = DiaryEntry.objects.filter(user=request.user).count()
    favorite_count = DiaryEntry.objects.filter(user=request.user, is_favorite=True).count()
    today_entries = DiaryEntry.objects.filter(
        user=request.user,
        created_at__date=timezone.now().date()
    ).count()
    
    context = {
        'page_obj': page_obj,
        'entries': page_obj,
        'search_query': search_query,
        'mood_filter': mood_filter,
        'favorite_filter': favorite_filter,
        'total_entries': total_entries,
        'favorite_count': favorite_count,
        'today_entries': today_entries,
    }
    
    return render(request, 'diary_app/diary.html', context)


@login_required
def entry_create(request):
    """Создание новой записи"""
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            
            # Обработка загруженных изображений
            images = request.FILES.getlist('images')
            for image in images:
                EntryImage.objects.create(entry=entry, image=image)
            
            messages.success(request, 'Запись успешно создана!')
            return redirect('entry_detail', pk=entry.pk)
    else:
        form = DiaryEntryForm()
    
    return render(request, 'diary_app/entry_form.html', {'form': form, 'action': 'Создать'})


@login_required
def entry_detail(request, pk):
    """Детальный просмотр записи"""
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    images = entry.images.all()
    return render(request, 'diary_app/entry_detail.html', {'entry': entry, 'images': images})


@login_required
def entry_edit(request, pk):
    """Редактирование записи"""
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            form.save()
            
            # Обработка новых загруженных изображений
            images = request.FILES.getlist('images')
            for image in images:
                EntryImage.objects.create(entry=entry, image=image)
            
            messages.success(request, 'Запись успешно обновлена!')
            return redirect('entry_detail', pk=entry.pk)
    else:
        form = DiaryEntryForm(instance=entry)
    
    return render(request, 'diary_app/entry_form.html', {'form': form, 'entry': entry, 'action': 'Редактировать'})


@login_required
def entry_delete(request, pk):
    """Удаление записи"""
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Запись удалена')
        return redirect('diary')
    
    return render(request, 'diary_app/entry_delete.html', {'entry': entry})


@login_required
def entry_toggle_favorite(request, pk):
    """Переключение избранного"""
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    entry.is_favorite = not entry.is_favorite
    entry.save()
    
    if entry.is_favorite:
        messages.success(request, 'Запись добавлена в избранное')
    else:
        messages.info(request, 'Запись удалена из избранного')
    
    return redirect('entry_detail', pk=entry.pk)


@login_required
def image_delete(request, pk):
    """Удаление изображения"""
    image = get_object_or_404(EntryImage, pk=pk, entry__user=request.user)
    entry_pk = image.entry.pk
    
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Фотография удалена')
        return redirect('entry_detail', pk=entry_pk)
    
    return redirect('entry_detail', pk=entry_pk)


@login_required
def profile_view(request):
    """Профиль пользователя"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    entries = DiaryEntry.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Статистика
    total_entries = DiaryEntry.objects.filter(user=request.user).count()
    favorite_count = DiaryEntry.objects.filter(user=request.user, is_favorite=True).count()
    
    # Статистика по месяцам
    now = timezone.now()
    months_stats = []
    for i in range(6):
        month_start = now.replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        count = DiaryEntry.objects.filter(
            user=request.user,
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        months_stats.append({
            'month': month_start.strftime('%B %Y'),
            'count': count
        })
    
    context = {
        'profile': profile,
        'entries': entries,
        'total_entries': total_entries,
        'favorite_count': favorite_count,
        'months_stats': months_stats,
    }
    
    return render(request, 'diary_app/profile.html', context)


@login_required
def profile_edit(request):
    """Редактирование профиля"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'diary_app/profile_edit.html', {'form': form})


def about_view(request):
    """О приложении"""
    return render(request, 'diary_app/about.html')


def tips_view(request):
    """Советы по ведению дневника"""
    return render(request, 'diary_app/tips.html')


def roadmap_view(request):
    """Дорожная карта"""
    return render(request, 'diary_app/roadmap.html')


def why_diary_view(request):
    """Зачем нужен дневник"""
    return render(request, 'diary_app/why_diary.html')

