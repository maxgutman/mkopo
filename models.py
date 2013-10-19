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
    Column('loan_amount', String(), default='0.0'),
    Column('repaid_amount', String(), default='0.0'),
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

    def get_user_group(self, group):
        return db.query(UserGroup).filter(UserGroup.user==self, UserGroup.group==group)

    def get_invite_groups(self):
        return db.query(InviteGroup).filter()

    @property
    def photo_url(self):
        return 'https://graph.facebook.com/%s/picture' % self.facebook_id



class Group(CRUDMixin, Base):
    __tablename__ = 'group'

    name = Column(String(255))
    users = relation('User', primaryjoin='Group.id==UserGroup.group_id', secondary=UserGroup.__table__, secondaryjoin='UserGroup.user_id==User.id')

    def __repr__(self):
        return u'<Group %r>' % self.name

    @classmethod
    def get_all(cls, **kwargs):
        return db.query(cls).filter()


class InviteGroup(CRUDMixin, Base):
    __tablename__ = 'invite_group'

    to_user = Column(Integer, ForeignKey('user.id'))
    from_user = Column(Integer, ForeignKey('user.id'))
    group = Column(Integer, ForeignKey('group.id'))
    subject = Column(String(255))
    message = Column(String(1255))
    remaining = Column(String(255))


    @property
    def _to_user(self):
        return db.query(User).get(self.to_user)

    @property
    def _from_user(self):
        return db.query(User).get(self.from_user)

    @property
    def _group(self):
        return db.query(Group).get(self.group)


    def __repr__(self):
        return u'<to_user %r>' % self.to_user


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
user0 = User.get_or_create(name='Max Gutman', email='jiggy361@gmail.com', facebook_id='6706834')
user1 = User.get_or_create(name='Renu Bora', email='renubora@gmail.com', facebook_id='764632058')
user2 = User.get_or_create(name='Tom Quast', email='tomquast89@gmail.com', facebook_id='100000179176787')
user3 = User.get_or_create(name='Arezu Aghasey', email='arezu@berkeley.edu', facebook_id='676966868')
user4 = User.get_or_create(name='Jenny Lo', email='jlo@ischool.berkeley.edu', facebook_id='4205393')
user5 = User.get_or_create(name='Pablo Arvizu', email='parvizu@ischool.berkeley.edu', facebook_id='511898967')

group1 = Group.get_or_create(name='Group Loan #1')
group2 = Group.get_or_create(name='Group Loan #2',)
group3 = Group.get_or_create(name='Group Loan #3',)

UserGroup.get_or_create(user_id=user0.id, group_id=group1.id, loan_amount='100.00', repaid_amount='100.00')
UserGroup.get_or_create(user_id=user1.id, group_id=group1.id, loan_amount='100.00', repaid_amount='100.00')
UserGroup.get_or_create(user_id=user2.id, group_id=group1.id, loan_amount='250.00', repaid_amount='0.00')
UserGroup.get_or_create(user_id=user3.id, group_id=group1.id, loan_amount='650.00', repaid_amount='650.00')

UserGroup.get_or_create(user_id=user0.id, group_id=group2.id, loan_amount='50.00', repaid_amount='0.00')
UserGroup.get_or_create(user_id=user4.id, group_id=group2.id, loan_amount='975.00', repaid_amount='500.00')
UserGroup.get_or_create(user_id=user5.id, group_id=group2.id, loan_amount='525.00', repaid_amount='525.00')


InviteGroup.get_or_create(to_user=user0.id, from_user=user1.id, group=group1.id, remaining="500.00", subject="A new bike", message="Hi Max Gutman, what's up? I really need some money to fix my bike so I can get to work tomorrow. I heard you also need some cash, so I thought we can help each other? See you soon.")
InviteGroup.get_or_create(to_user=user0.id, from_user=user2.id, group=group2.id, remaining="400.00", subject="Fix roof", message="Hi Max Gutman, I need your help! The roof of my house needs to get repaired, but I don't have neough money right now. Please help me to get a loan so I dont have to sit in a wet room.")
InviteGroup.get_or_create(to_user=user0.id, from_user=user3.id, group=group3.id, remaining="100.00", subject="Money for birthday", message="Yo Max Gutman, I want to throw a birthday-party, but cant afford the cake. Let's borrow some money together. You can spent it on a present for me ;)")


