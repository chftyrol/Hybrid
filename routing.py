#!/usr/bin/python3


#   This file is part of Hybrid.
#
#   Hybrid is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Hybrid is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with Hybrid.  If not, see <http://www.gnu.org/licenses/>.


'''
    .. module:: routing
        :platform: Unix
        :synopsis: This module provides the core functionality of the web service. It defines the functionality of each web page, the relationships between them and it manages HTTP request, taking action upon them if necessary.

    .. moduleauthor:: chftyrol

'''

'''
    This module provides the core functionality of the web service.
    It defines the functionality of each web page, the relationships between them and it manages HTTP request, taking action upon them if necessary.
'''
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort, make_response
import os
import sys
import subprocess
import bcrypt
import json
from base64 import b64encode
from helpers import Link, Service, Action, get_utterance, get_services_list, ActionNotAllowedException, TargetNotAllowedException, UnknownActionMethodException, UnknownMeasureMethodException
from cookiebaker import CookieBaker
import datetime
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)
loginDBFile = cookiesDBFile = serviceConfFile = logFile = ""
cookieLifetime = 0

def init(login_db_file, cookies_db_file, service_conf_file, cookie_lifetime, secret_key_file):
    '''
        Initialize global variables of this module.

        Information for these comes from hybrid, which specifies the paths for all DB and conf files.
        The logging setup also comes from hybrid, which gives us the logger object used in this module.
        Also, read the secret key from the appropriate file and set it. This ``secret_key`` is used to sign both session and long-lived cookies.

        :param login_db_file: Path of the json file containing the login data.
        :type login_db_file: str.
        :param cookies_db_file: Path of the json file containing the data pertaining login via permanent cookie.
        :type cookies_db_file: str.
        :param service_conf_file: Path of the config file containing the settings for the services offered by the server.
        :type service_conf_file: str.
        :param cookie_lifetime: How long (in days) should a permanent login cookie remain valid.
        :type cookie_lifetime: int.
        :param secret_key_file: Path of the file containing the secret key.
        :type secret_key_file: str.
        :raises: ``OSError``
    '''
    '''
    '''
    logger.debug("Initializing routing.")
    # the global statement here is necessary, otherwise global variables are not editable from a local scope.
    global loginDBFile, cookiesDBFile, serviceConfFile, logFile, cookieLifetime
    loginDBFile = login_db_file # file containing login data
    cookiesDBFile = cookies_db_file # file containing login via cookie data
    serviceConfFile = service_conf_file # config file specifying allowed actions and services
    cookieLifetime = cookie_lifetime 
    if not os.path.isfile(loginDBFile):
        # if login db file does not exist ==> create it
        logger.debug("Login DB file %s does not exist.", loginDBFile)
        try :
            with open(loginDBFile, 'w') as f:
                json.dump({ }, f)
            logger.info('Created login db file ' + loginDBFile)
        except OSError as ose:
            logger.error('Error opening file ' + ose.filename + '\nDescription:\n' + ose.strerror)
    if not os.path.isfile(secret_key_file):
        # if secret key file does not exist ==> create it with generated key
        logger.debug("Secret key file %s does not exist.", secret_key_file)
        try :
            with open(secret_key_file, 'w') as f:
                f.write(b64encode(os.urandom(96)).decode('utf-8'))
            os.chmod(secret_key_file, 0o640)
            logger.info('Generated app_key and wrote to file %s', secret_key_file)
        except OSError as ose:
            logger.error('Error opening file ' + ose.filename + '\nDescription:\n' + ose.strerror)
    # Read app_key from file
    try :
        with open(secret_key_file, 'r') as keyfile:
            app.secret_key = keyfile.read()
    except OSError as ose:
        logger.error('Error opening file ' + ose.filename + '\nDescription:\n' + ose.strerror)

def start(host, port):
    '''
        Start web server at the specified host and port

        :param host: IP Address to listen to (use 0.0.0.0 to mean all public IPs).
        :type host: str.
        :param port: specify on which port this web server should run.
        :type port: int.
    '''
    logger.debug("Starting web server.")
    app.run(host=host, port=port)

@app.route('/')
def index():
    '''
        Render the index page.

        :returns: ``flask.Response`` -- HTTP response containing the rendered web page
    '''
    logger.debug("Rendering index page")
    a_hybrid_service_manager = Link("/hsm", "Hybrid Service Manager")
    a_about = Link("/about/", "What's This?")
    nav = [ a_hybrid_service_manager, a_about ]
    return render_template("index.html", navigation=nav, utterance=get_utterance(sys.path[0] + '/content/utterance'))

