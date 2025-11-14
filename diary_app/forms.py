from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import DiaryEntry, UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email'
        }),
        label='Email'
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Логин'
        }),
        label='Логин'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Пароль'
        }),
        label='Пароль'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Подтвердите пароль'
        }),
        label='Подтверждение пароля'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Создаем профиль пользователя
            UserProfile.objects.get_or_create(user=user)
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Форма входа"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Логин'
        }),
        label='Логин'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Пароль'
        }),
        label='Пароль'
    )


class DiaryEntryForm(forms.ModelForm):
    """Форма создания/редактирования записи"""
    title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Заголовок (необязательно)'
        }),
        label='Заголовок'
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'placeholder': 'Начните писать...',
            'rows': 15
        }),
        label='Содержание'
    )
    mood = forms.ChoiceField(
        required=False,
        choices=DiaryEntry._meta.get_field('mood').choices,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Настроение'
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Теги через запятую'
        }),
        label='Теги'
    )
    is_favorite = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        }),
        label='Добавить в избранное'
    )
    
    class Meta:
        model = DiaryEntry
        fields = ('title', 'content', 'mood', 'tags', 'is_favorite')


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля"""
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'placeholder': 'Расскажите о себе...',
            'rows': 5
        }),
        label='О себе'
    )
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        }),
        label='Дата рождения'
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-input'
        }),
        label='Аватар'
    )
    
    class Meta:
        model = UserProfile
        fields = ('bio', 'birth_date', 'avatar')

