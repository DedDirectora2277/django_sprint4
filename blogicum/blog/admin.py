from django.contrib import admin
from .models import Location, Category, Post, Comment


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('is_published',)
    ordering = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('title', 'slug')
    list_filter = ('is_published',)
    ordering = ('title',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'category', 'location',
        'is_published', 'pub_date', 'created_at'
    )
    list_editable = ('is_published', 'category', 'location')
    search_fields = ('title', 'text')
    list_filter = ('category', 'location', 'is_published', 'pub_date')
    ordering = ('title',)
    date_hierarchy = 'pub_date'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text', 'post', 'author',
        'is_published', 'created_at'
    )
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    ordering = ('-created_at',)
    search_fields = ('title', 'text')
    date_hierarchy = 'created_at'