@app.route('/about/')
def about():
    '''
        Render the about page.

        :returns: ``flask.Response`` -- HTTP response containing the rendered web page
    '''
    logger.debug("Rendering about page")
    a_hybrid_service_manager = Link("/hsm", "Hybrid Service Manager")
    a_about = Link("/about/", "What's This?")
    nav = [ a_hybrid_service_manager, a_about ]
    try :
        logger.debug("Reading content of page about.html")
        with open(sys.path[0] + "/content/about.html", "r") as f:
            html = f.read()
    except OSError as ose:
        logger.error('Error opening file ' + ose.filename + '\nDescription:\n' + ose.strerror)
        return 'Internal server error', 500
    return render_template("generic.html", navigation=nav, content=html, title="About Hybrid", h1='About <a href="/" class="title">Hybrid</a>')

@app.route('/iosevka_notice/')
def iosevka_notice():
    '''
        Render page with Iosevka Notice Information.

        :returns: ``flask.Response`` -- HTTP response containing the rendered web page
    '''
    logger.debug("Rendering page Iosevka notice.")
    a_hybrid_service_manager = Link("/hsm", "Hybrid Service Manager")
    a_about = Link("/about/", "What's This?")
    nav = [ a_hybrid_service_manager, a_about ]
    try :
        logger.debug("Reading content of page iosevka_notice.html")
        with open(sys.path[0] + "/content/iosevka_notice.html", "r") as f:
            html = f.read()
    except OSError as ose:
        logger.error('Error opening file ' + ose.filename + '\nDescription:\n' + ose.strerror)
        return 'Internal server error', 500
    return render_template("generic.html", navigation=nav, content=html, title="Iosevka Notice", h1="Iosevka Notice")

@app.route('/hsm/')
def hsm():
    '''
        If user is logged in, render the Hybrid Service Manager web application, otherwise return a response redirecting to the login page.

        :returns: ``flask.Response`` -- HTTP response containing the rendered web page or the redirect response.
    '''
    logger.debug("Checking if user is logged in to see HSM.")
    a_hybrid_service_manager = Link("/hsm", "Hybrid Service Manager")
    a_about = Link("/about/", "What's This?")
    nav = [ a_hybrid_service_manager, a_about ]
    if not session.get('logged_in') :
        logger.debug("User is not logged in. Redirecting to login page.")
        return redirect(url_for('login'))
    else :
        logger.debug("User is logged in. Rendering HSM.")
        return render_template("hsm.html", navigation=nav, services=get_services_list(serviceConfFile))
@app.route('/login/')
def login():
    '''
        Show the login form, or log the user in directly if the client exhibits a valid rememberme cookie.

        .. note::
            
            As of now, there is not need for a 'next' parameter, as the only thing that needs logging in is HSM.

        :returns: ``flask.Response`` -- HTTP response containing the rendered login web page or the redirect response to HSM.
    '''
    logger.debug("Starting login procedure.")
    rememberme_cookie = request.cookies.get('rememberme')
    logger.debug("Checking if user has a rememberme cookie.")
    if rememberme_cookie:
        logger.debug("User has a rememberme cookie! Checking its validity.")
        cookieman = CookieBaker(cookiesDBFile, app.secret_key)
        cookieLoginUser = cookieman.check(rememberme_cookie)
        if cookieLoginUser:
            logger.debug("User %s has a valid rememberme cookie!", cookieLoginUser)
            logger.info('%s successfully logged in via cookie!', cookieLoginUser)
            session['logged_in'] = True
            return redirect(url_for('hsm'))

    a_hybrid_service_manager = Link("/hsm", "Hybrid Service Manager")
    a_about = Link("/about/", "What's This?")
    nav = [ a_hybrid_service_manager, a_about ]
    logger.debug("Rendering login page.")
    return render_template("login.html", navigation=nav)

