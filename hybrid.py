#!/usr/bin/python3

#   This file is part of hybrid.
#
#   hybrid is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   hybrid is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with hybrid.  If not, see <http://www.gnu.org/licenses/>.

'''
    .. module:: hybrid
        :platform: Unix
        :synopsis: This is the main module of hybrid. It is kept very brief on purpose. Its only functions are to set up the rotating logger and to start the actual web server.

    .. moduleauthor:: chftyrol

    Synopsis
    ^^^^^^^^

    This is the main module of hybrid.
    It is kept very brief on purpose. Its only functions are to set up the rotating logger and to start the actual web server.

    Data
    ^^^^

    This module contains the definition of a few important constants (values for file paths are expressed as absolute).
        
    * ``LOGIN_DB_FILE`` *(str)* -  a json file containing login data for the clients. It is located in the directory where the python modules reside.
    * ``COOKIES_DB_FILE`` *(str)* - a json file containing data pertaining permanent cookies. It is located in the directory where the python modules reside.
    * ``SERVICE_CONF_FILE`` *(str)* - a config file defining what services are supported by this web application and their properties.
    * ``COOKIE_LIFETIME`` *(int)* - how many days should a permanent cookie stay valid for. Value is 90 days.
    * ``APP_KEY_FILE`` *(str)* - a file containing the key used to sign the cookies. It is located in the directory where the python modules reside.
    * ``LOG_FILE`` *(str)* - the location of the log file. It is located in the directory where the python modules reside.
    * ``PORT`` *(int)* - the port where the server will be accessible from.
    * ``LOGGING_SETTINGS_FILE`` *(str)* - The path to the JSON file containing the configuration of this app for the :py:mod:`logging` module.
    * ``VERSION`` *(str)* - A string defining the version of this program.
 
'''

import sys
import json
import logging
from optparse import OptionParser
import logging.config
import routing

LOGIN_DB_FILE = sys.path[0] + '/db/login.json'
COOKIES_DB_FILE = sys.path[0] + '/db/cookies.xml'
SERVICE_CONF_FILE = sys.path[0] + '/service.conf'
COOKIE_LIFETIME = 90 # days
PORT = 27172
APP_KEY_FILE = sys.path[0] + '/app_key' # Key to sign cookies.
LOGGING_SETTINGS_FILE = sys.path[0] + '/log/settings.json'
VERSION = "1.0"

def setup_logging(stdout_level="ERROR", path=LOGGING_SETTINGS_FILE, default_level=logging.INFO):
    try :
        with open(path, 'rt') as f:
            config = json.load(f)
        config['handlers']['console']['level'] = stdout_level
        logging.config.dictConfig(config)
    except :
        print('Error while setting up logging configuration. Using defaults.')
        logging.basicConfig(level=default_level)

if __name__ == '__main__':

    optparser = OptionParser(description="A gateway to the services on your home server.", version=VERSION)
    optparser.add_option("-p", "--port", help="Specify the port where the server will run. The default value is " + str(PORT), action="store", type="int", dest="port")
    optparser.add_option("-v", help="Specify verbosity on stdout. i.e. -v means verbose, -vv means debug.", action="count", dest="verbosity")
    optparser.add_option("-q", "--quiet", help="Whisper to me, baby.", action="store_true", dest="quiet")
    (options, args) = optparser.parse_args()

    if options.verbosity and options.quiet:
        optparser.error("You can't be both verbose and quiet.")
    stdout_verbosity = "ERROR"
    if options.verbosity:
        if options.verbosity == 1 :
            stdout_verbosity = "INFO"
        elif options.verbosity > 1 :
            stdout_verbosity = "DEBUG"
    if options.quiet:
        stdout_verbosity = "CRITICAL"
    if options.port and options.port >= 1024 :
        PORT = options.port

    setup_logging(stdout_level=stdout_verbosity)
    logger = logging.getLogger(__name__)
    logger.debug("Loaded logging config.")
    logger.debug("Initializing routing module.")

    # Initialize hybrid
    routing.init(login_db_file=LOGIN_DB_FILE, cookies_db_file=COOKIES_DB_FILE, service_conf_file=SERVICE_CONF_FILE, cookie_lifetime=COOKIE_LIFETIME, secret_key_file=APP_KEY_FILE)
    # Start hybrid
    if not options.quiet:
        print("Firing Hybrid up on port", PORT)
    routing.start(host="0.0.0.0", port=PORT)
