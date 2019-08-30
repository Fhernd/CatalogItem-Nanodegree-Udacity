#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///itemcatalog.db')
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

# User:
user = User(name='John Ortiz O.',
            email='johnortizo@outlook.com',
            picture='photo.png')

# Category for soccer
soccer = Category(name="Soccer", user=user)

session.add(soccer)
session.commit()

item = Item(title="New item 1", description="new description",
            category=soccer, user=user)

session.add(item)
session.commit()

item = Item(title="New item 2", description="new description",
            category=soccer, user=user)

session.add(item)
session.commit()

item = Item(title="New item 3", description="new description",
            category=soccer, user=user)

session.add(item)
session.commit()


# Category for Basketball
basketball = Category(name="Basketball", user=user)

session.add(soccer)
session.commit()

item = Item(title="New item 1", description="new description",
            category=basketball, user=user)

session.add(item)
session.commit()

item = Item(title="New item 2", description="new description",
            category=basketball, user=user)

session.add(item)
session.commit()

item = Item(title="New item 3", description="new description",
            category=basketball, user=user)

session.add(item)
session.commit()


# Category for Baseball
baseball = Category(name="Baseball", user=user)

session.add(soccer)
session.commit()

item = Item(title="New item 1", description="new description",
            category=baseball, user=user)

session.add(item)
session.commit()


item = Item(title="New item 2", description="new description",
            category=baseball, user=user)

session.add(item)
session.commit()

item = Item(title="New item 3", description="new description",
            category=baseball, user=user)

session.add(item)
session.commit()


print("Added categories adn items!")
