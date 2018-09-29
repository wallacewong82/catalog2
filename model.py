# This file is meant for modelling the 4 sets of data used in this project.
# Dataset 1: Catalog. For this project we only allow 1 instance of Catalog,
# which houses a set of Categories which in turn house a set of Items within.
# Think of Catalog like a cluster of restaurants within a shopping mall.
# Dataset 2: Category. Subset of Catalog, superset to Item. Think of it
# like a specific restaurant within that shopping mall.
# Dataset 3: Item. Subset of Category. This is like a specific menu within
# the specific restaurant within a specific shopping mall.
# Dataset 4: User. The users whom use the above 3 datasets. Think of these
# as owners of the restaurants who in turn own the menus within them.

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, UniqueConstraint
from datetime import datetime

Base = declarative_base()


# User dataset.
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    picture = Column(String(250))

    # user for json decorator
    @property
    def serialize(self):
        return{
            'user_name': self.name,
            'user_email': self.email,
            'user_picture': self.picture,
            'user_id': self.id
        }


# Catalog dataset.
class Catalog(Base):
    __tablename__ = 'catalog'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    description = Column(String)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description
        }


# Category dataset. Akin to subcatalog.
class Subcatalog(Base):
    __tablename__ = 'subcatalog'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    description = Column(String)
    datetime_added = Column(DateTime, default=datetime.utcnow)
    catalog_id = Column(Integer, ForeignKey('catalog.id'))
    catalog = relationship(Catalog)
    user_name = Column(String(250), nullable=False)
    user_email = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # category for json decorator
    @property
    def serialize(self):
        return{
            'category_name': self.name,
            'category_description': self.description,
            'datetime_added': self.datetime_added,
            'category_id': self.id,
            'parent_catalog_id': self.catalog_id,
            'owner_name': self.user_name,
            'owner_email': self.user_email,
            'owner_id': self.user_id
        }


# Item dataset.
class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    datetime_added = Column(DateTime, default=datetime.utcnow)
    parent_catalog = Column(String(80), nullable=False)
    subcatalog_id = Column(Integer, ForeignKey('subcatalog.id'))
    subcatalog = relationship(Subcatalog)
    user_name = Column(String(250), nullable=False)
    user_email = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # item for json decorator
    @property
    def serialize(self):
        return{
            'item_name': self.name,
            'item_description': self.description,
            'datetime_added': self.datetime_added,
            'item_id': self.id,
            'parent_category': self.parent_catalog,
            'parent_id': self.subcatalog_id,
            'owner_name': self.user_name,
            'owner_email': self.user_email,
            'owner_id': self.user_id
        }


# Database engine initialization.
engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
