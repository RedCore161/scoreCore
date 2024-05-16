from django.contrib import admin
from scoring.models import Project, ImageScore, Backup, ImageFile, ScoreFeature

admin.site.register(Project)
admin.site.register(ScoreFeature)
admin.site.register(ImageScore)
admin.site.register(ImageFile)
admin.site.register(Backup)
