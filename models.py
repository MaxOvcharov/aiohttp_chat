# import sqlalchemy as sa
import uuid


from sqlalchemy import MetaData
from sqlalchemy import ForeignKey
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID

metadata = MetaData()


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('login', String(255)),
              Column('password', Text),
              Column('user_id', GUID(), default=uuid.uuid4, nullable=False, unique=True),
              )

unknown_users = Table('unknown_users', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('session_id', GUID(), default=uuid.uuid4, nullable=False, unique=True),)

# unknown_users = Table('unknown_users', metadata,
#                       Column('id', Integer, primary_key=True),
#                       Column('user_id', None, ForeignKey('users.id')),
#                       Column('email', String(255), nullable=False),
#                       Column('private', Boolean, nullable=False))


