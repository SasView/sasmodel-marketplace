# DatabaseStorage for django.
# 2009 (c) GameKeeper Gambling Ltd, Ivanov E.
import StringIO
import urlparse
import time
import os
from django.utils.deconstruct import deconstructible
from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured
import psycopg2

@deconstructible
class DatabaseStorage(Storage):
    """
    Class DatabaseStorage provides storing files in the database.
    """

    def __init__(self, option=settings.DB_FILES):

        self.db_table = option['db_table']
        self.fname_column = option['fname_column']
        self.blob_column = option['blob_column']
        self.size_column = option['size_column']
        self.base_url = option['base_url']

        #get database settings
        self.DATABASE_NAME = settings.DATABASES['default']['NAME']
        self.DATABASE_USER = settings.DATABASES['default']['USER']

    def _open(self, name, mode='rb'):
        """Open a file from database.

        @param name filename or relative path to file based on base_url. path should contain only "/", but not "\". Apache sends pathes with "/".
        If there is no such file in the db, returs None
        """
        assert mode == 'rb', "You've tried to open binary file without specifying binary mode! You specified: %s"%mode

        connection = psycopg2.connect("dbname={} user={}".format(self.DATABASE_NAME, self.DATABASE_USER))
        cursor = connection.cursor()

        cursor.execute("SELECT {} FROM {} WHERE {} = '{}'".format(self.blob_column,self.db_table,self.fname_column,name))
        row = cursor.fetchone()
        if row is None:
            return None
        inMemFile = StringIO.StringIO(row[0])
        inMemFile.name = name
        inMemFile.mode = mode

        retFile = File(inMemFile)

        cursor.close()
        connection.close()

        return retFile

    def _save(self, name, content):
        """Save 'content' as file named 'name'.

        @note '\' in path will be converted to '/'.
        """
        name = name.replace('\\', '/')
        binary = psycopg2.Binary(content.read())
        size = binary.__sizeof__()

        connection = psycopg2.connect("dbname={} user={}".format(self.DATABASE_NAME, self.DATABASE_USER))
        cursor = connection.cursor()

        #todo: check result and do something (exception?) if failed.
        if self.exists(name, cursor=cursor):
            cursor.execute("UPDATE {} SET {} = %s, {} = %s WHERE {} = '{}'".format(self.db_table,self.blob_column,self.size_column,self.fname_column,name),
                                 (binary, size)  )
        else:
            cursor.execute("INSERT INTO {} VALUES(%s, %s, %s)".format(self.db_table), (name, binary, size))
        connection.commit()

        cursor.close()
        connection.close()

        return name

    def exists(self, name, cursor=None):
        cursor_supplied = (cursor is not None)
        if not cursor_supplied:
            connection = psycopg2.connect("dbname={} user={}".format(self.DATABASE_NAME, self.DATABASE_USER))
            cursor = connection.cursor()

        cursor.execute("SELECT {} FROM {} WHERE {} = '{}'".format(self.fname_column,self.db_table,self.fname_column,name))
        row = cursor.fetchone()

        if not cursor_supplied:
            cursor.close()
            connection.close()

        return row is not None

    def get_available_name(self, name, max_length=100):
        fname, ext = os.path.splitext(name)
        fname = fname[:(max_length-len(ext))]
        name = fname + ext
        does_exist = self.exists(name)
        if not does_exist:
            return name
        elif does_exist:
            fname = fname + str(int(time.time()*1000))
            fname = fname[:(max_length-len(ext))]
            name = fname + ext

        return name

    def delete(self, name):
        connection = psycopg2.connect("dbname={} user={}".format(self.DATABASE_NAME, self.DATABASE_USER))
        cursor = connection.cursor()
        if self.exists(name, cursor):
            cursor.execute("DELETE FROM {} WHERE {} = '{}'".format(self.db_table,self.fname_column,name))
            connection.commit()
        cursor.close()
        connection.close()

    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        return urlparse.urljoin(self.base_url, name).replace('\\', '/')

    def size(self, name):
        connection = psycopg2.connect("dbname={} user={}".format(self.DATABASE_NAME, self.DATABASE_USER))
        cursor = connection.cursor()

        cursor.execute("SELECT {} from {} where {} = '{}'".format(self.size_column,self.db_table,self.fname_column,name))
        row = cursor.fetchone()

        cursor.close()
        connection.close()

        if row is None:
            return 0
        else:
            return int(row[0])