@app.route('/login/attempt/', methods=['POST'])
def login_attempt():
    '''
        Attempt login via username, password through a POST request.

        For details on this method's internal workings check :ref:`loginattempt`.

        :returns: ``flask.Response`` -- HTTP response with either:

                  * a redirection to HSM.
                  * a 400 Bad Request HTTP Error (if the request is malformed).
                  * a 401 Unauthorized HTTP Error (if the credentials are not valid).
        :raises: ``json.JSONDecodeError``, ``OSError``

    '''
    '''
        request.form is a dictionary containing the data for the login request. It is like this:
            {attemptedid: "SHA256(attemptedpw)", rememberme: i}
        where i is an integer, taking values 0 (=== False) and 1 (=== True).
        If the dictionary doesn't have either 1 or 2 key/value pairs, return a 400 Bad Request.
        Otherwise read our loginDBFile. Look for an entry with username == attemptedid. If not found return a 401 Unauthorized.
        Otherwise with bcrypt do a checkpw of SHA256(attemptedpw) against the stored password hash for the matching user.
        If passwords don't match throw a 401 Unauthorized.
        Otherwise, log in the user by setting session['logged_in'] = True. This will be checked by other functions when they need to see if the user is logged in.
        If the user asked to be remembered bake a signed cookie with CookieBaker.
        The give it an expiration date and give it to the client.
    '''
    logger.debug("Attempting to log in.")
    if request.method == 'POST' :
        resp = make_response(url_for('hsm'))
        # salted and hashed by client. We salt and hash it again with bcrypt.
        req_keys = list(request.form.keys())
        if len(req_keys) == 1 or len(req_keys) == 2 : 
            # if rememberme is appearing first in the login data passed with the request, then the username, hashed_password field is the second one.
            # and vice versa.
            idindex = ( req_keys.index('rememberme') + 1 ) % 2
            attemptedid = req_keys[idindex]
            attemptedpw = request.form[attemptedid]
            rememberme = int(request.form['rememberme'])
            logger.info('Login attempt by ' + attemptedid)
            try :
                with open(loginDBFile, 'r') as logindbfile :
                    try :
                        logindb = json.load(logindbfile)
                        if attemptedid in logindb:
                            if bcrypt.checkpw(attemptedpw.encode('utf-8'), logindb[attemptedid].encode('utf-8')) :
                                logger.info(attemptedid + ' logged in successfully.')
                                session['logged_in'] = True
                                if rememberme:
                                    logger.debug("User requested rememberme cookie. Let's get them one.")
                                    t = datetime.datetime.now()
                                    t = t + datetime.timedelta(days=cookieLifetime)
                                    cookie_death_timestamp = int(t.timestamp())
                                    cookieman = CookieBaker(cookiesDBFile, app.secret_key)
                                    rememberme_cookie = cookieman.bake(attemptedid)
                                    cookieman.store(rememberme_cookie, cookie_death_timestamp)
                                    logger.info('Setting rememberme cookie, with expiry date %s', t.isoformat())
                                    resp.set_cookie('rememberme', rememberme_cookie, expires=cookie_death_timestamp)
                            else :
                                logger.warning('Failed login attempt by ' + attemptedid) # wrong pw, but user exists.
                                return 'Login failed', 401 # 401 is 'Unauthorized'
                        else :
                            logger.warning('Failed login attempt by ' + attemptedid) # user does not exist
                            return 'Login failed', 401 # 401 is 'Unauthorized'
                    
                    except json.JSONDecodeError as err:
                        logger.error('Error parsing the JSON document ' + loginDBFile + '\nmessage:\n' + err.msg)
                        return 'Internal server error', 500
            except OSError as ose:
                    logger.error('Error opening file ' + ose.filename + '\nDescription:\n' + ose.strerror)
                    return 'Internal server error', 500
        else : 
            return 'Bad Request', 400
    return resp


@app.route('/hsm/perform_action/')
def perform_action():
    '''
        Process a request to act on a service of the server.

        For details on this method's internal workings check :ref:`performaction`.

        :raises: ``ActionNotAllowedException``, ``TargetNotAllowedException``, ``UnknownActionMethodException``, ``UnknownMeasureMethodException``, ``subprocess.CalledProcessError``
        :returns: ``flask.Response`` -- HTTP response with either:

          * a 200 OK code.
          * a 403 Forbidden HTTP Error (if the request is for unallawed targets and/or actions).
          * a 500 Internal Error code (if a server error occurs while performing the action).

    '''
    '''
        Look if the request for action corresponds (by Action and by Service) to an allowed combination of Action and Service
        as specified by the list of get_services_list()
        If the request is for anything not allowed raise corresponding exceptions and return a 403 Forbidden error.
        Otherwise the request is safe, so we take action.
        The action taken depends on the actionMethod of the Service.
        In case of actionMethod == "systemd" run:

        .. code-block:: sh

            $ systemctl <what> <who.unit>

        Note that this approach is highly unrecommended because to be able to operate on global systemd units, the server should be run as root, which is a security hazard.
        Instead prefer one of the following two approaches (with the first one being the safest).
        In case of actionMethod == "systemd-user" run:

        .. code-block:: sh

            $ systemctl --user <what> <who.unit>

        In case of actionMethod == "script" run:

        .. code-block:: sh

            $ <s.actionInstrument> <what>

        where actionInstrument is a custom user script that has to accept the args "start", "stop", "restart" and if feasible "enable" and "disable"
        and act accordingly.
        Manage the possible exceptions. If all is fine, return a 200 OK.
    '''
    services = get_services_list(serviceConfFile)
    who = request.args.get('who') # the id of the requested Service
    what = request.args.get('what') # the which of the requested Action
    logger.debug("Performing action %s on target %s", what, who)
    requested_service = None
    logger.debug("Checking if the action and target are allowed.")
    try :
        targetAllowed = actionAllowed = False
        for s in services:
            if who == s.id:
                targetAllowed = True
                logger.debug("Target is allowed.")
                actionstxt = []
                for a in s.actions:
                    actionstxt.append(a.which)
                if what in actionstxt:
                    actionAllowed = True
                    logger.debug("Action is allowed.")
                    requested_service = s
                    break

        if not targetAllowed:
            raise TargetNotAllowedException(who)
        if not actionAllowed:
            raise ActionNotAllowedException(what)
    except TargetNotAllowedException as e:
        logger.error("The client request to operate on target %s, which is not allowed.", e.target)
        return 'Forbidden', 403
    except ActionNotAllowedException as err:
        logger.error("The client request to perform action '%s', which is not allowed.", err.action)
        return 'Forbidden', 403

    if what != 'navigate':
        try :
            if s.actionMethod.lower() == "systemd" :
                command = 'systemctl ' + what + ' ' + s.actionInstrument
            elif s.actionMethod.lower() == "systemd-user" :
                command = 'systemctl --user ' + what + ' ' + s.actionInstrument
            elif s.actionMethod.lower() == "script" :
                command = s.actionInstrument + " " + what
            else :
                raise UnknownActionMethodException(s.actionMethod)

            logger.debug("Computed command to perform action: '%s'", command)
            proc = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
            proc.wait() # wait for proc to finish
            stderr = proc.stderr.read().decode('ascii')
            if stderr:
                raise subprocess.CalledProcessError(cmd=command, output=stderr, returncode=proc.returncode)
        except subprocess.CalledProcessError as err:
            logger.error("An error occurred while performing the requested action. \n\tOffending command was: %s\n\tExit Code=%d\n\tOutput:%s ", err.cmd, err.returncode, err.stdout)
            return 'Internal server error', 500
        except UnknownActionMethodException as uame:
            logger.error(uame.msg)
            return 'Internal server error', 500
    else :
        resp = make_response(s.navigatePort)
        return resp
        
    return 'OK', 200

