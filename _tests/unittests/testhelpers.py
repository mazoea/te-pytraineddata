# coding=utf-8
# See main file for licence
# pylint: disable=C0111,W0212
#
import time
import logging
import sys
import os
import tempfile
import unittest

import testsettings

project_path = os.path.join( os.path.dirname( __file__ ),
                             testsettings.settings['path_to_project'] )
if not project_path in sys.path:
    sys.path.insert( 0, project_path )

sys.path.insert( 0, os.path.dirname( __file__ ) )


#
#
#

class test_case( unittest.TestCase ):
    """
        Unified approach to all tests.
    """

    # noinspection PyMethodOverriding
    @classmethod
    def setUpClass(cls):
        """
            Unified first function.
        """
        logging.basicConfig( level=logging.DEBUG, format="%(message)s" )
        logging.getLogger( ).warning( 40 * "<" + "\nExecuting tests in [%s].\n" % cls.__module__ )
        cls ._time = time.time( )

    # noinspection PyMethodOverriding
    @classmethod
    def tearDownClass(cls):
        """
            Unified last function.
        """
        files.chdir_to_start_dir( )
        lasted = time.time( ) - cls._time
        logging.getLogger( ).warning( "\nFinished tests in [%s] after [%s] seconds." % (cls.__module__, lasted) )
        logging.getLogger( ).warning( 40 * ">" )
        files.chdir_to_start_dir( )

    def setUp(self):
        """
            Unified setUp.
        """
        self._test_time = time.time( )
        logging.getLogger( ).warning( 40 * "." )

    def tearDown(self):
        """
            Unified tearDown.
        """
        lasted = time.time( ) - self._test_time
        name = self.shortDescription( )
        logging.getLogger( ).warning( "\nFinished test [%s] after [%s] seconds." % (name, lasted) )
        logging.getLogger( ).warning( 40 * "." )


#
#
#

class files( object ):
    """
        File helper function wrapper.
    """

    @staticmethod
    def __in_dir(dir_str, file_str, start_path=None):
        """
            Returns tuple (file_name, exists_bool).

            IF start_path is None uses dirname of this file.
        """
        start_path = os.path.abspath( testsettings.settings["start_dir"] ) \
            if start_path is None else start_path
        file_str = os.path.join( start_path, dir_str, file_str )
        return file_str, os.path.exists( file_str )

    @staticmethod
    def in_data_dir(file_str, start_path=None):
        """
            Returns tuple (file_name, exists_bool) of a file in data_dir.
        """
        return files.__in_dir( testsettings.settings["data_dir"], file_str, start_path )

    @staticmethod
    def in_temp_dir(file_str, start_path=None, cleanup_at=None):
        """
            Returns file_name of a file in temp_dir.

            If file_str is None returns temporary file.
        """
        temp_dir = testsettings.settings["temp_dir"]
        if file_str is None or file_str == "":
            tmp_dir, _ = files.__in_dir( temp_dir, ".", start_path=start_path )
            file_str = tempfile.NamedTemporaryFile( dir=tmp_dir ).name

        file_str, exists = files.__in_dir( temp_dir, file_str, start_path )
        if exists:
            os.remove( file_str )

        if not cleanup_at is None:
            cleanup_at( os.remove, file_str )

        return file_str

    @staticmethod
    def chdir_to_project():
        """
            Change dir to project.
        """
        os.chdir( os.path.join( testsettings.settings["start_dir"],
                                testsettings.settings["path_to_project"] ) )
        print "Changing to " + os.getcwd( )
        pass

    @staticmethod
    def chdir_to_start_dir():
        """
            Not really needed for now. Called from tearDownClass.
        """
        pass


#
#
#

class output( object ):
    """
        Common output.
    """

    @staticmethod
    def test(msg_str):
        """ Output with indentation. """
        print "\n", 40 * "="
        print msg_str

    @staticmethod
    def out(msg_str):
        """ Output with indentation. """
        print "\t" + msg_str


#
#
#

class intercept_sys_stdout( object ):
    """
        Sys stdout interceptor.
    """

    def __init__(self, module_=None):
        logging.basicConfig( level=logging.DEBUG, stream=self )
        self._text = u""
        self.module_ = module_

    def write(self, text):
        if text.strip( ) == "":
            return
        sys.__stdout__.write( text )
        self._text += text

    def flush(self):
        pass

    def get(self):
        return self._text

    def __del__(self):
        if not self.module_ is None:
            self.module_.stdout = sys.__stdout__
