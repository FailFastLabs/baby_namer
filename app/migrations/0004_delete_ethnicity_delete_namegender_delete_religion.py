# Generated by Django 4.2.3 on 2023-07-16 20:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_rename_related_name_famousperson_first_name'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Ethnicity',
        ),
        migrations.DeleteModel(
            name='NameGender',
        ),
        migrations.DeleteModel(
            name='Religion',
        ),
    ]