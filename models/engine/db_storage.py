#!/usr/bin/python3
"""DBStorage class"""

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from os import getenv
from models.base_model import Base
from models.amenity import Amenity
from models.state import State
from models.city import City
from models.place import Place
from models.review import Review
from models.user import User
from models import storage_type


classes = {
    'Amenity': Amenity,
    'City': City,
    'Place': Place,
    'State': State,
    'Review': Review,
    'User': User
}


class DBStorage:
    """Database storage class"""

    __engine = None
    __session = None

    def __init__(self):
        HBNB_MYSQL_USER = getenv('HBNB_MYSQL_USER')
        HBNB_MYSQL_PWD = getenv('HBNB_MYSQL_PWD')
        HBNB_MYSQL_HOST = getenv('HBNB_MYSQL_HOST')
        HBNB_MYSQL_DB = getenv('HBNB_MYSQL_DB')
        HBNB_ENV = getenv('HBNB_ENV')

        self.__engine = create_engine(
            'mysql+mysqldb://{}:{}@{}/{}'.format(
                                           HBNB_MYSQL_USER,
                                           HBNB_MYSQL_PWD,
                                           HBNB_MYSQL_HOST,
                                           HBNB_MYSQL_DB
                                       ), pool_pre_ping=True)

        if HBNB_ENV == 'test':
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """
        queries on the current database session (self.__session) all
        objects depending of the class name (argument cls)
        if cls=None, query all types of objects
        (User, State, City, Amenity, Place and Review)
        this method must return a dictionary
        """

        _dict = {}

        if cls:
            objects = self.__session.query(cls).all()
            for obj in objects:
                key = obj.__class__.__name__ + '.' + obj.id
                _dict[key] = obj

        else:
            for item in classes.values():
                objects = self.__session.query(item).all()
                for obj in objects:
                    key = obj.__class__.__name__ + '.' + obj.id
                    _dict[key] = obj

        return _dict

    def new(self, obj):
        """adds the object to the current database session"""
        self.__session.add(obj)

    def save(self):
        """commits all changes of the current database session"""
        self.__session.commit()

    def delete(self, obj=None):
        """deletes from the current database session"""
        if obj:
            self.session.delete(obj)

    def reload(self):
        """
        creates all tables in the database
        creates the current database session
        """
        Base.metadata.create_all(self.__engine)
        new = sessionmaker(bind=self.__engine, expire_on_commit=False)
        self.__session = scoped_session(new)()

    def close(self):
        """closes the working SQLAlchemy session"""
        self.__session.close()
