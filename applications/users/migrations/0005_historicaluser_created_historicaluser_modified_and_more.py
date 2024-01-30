# Generated by Django 4.2.2 on 2024-01-26 02:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_historicaluser_is_active_alter_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaluser',
            name='created',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicaluser',
            name='modified',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]