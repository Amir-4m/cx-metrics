# Generated by Django 2.2 on 2019-04-27 07:49

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('businesses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')),
                ('name', models.CharField(max_length=256, verbose_name='Name')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('type', models.CharField(max_length=50, verbose_name='Type')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='surveys', related_query_name='surveys', to='businesses.Business', verbose_name='Business')),
            ],
            options={
                'verbose_name_plural': 'Surveys',
                'verbose_name': 'Survey',
                'abstract': False,
            },
        ),
    ]
