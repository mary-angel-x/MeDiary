from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import DiaryEntry, UserProfile, EntryImage


@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    """Админка для записей дневника"""
    list_display = ('id', 'user', 'title_preview', 'mood', 'created_at', 'is_favorite', 'content_preview')
    list_filter = ('created_at', 'mood', 'is_favorite', 'user')
    search_fields = ('title', 'content', 'user__username', 'tags')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_per_page = 25
    list_editable = ('is_favorite',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'title', 'content', 'mood')
        }),
        ('Дополнительно', {
            'fields': ('tags', 'is_favorite')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_preview(self, obj):
        """Превью заголовка"""
        if obj.title:
            return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
        return 'Без заголовка'
    title_preview.short_description = 'Заголовок'
    
    def content_preview(self, obj):
        """Превью содержимого"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Содержание'
    
    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(EntryImage)
class EntryImageAdmin(admin.ModelAdmin):
    """Админка для изображений записей"""
    list_display = ('id', 'entry', 'image_preview', 'caption', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('entry__title', 'entry__content', 'caption')
    readonly_fields = ('uploaded_at', 'image_preview')
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('entry', 'image', 'image_preview', 'caption')
        }),
        ('Дата загрузки', {
            'fields': ('uploaded_at',)
        }),
    )
    
    def image_preview(self, obj):
        """Превью изображения"""
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 8px;" />', obj.image.url)
        return 'Нет изображения'
    image_preview.short_description = 'Превью'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Админка для профилей пользователей"""
    list_display = ('user', 'birth_date', 'created_at', 'avatar_preview')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'bio')
    readonly_fields = ('created_at', 'avatar_preview')
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Информация', {
            'fields': ('bio', 'birth_date', 'avatar', 'avatar_preview')
        }),
        ('Дата регистрации', {
            'fields': ('created_at',)
        }),
    )
    
    def avatar_preview(self, obj):
        """Превью аватара"""
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.avatar.url)
        return 'Нет аватара'
    avatar_preview.short_description = 'Аватар'


# Расширяем админку пользователей
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'


class CustomUserAdmin(BaseUserAdmin):
    """Расширенная админка пользователей"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'entry_count')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    
    def entry_count(self, obj):
        """Количество записей пользователя"""
        return obj.diary_entries.count()
    entry_count.short_description = 'Записей'


# Перерегистрируем админку пользователей
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Настройки админки
admin.site.site_header = 'MeMind - Администрирование'
admin.site.site_title = 'MeMind Admin'
admin.site.index_title = 'Панель управления дневником'

