import datetime

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    relation,
    backref,
    mapper,
    sessionmaker,
    scoped_session,
)

engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
db = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db.query_property()

class CRUDMixin(object):
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, id):
        if any(
            (isinstance(id, basestring) and id.isdigit(),
             isinstance(id, (int, float))),
        ):
            return cls.query.get(int(id))
        return None

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = db.query(cls).filter_by(**kwargs).first()
        if not instance:
            instance = cls(**kwargs)
            instance.save()
        return instance

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.add(self)
        if commit:
            db.commit()
        return self

    def delete(self, commit=True):
        db.delete(self)
        return commit and db.commit()


user_group = Table('user_group', Base.metadata,
    Column('id', Integer(), primary_key=True, nullable=False),
    Column('user_id', Integer(), ForeignKey('user.id'), nullable=False),
    Column('group_id', Integer(), ForeignKey('group.id'), nullable=False),
    Column('created', DateTime(), default=datetime.datetime.now),
)


class UserGroup(CRUDMixin, Base):
    __tablename__ = 'user_group'
    __table__ = user_group

    group = relation('Group', primaryjoin='UserGroup.group_id==Group.id')
    user = relation('User', primaryjoin='UserGroup.user_id==User.id')


class User(CRUDMixin, Base):
    __tablename__ = 'user'

    email = Column(String(255), unique=True)
    name = Column(String(255))
    employer = Column(String(255))
    position = Column(String(255))
    location = Column(String(255))
    bio = Column(String(1255))
    facebook_id = Column(BigInteger(20, unsigned=True))
    groups = relation('Group', primaryjoin='User.id==UserGroup.user_id', secondary=UserGroup.__table__, secondaryjoin='UserGroup.group_id==Group.id')

    def __init__(self, email, name=None, loan_amount=None, facebook_id=None):
        self.email = email
        self.name = name
        self.loan_amount = loan_amount
        self.facebook_id = facebook_id

    def __repr__(self):
        return u'<User %r>' % self.email

    @classmethod
    def get_or_create(cls, **kwargs):
        instance = db.query(cls).filter_by(email=kwargs.get('email')).first()
        if not instance:
            instance = User.create(**kwargs)
        return instance

    @classmethod
    def get_all(cls, **kwargs):
        return db.query(cls).filter(User.id != kwargs.get('exclude_user_id'))


class Group(CRUDMixin, Base):
    __tablename__ = 'group'

    name = Column(String(255))
    domain = Column(String(255))

    users = relation('User', primaryjoin='Group.id==UserGroup.group_id', secondary=UserGroup.__table__, secondaryjoin='UserGroup.user_id==User.id')

    def __repr__(self):
        return u'<Group %r>' % self.name


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
user1 = User.get_or_create(name='Renu Bora', email='renubora@gmail.com', facebook_id='764632058')
user2 = User.get_or_create(name='Tom Quast', email='tomquast89@gmail.com', facebook_id='100000179176787')
user3 = User.get_or_create(name='Arezu Aghasey', email='arezu@berkeley.edu', facebook_id='676966868')
user4 = User.get_or_create(name='Jenny Lo', email='jlo@ischool.berkeley.edu', facebook_id='4205393')

