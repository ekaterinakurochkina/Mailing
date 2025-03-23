from django.contrib import admin
from .models import User


@admin.register(User)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'avatar')
    list_filter = ('email',)
    search_fields = ('email',)
