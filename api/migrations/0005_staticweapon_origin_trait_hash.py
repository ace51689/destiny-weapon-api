# Generated by Django 3.2.7 on 2022-03-07 16:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20220303_1940'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticweapon',
            name='origin_trait_hash',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='origin_trait', to='api.plugset'),
        ),
    ]
