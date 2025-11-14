from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class DiaryEntry(models.Model):
    """Модель записи в дневнике"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diary_entries', verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Заголовок', blank=True)
    content = models.TextField(verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    mood = models.CharField(
        max_length=20,
        choices=[
            ('happy', '😊 Счастливый'),
            ('sad', '😢 Грустный'),
            ('excited', '🤩 Взволнованный'),
            ('calm', '😌 Спокойный'),
            ('anxious', '😰 Тревожный'),
            ('grateful', '🙏 Благодарный'),
            ('tired', '😴 Усталый'),
            ('motivated', '💪 Мотивированный'),
        ],
        blank=True,
        null=True,
        verbose_name='Настроение'
    )
    tags = models.CharField(max_length=255, blank=True, verbose_name='Теги (через запятую)')
    is_favorite = models.BooleanField(default=False, verbose_name='Избранное')
    
    class Meta:
        verbose_name = 'Запись дневника'
        verbose_name_plural = 'Записи дневника'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%d.%m.%Y')}"
    
    def get_absolute_url(self):
        return reverse('entry_detail', kwargs={'pk': self.pk})
    
    def get_tags_list(self):
        """Возвращает список тегов"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []


class EntryImage(models.Model):
    """Модель изображения для записи дневника"""
    entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE, related_name='images', verbose_name='Запись')
    image = models.ImageField(upload_to='diary_images/%Y/%m/%d/', verbose_name='Изображение')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Подпись')
    
    class Meta:
        verbose_name = 'Изображение записи'
        verbose_name_plural = 'Изображения записей'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Изображение для записи {self.entry.pk}"


class UserProfile(models.Model):
    """Расширенный профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    bio = models.TextField(max_length=500, blank=True, verbose_name='О себе')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f"Профиль {self.user.username}"

