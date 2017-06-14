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
    .. module:: helpers
        :platform: Unix
        :synopsis: This module contains the definition of a few helper classes and functions used by Hybrid.

    .. moduleauthor:: chftyrol

'''
'''
    This module contains the definition of a few helper classes and functions used by Hybrid.
    
    Most of the contents of this module are simple classes like Action, Link etc. used to represent structured data types and nothing more.
    A few custom exceptions are also defined.

    There are also a couple of methods not belonging to any class, such as the Hybrid utterance generator.
'''
import random
import configparser
import os
import logging

logger = logging.getLogger(__name__)

class Link:
    '''
        Simple class used to pass Link objects to Jinja HTML templates.
        Example:

        .. code-block:: python

            >>> redditLink = Link("https://reddit.com/r/owlsinhats", "Check out some cool looking owls wearing hats!")

        :param href: The target of the link.
        :type href: str.
        :param caption: The text displayed on the link.
        :type caption: str.
    '''
    def __init__(self, href, caption):
        self.href = href
        self.caption = caption
class Action:
    '''
        Represents a possible action to perform on a service, for example start, disable, navigate, etc.
        Example:

        .. code-block:: python

            >>> restartAction = Action("restart", "⟳")

        :param which: Specify which action is to be taken. Valid values are only: ``start``, ``stop``, ``restart``, ``enable``, ``disable``, ``navigate``.
        :type which: str.
        :param description: Symbol or text describing the action.
        :type description: str.
    '''
    def __init__(self, which, description):
        self.which = which
        self.description = description
class Service:
    '''
        Entity corresponding to an entry in HSM.

        :param title: the title of the service item, as displayed in HSM webpage.
        :type title: str.
        :param description: a description of the service item, as displayed in HSM webpage.
        :type description: str.
        :param id: an id string for reference. It is used in many places, namely as class attribute in HSM for elements relative to a service, in the config file as a section id.
        :type id: str.
        :param actions: a list of allowed Action objects that can be performed with this Service.
        :type actions: List
        :param measureMethod: either ``systemd``, ``systemd-user`` or ``Script``. This specifies how the measurement of status of the service will be performed.
        :type measureMethod: str.
        :param actionsMethod: either ``systemd``, ``systemd-user`` or ``Script``. This specifies how actions on the service will be performed.
        :type actionsMethod: str.
        :param measurementInstrument:
                               - if ``measureMethod`` is ``systemd`` it is the systemd unit probed for ``is-active`` and ``is-enabled`` properties;
                               - if ``measureMethod`` is 'systemd-user' it is the user systemd unit probed for ``is-active`` and ``is-enabled`` properties;
                               - if ``measureMethod`` is ``Script`` it is the full path to a script which must return a string concatenating either ``active``, ``inactive``, ``unknown`` (for the is-active part) and either ``disabled``, ``enabled``, ``unknown`` (for the ``is-enabled`` part)
        :type measurementInstrument: str.
        :param actionInstrument: 
                               - if ``measureMethod`` is ``systemd`` or ``systemd-user`` it is the systemd unit triggered to ``start``, ``stop`` etc.
                               - if ``measureMethod`` is ``Script`` it is the full path to a script which performs the following:
                                  * starts the service when passed the argument ``start`` ;
                                  * stops the service when passed the argument ``stop`` ;
                                  * restarts the service when passed the argument ``restart`` ;
                                  * enables the service when passed the argument ``enable`` (if available) ;
                                  * disables the service when passed the argument ``disable`` (if available) ;
        :type actionInstrument: str.
        :param navigatePort: the redirection port destination, when performing a ``navigate`` action.
        :type measureMethod: str.
    '''
    def __init__(self, title, description, id, actions, measureMethod, actionMethod, measurementInstrument, actionInstrument, navigatePort):
        self.title = title
        self.description = description
        self.id = id
        self.actions = actions
        self.measureMethod = measureMethod
        self.actionMethod = actionMethod
        self.measurementInstrument = measurementInstrument
        self.actionInstrument = actionInstrument
        self.navigatePort = navigatePort

class InvalidServiceRequest(Exception):
    '''
        Base class for exceptions about performing unallowed Actions of performing actions on unallowed Targets.
    '''
    pass
class TargetNotAllowedException(InvalidServiceRequest):
    '''
        Exception raised when client tries to do something with a target (Service) it is not supposed to work with.

        :param target: The forbidden target which was attempted to be accessed.
        :type target: str.
    '''
    def __init__(self, target):
        self.target = target
class ActionNotAllowedException(InvalidServiceRequest):
    '''
        Exception raised when client tries to do an unallowed Action with a certain service.

        :param action: The forbidden action which was attempted to be performed.
        :type action: str.
    '''
    def __init__(self, action):
        self.action = action
class UnknownMethodException(Exception):
    '''
        Base class for exceptions about invalid measureMethod or actionMethod
    '''
    pass
class UnknownActionMethodException(UnknownMethodException):
    '''
        Exception raised when a value for actionMethod differing from either ``systemd``, ``systemd-user`` or ``script`` is given

        :param method: The invalid value of actionMethod that raised this exception.
        :type method: str.
    '''
    def __init__(self, method):
        self.method = method
        self.msg = "Invalid value for actionMethod: " + method + "\n The only allowed values are 'systemd', 'systemd-user' and 'script'."
class UnknownMeasureMethodException(UnknownMethodException):
    '''
        Exception raised when a value for measureMethod differing from either ``systemd``, ``systemd-user`` or ``script`` is given

        :param method: The invalid value of measureMethod that raised this exception.
        :type method: str.
    '''
    def __init__(self, method):
        self.method = method
        self.msg = "Invalid value for measureMethod: " + method + "\n The only allowed values are 'systemd', 'systemd-user' and 'script'."

def get_utterance(utteranceSrcFile):
    '''
        Generate enough random Hybrid utterance to fill the screen.

        :param utteranceSrcFile: a file acting as the source for the utterance. It contains one quote of the Battlestar Galactica Hybrids per line.
        :type utteranceSrcFile: str.
    '''
    try :
        logger.debug("Reading utterance file.")
        with open(utteranceSrcFile, "r") as f:
            lines = f.readlines()
            minlen = 5400
            nquotes = 30
            utterance = ""
            logger.debug("Generating random utterance.")
            random.seed()
            while len(utterance) < minlen:
                randlines = random.sample(lines, nquotes)
                utterance = "\n".join(randlines)
                nquotes += 2
            return "\n".join(randlines)
    except OSError as ose:
        logger.error('Error opening file ' + ose.filename + '\nDescription:\n' + ose.strerror)

def get_services_list(serviceConfFile):
    '''
        Generate the list of available services the client can operate with.

        It is specified by the conf file ``serviceConfFile``, with the syntax specified in :ref:`serviceconfsyntax`.

        :param serviceConfFile: the ``service.conf`` file path, containing the specification of the supported services, their measurement and action methods and their allowed actions.
        :type serviceConfFile: str.
        :returns: ``list`` -- A list of ``Service`` objects.
    '''
    '''
        The DEFAULT section in that file it propagated to all sections.
        Having this information hardcoded provides a safe way to operate on the machine services, especially when using systemd units instead of custom scripts.
        This is because stuff from the client (presumably unsafe) is never directly written in a command.
        Instead we write content from this list's items and its members.

        serviceConfFile Syntax:
            Name: the name of the service
            Description: a description of what the service does
            AllowedActions: a comma separated list of the actions that can be performed to the service. 
                The only acceptable values here are: start, stop, restart, enable, disable and navigate.
            MeasureMethod: one of the following (case insensitive keys):
                'systemd' : status of the service should be measured by checking the status of a systemd unit, specified by MeasurementInstrument
                'systemd-user' : status of the service should be measured by checking the status of a user systemd unit, specified by MeasurementInstrument
                'Script' : the status of the service should be measured by running a custom script, which full path is specified in MeasurementInstrument
            MeasurementInstrument: if MeasureMethod is either 'systemd' or 'systemd-unit' this must be a systemd unit (a user one in case of 'systemd-unit')
                                   if MeasureMethod is 'Script' this is the full path of the custom script. Said script when run should return a string in the form:
                                        "<A> <E>"
                                    where <A> can be: active, inactive, unknown
                                    and <E> can be: enabled, disabled, unknown.
            ActionMethod: same as MeasureMethod, but specify the way we will be operating on the service
            MeasurementInstrument : if MeasureMethod is either 'systemd' or 'systemd-unit' this must be a systemd unit (a user one in case of 'systemd-unit')
                                    if MeasureMethod is 'Script' this is the full path of the custom script. Said script should do the following:
                                        - start the service when passed the arg 'start'
                                        - stop the service when passed the arg 'stop'
                                        - restart the service when passed the arg 'restart'
                                        - enable the service when passed the arg 'enable' (if applicable)
                                        - disable the service when passed the arg 'disable' (if applicable)
            NavigatePort: the port of the destination of the ``navigate`` action.
                                    
    '''
    logger.debug("Generating services list.")
    res = []
    conf = configparser.ConfigParser()
    try :
        logger.debug("Reading services file %s", serviceConfFile)
        conf.read(serviceConfFile)
    except configparser.Error as err:
        logger.error('Could not load services list from %s \n Error was: %s', serviceConfFile, err.msg)
        return res
    for sec in conf.sections():
        try :
            actionstxt = conf[sec]['AllowedActions'].split(",")
        except KeyError as ke:
            logger.error(str(ke) + " entry was not found while parsing file " + serviceConfFile)
            actionstxt = []
        actions = []
        for a in actionstxt:
            sym = ""
            if a == "start":
                sym = "▶"
            elif a == "stop":
                sym = "■"
            elif a == "restart":
                sym = "⟳"
            elif a == "navigate":
                sym = "↝"
            elif a == "enable":
                sym = "✓"
            elif a == "disable":
                sym = "⍻"
            actions.append(Action(a, sym))

        try :
            res.append(Service(title=conf[sec]['Name'], \
                               description=conf[sec]['Description'], \
                               id=sec, \
                               actions=actions, \
                               measureMethod=conf[sec]['MeasureMethod'], \
                               actionMethod=conf[sec]['ActionMethod'], \
                               measurementInstrument=conf[sec]['MeasurementInstrument'], \
                               actionInstrument=conf[sec]['ActionInstrument'], \
                               navigatePort=conf[sec]['NavigatePort'] ))
        except KeyError as ke:
            logger.error(str(ke) + " entry was not found while parsing file " + serviceConfFile)
    return res

if __name__ == "__main__":
    print("This module is not meant to be run on its own.")
    print("It defines data structures, classes and methods used by routing and hybrid")
    quit()
