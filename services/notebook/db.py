from peewee import *

db = SqliteDatabase('static/db.sqlite')
db.connect()


class Note(Model):
    name = CharField()
    key = CharField()

    class Meta:
        database = db


db.create_tables([Note])


def add_note(note, key):
    Note.create(name=note, key=key)


def get_key(note):
    try:
        r = Note.select().where(Note.name == note)[0].key
        return r
    except:
        return None