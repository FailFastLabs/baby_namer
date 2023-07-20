# Generated by Django 4.2.3 on 2023-07-16 15:34

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='famousperson',
            name='id',
        ),
        migrations.AddField(
            model_name='famousperson',
            name='related_name',
            field=models.ForeignKey(default='John', on_delete=django.db.models.deletion.CASCADE, to='app.babyname'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='famousperson',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='famousperson',
            name='wikipedia_link',
            field=models.URLField(primary_key=True, serialize=False, validators=[django.core.validators.URLValidator()]),
        ),
        migrations.DeleteModel(
            name='BabyNameRef',
        ),
    ]