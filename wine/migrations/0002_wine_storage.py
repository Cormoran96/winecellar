# Generated by Django 3.2.6 on 2021-09-06 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wine', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='wine',
            name='storage',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
