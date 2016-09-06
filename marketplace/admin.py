from django.contrib import admin
from .models import SasviewModel, ModelFile, Comment, Category

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'model', 'content_truncated')

@admin.register(ModelFile)
class ModelFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'model')

@admin.register(SasviewModel)
class SasviewModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'description_truncated', 'category', 'upload_date')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = { "slug": ("name",) }
