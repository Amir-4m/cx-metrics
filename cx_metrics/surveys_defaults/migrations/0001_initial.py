# Generated by Django 2.2 on 2019-07-28 11:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('industries', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('survey_type', models.CharField(choices=[('nps', 'NPS'), ('csat', 'CSAT'), ('ces', 'CES')], max_length=20, verbose_name='Survey Type')),
                ('question_type', models.CharField(choices=[('contra', 'Contra')], max_length=20, verbose_name='Question Type')),
                ('text', models.CharField(max_length=256, verbose_name='Text')),
                ('order', models.PositiveSmallIntegerField(db_index=True, default=0, verbose_name='Order')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('industry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='default_options', to='industries.Industry', verbose_name='Industry')),
            ],
            options={
                'verbose_name': 'Default Option',
                'verbose_name_plural': 'Default Options',
                'unique_together': {('survey_type', 'question_type', 'order')},
            },
        ),
    ]
