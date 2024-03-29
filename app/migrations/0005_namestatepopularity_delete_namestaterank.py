# Generated by Django 4.2.3 on 2023-07-18 20:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_delete_ethnicity_delete_namegender_delete_religion'),
    ]

    operations = [
        migrations.CreateModel(
            name='NameStatePopularity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=15)),
                ('relative_popularity', models.FloatField()),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.babyname')),
            ],
            options={
                'unique_together': {('name', 'state')},
            },
        ),
        migrations.DeleteModel(
            name='NameStateRank',
        ),
    ]
