# Generated by Django 4.2.3 on 2023-07-22 18:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_favorite'),
    ]

    operations = [
        migrations.CreateModel(
            name='BabyTags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
                ('baby_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.babyname')),
            ],
            options={
                'unique_together': {('baby_name', 'key', 'value')},
            },
        ),
    ]