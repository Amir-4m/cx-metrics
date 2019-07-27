# Generated by Django 2.2 on 2019-07-27 11:36

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('multiple_choices', '0001_initial'),
        ('surveys', '0001_initial'),
        ('businesses', '0003_auto_20190710_0553'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CSATResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('survey_uuid', models.UUIDField(editable=False, verbose_name='Survey UUID')),
                ('customer_uuid', models.UUIDField(editable=False, verbose_name='Customer UUID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('rate', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)])),
            ],
            options={
                'verbose_name': 'CSAT Response',
                'verbose_name_plural': 'CSAT Responses',
            },
        ),
        migrations.CreateModel(
            name='CSATSurvey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')),
                ('name', models.CharField(max_length=256, verbose_name='Name')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('text', models.TextField(max_length=1000, verbose_name='Intro Text')),
                ('text_enabled', models.BooleanField(default=True, verbose_name='Is Intro Enabled')),
                ('question', models.TextField(max_length=256, verbose_name='Question')),
                ('message', models.TextField(max_length=256, verbose_name='Thank You Message')),
                ('scale', models.CharField(choices=[('3', '3 Choices'), ('5', '5 Choices'), ('7', '7 Choices')], default='3', max_length=1, verbose_name='Scale')),
                ('author', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='csatsurveys', related_query_name='csatsurveys', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='csatsurveys', related_query_name='csatsurveys', to='businesses.Business', verbose_name='Business')),
                ('contra', models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='csat_survey', to='multiple_choices.MultipleChoice', verbose_name='Contra')),
                ('survey', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='csatsurvey', related_query_name='csatsurvey', to='surveys.Survey', verbose_name='Survey')),
            ],
            options={
                'verbose_name': 'CSAT Survey',
                'verbose_name_plural': 'CSAT Surveys',
            },
        ),
    ]
