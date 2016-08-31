from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0003_auto_20160826_1029'),
    ]

    operations = [
        migrations.CreateModel(
            name='uploaded_files',
            fields=[
                ('file_name', models.FilePathField(primary_key=True)),
                ('blob', models.BinaryField()),
                ('size', models.BigIntegerField()),
            ],
        ),
    ]
