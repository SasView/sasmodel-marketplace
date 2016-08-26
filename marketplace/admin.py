from django.contrib import admin
from models import SasviewModel
from attachments.admin import AttachmentInlines

class SasviewModelAdmin(admin.ModelAdmin):
    inlines = (AttachmentInlines,)

admin.site.register(SasviewModel, SasviewModelAdmin)
