from django.contrib import admin
from scoring.models import Project, ImageScore, Backup, ImageFile

admin.site.register(Project)
admin.site.register(ImageScore)
admin.site.register(ImageFile)
admin.site.register(Backup)
