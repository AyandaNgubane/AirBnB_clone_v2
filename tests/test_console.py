#!/usr/bin/python3
"""A unit test module for the console (command interpreter).
"""
import json
import os
import MySQLdb
import unittest
from io import StringIO
from unittest.mock import patch

from console import HBNBCommand
from models import storage
from models.base_model import BaseModel


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') != 'db',
                 'file_storage test not supported here')
class TestDBStorageWithConsole(unittest.TestCase):
    """
    Test dbstorage engine with console
    """
    def query(self, string):
        """Sending database query"""
        db = MySQLdb.connect(
            user=os.getenv('HBNB_MYSQL_USER'),
            host=os.getenv('HBNB_MYSQL_HOST'),
            passwd=os.getenv('HBNB_MYSQL_PWD'),
            port=3306,
            db=os.getenv('HBNB_MYSQL_DB')
        )
        cur = db.cursor()
        cur.execute(string)
        count = cur.fetchall()
        cur.close()
        db.close()
        return count

    def test_create_state(self):
        """Test create State"""
        string = "SELECT * FROM states"
        old_count = self.query(string)
        cmd = 'create State name="California"'
        self.getOutput(cmd)
        new_count = self.query(string)
        self.assertEqual(len(new_count) - len(old_count), 1)

    def getOutput(self, command):
        """Get output from stdout"""
        with patch('sys.stdout', new=StringIO()) as out:
            cmd = HBNBCommand()
            cmd.onecmd(command)
            return out.getvalue().strip()

    def test_create_place_with_integer_and_float(self):
        """Test create City"""
        string = "SELECT * FROM places"
        # old_count = self.query(string)
        cmd = 'create State name="California"'
        state_id = self.getOutput(cmd)
        name = "San_Francisco_is_super_cool"
        cmd = f'create City state_id="{state_id}" name="{name}"'
        city_id = self.getOutput(cmd)
        cmd = f'create User email="my@me.com"\
            password="pwd" first_name="FN" last_name="LN"'
        user_id = self.getOutput(cmd)
        cmd = f'create Place city_id="{city_id}" user_id="{user_id}"\
            name="My_house" description="no_description_yet" number_rooms=4\
            number_bathrooms=1 max_guest=3 price_by_night=100 latitude=120.12\
            longitude=101.4'
        place_id = self.getOutput(cmd)
        new_count = self.query(string)
        self.assertIn(place_id, str(new_count))
        self.assertIn('100', str(new_count))
        self.assertIn('120.12', str(new_count))

    def test_create_city_with_underscore(self):
        """Test create City"""
        string = "SELECT * FROM cities"
        old_count = self.query(string)
        cmd = 'create State name="California"'
        state_id = self.getOutput(cmd)
        name = "San_Francisco_is_super_cool"
        cmd = f'create City state_id="{state_id}" name="{name}"'
        city_id = self.getOutput(cmd)
        new_count = self.query(string)
        self.assertEqual(len(new_count) - len(old_count), 1)
        cmd = 'show City {}'.format(city_id)
        output = self.getOutput(cmd)
        self.assertIn(name.replace('_', ' '), output)

    def test_create_city_without_underscore(self):
        """Test create City"""
        string = "SELECT * FROM cities"
        cmd = 'create State name="California"'
        state_id = self.getOutput(cmd)
        name = "Fremont"
        cmd = f'create City state_id="{state_id}" name="{name}"'
        self.getOutput(cmd)
        new_count = self.query(string)
        self.assertIn(name.replace('_', ' '), str(new_count))


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') == 'db',
                 'console test not supported')
