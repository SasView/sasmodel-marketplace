# -*- coding: utf-8 -*-
# Create table for storing uploaded files
from django.db import migrations, models
import marketplace.backends.database


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_sasviewmodel_model_file'),
    ]
    operations = [
        migrations.RunSQL([("CREATE TABLE marketplace_uploaded_files "
            "(file_name VARCHAR(100) NOT NULL PRIMARY KEY, "
            "blob_name BLOB NOT NULL, "
            "size BIGINT NOT NULL);")],
            ["DROP TABLE \"marketplace_uploaded_files\""])
    ]
