from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('social.db')


class BaseModel(Model):
    """A base model that will use our Sqlite database."""
    class Meta:
        database = DATABASE


class User(UserMixin, BaseModel):
    """User model with email and password"""
    email = CharField(unique=True)
    password = CharField(max_length=100)

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, email, password):
        try:
            User.select().where(
                User.email ** email
            ).get()
        except DoesNotExist:
            cls.create(
                email=email,
                password=generate_password_hash(password)
            )
        else:
            raise ValueError


class Journal(BaseModel):
    """Journal model"""
    title = CharField(unique=True)
    date = DateField()
    time_spent = IntegerField()
    learned_info = TextField()
    resources = TextField()
    slug = CharField(unique=True)
    tags = TextField(null=True)

    def tag_list(self):
        return [x.strip() for x in self.tags.lower().split(',')]


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Journal], safe=True)
    DATABASE.close()
