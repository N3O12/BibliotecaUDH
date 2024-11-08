# Generated by Django 5.0.1 on 2024-10-28 02:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_libro_generos_delete_librogenero'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='generos_favoritos',
        ),
        migrations.AlterField(
            model_name='favorito',
            name='libro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoritos', to='api.libro'),
        ),
        migrations.AlterField(
            model_name='favorito',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoritos', to=settings.AUTH_USER_MODEL),
        ),
    ]
