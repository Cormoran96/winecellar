# Generated by Django 3.0.2 on 2020-05-12 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wine', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wine',
            name='purchase',
            field=models.DateField(blank=True, default=0),
        ),
    ]
