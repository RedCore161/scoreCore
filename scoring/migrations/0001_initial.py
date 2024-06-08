# Generated by Django 5.0.6 on 2024-06-08 12:58

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Backup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ImageFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=50)),
                ('path', models.CharField(max_length=500)),
                ('useless', models.BooleanField(default=False)),
                ('hidden', models.BooleanField(default=False)),
                ('varianz', models.FloatField(blank=True, default=0, null=True)),
                ('data', models.JSONField(blank=True, default=dict)),
                ('width', models.IntegerField(blank=True, default=0)),
                ('height', models.IntegerField(blank=True, default=0)),
                ('frame_x', models.IntegerField(blank=True, default=0)),
                ('frame_y', models.IntegerField(blank=True, default=0)),
                ('frame_w', models.IntegerField(blank=True, default=0)),
                ('frame_h', models.IntegerField(blank=True, default=0)),
                ('date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('icon', models.CharField(blank=True, default='', max_length=5, null=True)),
                ('image_dir', models.CharField(blank=True, max_length=500, null=True, validators=[django.core.validators.RegexValidator('^(?!setup$|backup$|evaluations$).*$')])),
                ('wanted_scores_per_user', models.IntegerField(blank=True, default=100, null=True)),
                ('wanted_scores_per_image', models.IntegerField(blank=True, default=2, null=True)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ImageScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_created=True, blank=True, null=True)),
                ('comment', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('data', models.JSONField(blank=True, default=dict)),
                ('is_completed', models.BooleanField(default=False)),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='scoring.imagefile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='scoring.project')),
            ],
        ),
        migrations.AddField(
            model_name='imagefile',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='scoring.project'),
        ),
        migrations.CreateModel(
            name='ScoreFeature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('bit', models.IntegerField(blank=True, default=0)),
                ('option_count', models.IntegerField(blank=True, default=3)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='features', to='scoring.project')),
            ],
        ),
    ]