class TestHBNBCommand(unittest.TestCase):
    """Represents the test class for the HBNBCommand class.
    """

    def test_console_v_0_0_1(self):
        from tests import clear_stream
        """Tests the features of version 0.0.1 of the console.
        """
        with patch('sys.stdout', new=StringIO()) as cout:
            cons = HBNBCommand()
            # normal empty line
            cons.onecmd('')
            cons.onecmd('    ')
            self.assertEqual(cout.getvalue(), '')
            # empty line after a wrong command
            clear_stream(cout)
            cons.onecmd('ls')
            cons.onecmd('')
            cons.onecmd('  ')
            self.assertEqual(cout.getvalue(), '*** Unknown syntax: ls\n')
            # the help command
            clear_stream(cout)
            cons.onecmd('help')
            self.assertNotEqual(cout.getvalue().strip(), '')
            clear_stream(cout)
            cons.onecmd('help quit')
            self.assertNotEqual(cout.getvalue().strip(), '')
            clear_stream(cout)
            self.assertTrue(cons.onecmd('EOF'))
            self.assertTrue(cons.onecmd('quit'))

    def test_console_v_0_1(self):
        from tests import clear_stream
        """Tests the features of version 0.1 of the console.
        """
        with patch('sys.stdout', new=StringIO()) as cout:
            cons = HBNBCommand()
            if os.path.isfile('file.json'):
                os.unlink('file.json')
        # region The create command
            # missing class name
            clear_stream(cout)
            cons.onecmd('create')
            self.assertEqual(cout.getvalue(), "** class name missing **\n")
            # invalid class name
            clear_stream(cout)
            cons.onecmd('create Base')
            self.assertEqual(cout.getvalue(), "** class doesn't exist **\n")
            clear_stream(cout)
            cons.onecmd('create base')
            self.assertEqual(cout.getvalue(), "** class doesn't exist **\n")
            # valid class name
            clear_stream(cout)
            cons.onecmd('create BaseModel')
            mdl_sid = 'BaseModel.{}'.format(cout.getvalue().strip())
            self.assertTrue(mdl_sid in storage.all().keys())
            self.assertTrue(type(storage.all()[mdl_sid]) is BaseModel)
            with open('file.json', mode='r') as file:
                json_obj = json.load(file)
                self.assertTrue(type(json_obj) is dict)
                self.assertTrue(mdl_sid in json_obj)
        # endregion
        # region The show command
        # endregion
        # region The destroy command
        # endregion
        # region The all command
            # invalid class name
            clear_stream(cout)
            cons.onecmd('all Base')
            self.assertEqual(cout.getvalue(), "** class doesn't exist **\n")
            clear_stream(cout)
            cons.onecmd('all base')
            self.assertEqual(cout.getvalue(), "** class doesn't exist **\n")
            # valid class name
            clear_stream(cout)
            cons.onecmd('create BaseModel')
            mdl_id = cout.getvalue().strip()
            mdl_sid = 'BaseModel.{}'.format(mdl_id)
            clear_stream(cout)
            cons.onecmd('create Amenity')
            mdl_id1 = cout.getvalue().strip()
            mdl_sid1 = 'Amenity.{}'.format(mdl_id1)
            self.assertTrue(mdl_sid in storage.all().keys())
            self.assertTrue(mdl_sid1 in storage.all().keys())
            clear_stream(cout)
            cons.onecmd('all BaseModel')
            self.assertIn('[BaseModel] ({})'.format(mdl_id), cout.getvalue())
            self.assertNotIn('[Amenity] ({})'.format(mdl_id1), cout.getvalue())
            clear_stream(cout)
            cons.onecmd('all')
            self.assertIn('[BaseModel] ({})'.format(mdl_id), cout.getvalue())
            self.assertIn('[Amenity] ({})'.format(mdl_id1), cout.getvalue())
        # endregion
        # region The update command
            # missing instance id
            clear_stream(cout)
            cons.onecmd('update BaseModel')
            self.assertEqual(cout.getvalue(), "** instance id missing **\n")
            # invalid instance id
            clear_stream(cout)
            cons.onecmd('update BaseModel 49faff9a-451f-87b6-910505c55907')
            self.assertEqual(cout.getvalue(), "** no instance found **\n")
            # missing attribute name
            clear_stream(cout)
            cons.onecmd('create BaseModel')
            mdl_id = cout.getvalue().strip()
            clear_stream(cout)
            cons.onecmd('update BaseModel {}'.format(mdl_id))
            self.assertEqual(cout.getvalue(), "** attribute name missing **\n")
            # missing attribute value
            clear_stream(cout)
            cons.onecmd('update BaseModel {} first_name'.format(mdl_id))
            self.assertEqual(cout.getvalue(), "** value missing **\n")
            # missing attribute value
            clear_stream(cout)
            if os.path.isfile('file.json'):
                os.unlink('file.json')
            self.assertFalse(os.path.isfile('file.json'))
            cons.onecmd('update BaseModel {} first_name Chris'.format(mdl_id))
            self.assertEqual(cout.getvalue(), "")
            mdl_sid = 'BaseModel.{}'.format(mdl_id)
            self.assertTrue(mdl_sid in storage.all().keys())
            self.assertTrue(os.path.isfile('file.json'))
            self.assertTrue(hasattr(storage.all()[mdl_sid], 'first_name'))
            self.assertEqual(
                getattr(storage.all()[mdl_sid], 'first_name', ''),
                'Chris'
            )
        # endregion

    def test_user(self):
        """Tests the show, create, destroy, update, and all
        commands with a User model.
        """
        from tests import clear_stream
        with patch('sys.stdout', new=StringIO()) as cout:
            cons = HBNBCommand()
            # creating a User instance
            cons.onecmd('create User')
            mdl_id = cout.getvalue().strip()
            # showing a User instance
            clear_stream(cout)
            cons.onecmd('show User {}'.format(mdl_id))
            self.assertIn(mdl_id, cout.getvalue())
            self.assertIn('[User] ({})'.format(mdl_id), cout.getvalue())
            # showing all User instances
            clear_stream(cout)
            cons.onecmd('all User')
            self.assertIn(mdl_id, cout.getvalue())
            self.assertIn('[User] ({})'.format(mdl_id), cout.getvalue())
            # updating a User instance
            clear_stream(cout)
            cons.onecmd('update User {} first_name Akpanoko'.format(mdl_id))
            cons.onecmd('show User {}'.format(mdl_id))
            self.assertIn(mdl_id, cout.getvalue())
            self.assertIn(
                "'first_name': 'Akpanoko'".format(mdl_id),
                cout.getvalue()
            )
            # destroying a User instance
            clear_stream(cout)
            cons.onecmd('destroy User {}'.format(mdl_id))
            self.assertEqual(cout.getvalue(), '')
            cons.onecmd('show User {}'.format(mdl_id))
            self.assertEqual(cout.getvalue(), '** no instance found **\n')

    def test_state(self):
        """
        Test States
        """
        from tests import clear_stream
        with patch('sys.stdout', new=StringIO()) as cout:
            cons = HBNBCommand()
            clear_stream(cout)
            cons.onecmd('create State name="California"')
            mdl_id = cout.getvalue().strip()
            clear_stream(cout)
            cons.onecmd('show State {}'.format(mdl_id))
            self.assertIn(mdl_id, cout.getvalue())

    def test_class_all(self):
        from tests import clear_stream
        """Tests the ClassName.all() feature.
        """
        with patch('sys.stdout', new=StringIO()) as cout:
            cons = HBNBCommand()
            # create a sample object and show it
            cons.onecmd('create City')
            mdl_id = cout.getvalue().strip()
            clear_stream(cout)
            cmd_line = cons.precmd('City.all()'.format(mdl_id))
            cons.onecmd(cmd_line)
            self.assertIn(mdl_id, cout.getvalue())

    def test_class_show(self):
        from tests import clear_stream
        """Tests the ClassName.show(id) feature.
        """
        with patch('sys.stdout', new=StringIO()) as cout:
            cons = HBNBCommand()
            # create a sample object and show it
            cons.onecmd('create City')
            mdl_id = cout.getvalue().strip()
            clear_stream(cout)
            cmd_line = cons.precmd('City.show({})'.format(mdl_id))
            cons.onecmd(cmd_line)
            self.assertIn(mdl_id, cout.getvalue())

    def test_class_destroy(self):
        from tests import clear_stream
        """Tests the ClassName.destroy(id) feature.
        """
        with patch('sys.stdout', new=StringIO()) as cout:
            cons = HBNBCommand()
            # create a sample object and destroy it
            cons.onecmd('create City')
            mdl_id = cout.getvalue().strip()
            clear_stream(cout)
            cmd_line = cons.precmd('City.destroy({})'.format(mdl_id))
            cons.onecmd(cmd_line)
            clear_stream(cout)
            cons.onecmd('show City {}'.format(mdl_id))
            self.assertEqual(cout.getvalue(), "** no instance found **\n")

    def test_class_update_0(self):
        from tests import clear_stream
        """Tests the ClassName.update(id, attr_name, attr_value) feature.
        """
        with patch('sys.stdout', new=StringIO()) as cout:
            cons = HBNBCommand()
            # create a sample object and update it
            cons.onecmd('create Place')
            mdl_id = cout.getvalue().strip()
            clear_stream(cout)
            cmd_line = cons.precmd(
                'Place.update({}, '.format(mdl_id) +
                'name, "Rio de Janeiro")'
            )
            cons.onecmd(cmd_line)
            cons.onecmd('show Place {}'.format(mdl_id))
            self.assertIn(
                "'name': 'Rio de Janeiro'",
                cout.getvalue()
            )

    def test_class_update_1(self):
        from tests import clear_stream
        """Tests the ClassName.update(id, dict_repr) feature.
        """
        with patch('sys.stdout', new=StringIO()) as cout:
            cons = HBNBCommand()
            # create a sample object and update it
            cons.onecmd('create Amenity')
            mdl_id = cout.getvalue().strip()
            clear_stream(cout)
            cmd_line = cons.precmd(
                'Amenity.update({}, '.format(mdl_id) +
                "{'name': 'Basketball court'})"
            )
            cons.onecmd(cmd_line)
            cons.onecmd('show Amenity {}'.format(mdl_id))
            self.assertIn(
                "'name': 'Basketball court'",
                cout.getvalue()
            )

    def test_create_with_kwargs_fsv2(self):
        from tests import clear_stream
        ''' tests the create method of the console
            using the kwargs feature using filestorage
        '''
        with patch('sys.stdout', new=StringIO()) as cout:
            cons = HBNBCommand()
            # create a user using kwargs
            cons.onecmd('create User email="test@email.com" password=12345' +
                        ' first_name="big_john"')
            user_id = cout.getvalue().strip()
            clear_stream(cout)
            cons.onecmd('show User ' + user_id)
            user_info = cout.getvalue().strip()
            self.assertIn("'first_name': 'big john'", user_info)
            self.assertIn("'email': 'test@email.com'", user_info)
            if os.getenv('HBNB_TYPE_STORAGE') == 'db':
                self.assertIn("'password': '12345'", user_info)
            else:
                self.assertIn("'password': 12345", user_info)
            clear_stream(cout)