@app.route('/hsm/measure_status/')
def measure_status():
    '''
        Measure the status (is the service running? Is it enabled?) for each service and send the results to the client.

        For details on this method's internal workings check :ref:`measurestatus`.

        :raises: ``UnknownMeasureMethodException`, ``subprocess.CalledProcessError``
        :returns: ``flask.Response`` -- HTTP response with the results in JSON format. e.g.

        .. code-block:: json

            {"status_all":{"kodi":"unavailable","sickrage":"unavailable","transmission":"inactive disabled"}}
    '''

    '''
        The way the measurement is done is specified by measureMethod: we use systemd units or custom user scripts.
        In any case the output of the command must be of the form:
            "<A> <E>"
        where <A> can be: active, inactive, unknown
        and <E> can be: enabled, disabled, unknown.
        The results of this are put in a JSON like:
            {"status_all":{"kodi":"unavailable","sickrage":"unavailable","transmission":"inactive disabled"}}
        and sent as a get response to the client.
    '''
    services = get_services_list(serviceConfFile)
    statuses = {}
    logger.debug("Checking services status.")
    for s in services:
        try :
            if s.measureMethod.lower() == "systemd" :
                command = 'echo -n $(systemctl is-active ' + s.measurementInstrument + ') $(systemctl is-enabled ' + s.measurementInstrument + ')' 
            elif s.measureMethod.lower() == "systemd-user" :
                command = 'echo -n $(systemctl --user is-active ' + s.measurementInstrument + ') $(systemctl --user is-enabled ' + s.measurementInstrument + ')' 
            elif s.measureMethod.lower() == "script" :
                command = s.measurementInstrument
            else :
                raise UnknownMeasureMethodException(s.measureMethod)
            # output of command must be in a form like "inactive enabled" if no errors occur
            # the first word can be: active, inactive, unknown
            # the second word can be: enabled, disabled, unknown
            logger.debug("Computed command for checking: '%s'", command)
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait() # wait for proc to finish
            statuses[s.id] = proc.stdout.read().decode('ascii')
            stderr = proc.stderr.read().decode('ascii')
            if stderr:
                raise subprocess.CalledProcessError(cmd=command, output=stderr, returncode=proc.returncode)
        except subprocess.CalledProcessError as err:
            logger.error("An error occurred while measuring the services status. \n\tOffending command was: %s\n\tExit Code=%d\n\tOutput:%s ", err.cmd, err.returncode, err.stdout)
            statuses[s.id] = 'unavailable'
        except UnknownMeasureMethodException as umme:
            logger.error(umme.msg)
            statuses[s.id] = 'unavailable'

    return jsonify(status_all=statuses)

if __name__ == "__main__":
    print("This module is not meant to be run on its own.")
    print("Take a look at hybrid for a way to use it properly.")
    quit()
