# -*- coding: utf-8 -*-
# Create table for storing uploaded files
from django.db import migrations, models
import marketplace.backends.database


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_sasviewmodel_model_file'),
    ]
    operations = [
        migrations.RunSQL([("CREATE TABLE \"marketplace_uploaded_files\" "
            "(\"file_name\" varchar(100) NOT NULL PRIMARY KEY, "
            "\"blob\" bytea NOT NULL, "
            "\"size\" bigint NOT NULL);")],
            ["DROP TABLE \"marketplace_uploaded_files\""])
    ]
