# This file is meant to help create a repository of data in order to
# have some data in the database; rather than start from scratch.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

from model import Catalog, Item, Base, Subcatalog, User

engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False}, echo=True)

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# There will be a total of 2 users created; but 3 Categories added.
# In the 3 Categories, 4 Items each will be added to these Categories.

# Replace with your own user name and email for this first user.
User1 = User(name="W Wong", email="wallacewong82@gmail.com",
             picture='')
session.add(User1)
session.commit()

# Replace with your own user name and email for this second user.
User2 = User(name="WebMagicSG", email="webmagicsg@gmail.com",
             picture='')
session.add(User2)
session.commit()


catalog1 = Catalog(name="Categories",
                   description="ball games, racket games, table games")
session.add(catalog1)
session.commit()

# Gear for Soccer
subcatalog1 = Subcatalog(name="Soccer", description="Association football,"\
                         " more commonly known as football or soccer, is a"\
                         "team sport played between two teams of eleven players"\
                         "with a spherical ball. It is played by 250 million"\
                         "players in over 200 countries and dependencies,"\
                         " making it the world's most popular sport. The game"\
                         " is played on a rectangular field with a goal at"\
                         " each end. The object of the game is to score by"\
                         " moving the ball beyond the goal line into the "\
                         "opposing goal.",
                         catalog=catalog1, user_name=User1.name,
                         user_id=User1.id,
                         user_email=User1.email)
session.add(subcatalog1)
session.commit()

subcatalogItem1 = Item(name="Boots", description="A pair of boots",
                       subcatalog=subcatalog1, parent_catalog=subcatalog1.name,
                       user_name=User1.name, user_email=User1.email,
                       user_id=User1.id,
                       datetime_added=datetime.datetime(2018, 3, 7, 0, 6))
session.add(subcatalogItem1)
session.commit()

subcatalogItem2 = Item(name="Jersey", description="A dryfit shirt",
                       subcatalog=subcatalog1, parent_catalog=subcatalog1.name,
                       user_name=User1.name, user_email=User1.email,
                       user_id=User1.id,
                       datetime_added=datetime.datetime(2018, 3, 7, 0, 8))
session.add(subcatalogItem2)
session.commit()

subcatalogItem3 = Item(name="Shorts", description="A pair of shorts",
                       subcatalog=subcatalog1, parent_catalog=subcatalog1.name,
                       user_name=User1.name, user_email=User1.email,
                       user_id=User1.id,
                       datetime_added=datetime.datetime(2018, 3, 7, 0, 3))
session.add(subcatalogItem3)
session.commit()

subcatalogItem4 = Item(name="Socks", description="A pair of knee socks",
                       subcatalog=subcatalog1, parent_catalog=subcatalog1.name,
                       user_name=User1.name, user_email=User1.email,
                       user_id=User1.id,
                       datetime_added=datetime.datetime(2018, 3, 7, 0, 1))
session.add(subcatalogItem4)
session.commit()


# Gear for basketball
subcatalog2 = Subcatalog(name="Basketball", description="Basketball is a team"\
                         "sport in which ten players, five on a side, opposing"\
                         " one another on a rectangular court, have in play"\
                         " the primary objective to shoot a basketball "\
                         " through the defender's hoop while preventing the"\
                         " opposing team from shooting through their own hoop.",
                         catalog=catalog1, user_name=User2.name,
                         user_id=User2.id,
                         user_email=User2.email)
session.add(subcatalog2)
session.commit()

subcatalogItem1 = Item(name="Sneakers", description="A pair of sneakers",
                       subcatalog=subcatalog2, parent_catalog=subcatalog2.name,
                       user_email=User2.email, user_name=User2.name,
                       user_id=User2.id,
                       datetime_added=datetime.datetime(2018, 3, 7, 0, 1))
session.add(subcatalogItem1)
session.commit()

subcatalogItem2 = Item(name="Jersey", description="A dryfit singlet",
                       subcatalog=subcatalog2, parent_catalog=subcatalog2.name,
                       user_email=User2.email, user_name=User2.name,
                       user_id=User2.id,
                       datetime_added=datetime.datetime(2018, 3, 7, 0, 6))
session.add(subcatalogItem2)
session.commit()

subcatalogItem3 = Item(name="Bermudas", description="A pair of bermuda shorts",
                       subcatalog=subcatalog2, parent_catalog=subcatalog2.name,
                       user_email=User2.email, user_name=User2.name,
                       user_id=User2.id,
                       datetime_added=datetime.datetime(2018, 3, 7, 0, 3))
session.add(subcatalogItem3)
session.commit()

subcatalogItem4 = Item(name="Socks", description="A pair of socks",
                       subcatalog=subcatalog2, parent_catalog=subcatalog2.name,
                       user_email=User2.email, user_name=User2.name,
                       user_id=User2.id,
                       datetime_added=datetime.datetime(2018, 3, 7, 0, 7))
session.add(subcatalogItem4)
session.commit()


# Gear for rugby
subcatalog3 = Subcatalog(name="Rugby", description="Rugby league football is a"\
                         "full-contact sport played by two teams of thirteen"\
                         " players on a rectangular field. In rugby league,"\
                         " points are scored by carrying the ball and touching"\
                         " it to the ground beyond the opposing team's goal"\
                         " line; this is called a try, and is the primary"\
                         " method of scoring. The opposing team attempts to"\
                         " stop the attacking side scoring points by tackling"\
                         " the player carrying the ball. In addition to tries,"\
                         " points can be scored by kicking goals. After each"\
                         " try, the scoring team gains a free kick to try at"\
                         " goal with a conversion for further points. Kicks "\
                         "at goal may also be awarded for penalties, and "\
                         "field goals can be attempted at any time.",
                         catalog=catalog1, user_name=User1.name,
                         user_id=User1.id,
                         user_email=User1.email)
session.add(subcatalog3)
session.commit()

subcatalogItem1 = Item(name="Boots", description="A pair of boots",
                       subcatalog=subcatalog3, parent_catalog=subcatalog3.name,
                       user_name=User1.name, user_email=User1.email,
                       user_id=User1.id,
                       datetime_added=datetime.datetime(2018, 3, 7, 0, 2))
session.add(subcatalogItem1)
session.commit()

subcatalogItem2 = Item(name="Jersey", description="A dryfit singlet",
                       subcatalog=subcatalog3, parent_catalog=subcatalog3.name,
                       user_name=User1.name, user_email=User1.email,
                       user_id=User1.id,
                       datetime_added=datetime.datetime(2018, 3, 7, 0, 4))
session.add(subcatalogItem2)
session.commit()

subcatalogItem3 = Item(name="Bermudas", description="A pair of bermuda shorts",
                       subcatalog=subcatalog3, parent_catalog=subcatalog3.name,
                       user_name=User1.name, user_email=User1.email,
                       user_id=User1.id,
                       datetime_added=datetime.datetime(2018, 3, 7, 0, 8))
session.add(subcatalogItem3)
session.commit()

subcatalogItem4 = Item(name="Socks", description="A pair of socks",
                       subcatalog=subcatalog3, parent_catalog=subcatalog3.name,
                       user_name=User1.name, user_email=User1.email,
                       user_id=User1.id,
                       datetime_added=datetime.datetime(2018, 3, 7, 0, 5))
session.add(subcatalogItem4)
session.commit()

print "added menu items!"
