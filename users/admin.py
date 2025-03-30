from django.contrib import admin
from .models import User


@admin.register(User)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email',)
    list_filter = ('email',)
    search_fields = ('username','email',)
