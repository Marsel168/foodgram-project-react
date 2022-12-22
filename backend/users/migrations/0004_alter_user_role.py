# Generated by Django 4.1.4 on 2022-12-19 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('moderator', 'Модератор'), ('admin', 'Админ'), ('user', 'Пользователь')], default='user', max_length=20, verbose_name='статус'),
        ),
    ]