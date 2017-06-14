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
    .. module:: cookiebaker
        :platform: Unix
        :synopsis: A module to manage long-lived login cookies.

    .. moduleauthor:: chftyrol
    
'''
'''
    This module contains the implementation of the CookieBaker class.

    CookieBaker is a class implementing a manager of login cookies.

    It can generate them, store and delete them, as well as check them for integrity and against a db.

    Cookies consist of couples (cookieKey, cookieVal).
    For our purpose cookieKey will always be 'rememberme'.
    cookieVal is obtained as follows: make a dictionary with the username as key and
    cookieSize random bytes from urandom. Said dictionary is then encoded and signed using the 
    JSON Web Signature (JWS) standard.

    Our cookies are stored in cookieStorageFile, after being hashed with bcrypt.
'''

import os
import bcrypt
from itsdangerous import JSONWebSignatureSerializer, BadSignature
import xml.etree.cElementTree as ET
from base64 import b64encode
import datetime
import logging

logger = logging.getLogger(__name__)

class CookieBaker:
    '''
        CookieBaker is a manager of long-lived (as opposed to session-lived) login cookies.

        This is a very convenient feature for a web app to have, but only conscious users who are responsible with their cookies should use it.
        This cookie management system is secure, as long as the connection to the service is end-to-end encrypted AND the user is responsible with their cookies.

        .. important::

            Upon creation of a new instance of CookieBaker, the cookie database file passed is pruned from all expired cookies, by calling the function :func:`CookieBaker.pruneCookieDB`.

        :param cookieStorageFile: The XML file used as a db for login cookies.
        :type cookieStorageFile: str.
        :param key: The secret key used to sign cookies.
        :type key: str.
        :param salt: Not a cryptographic salt per se, but it can be used to alter the signing key for cookies with different functions (unused).
        :type salt: str.
        :param cookieSize: The size in bytes of the cookie (default value is 33)
        :type cookieSize: int.

    '''

    def __init__(self, cookieStorageFile, key, salt=None, cookieSize=33):
        logger.debug("Initializing CookieBaker.")
        self.baker = JSONWebSignatureSerializer(key, salt=salt)
        self.cookieSize = cookieSize
        self.cookieStorageFile = cookieStorageFile
        if not os.path.isfile(cookieStorageFile):
            # if cookie storage file does not exist ==> create it
            try :
                with open(cookieStorageFile, 'w') as f:
                    ET.ElementTree(ET.Element('cookiedb')).write(f, encoding="unicode", method="html")
                logger.info('Created cookie database file ' + cookieStorageFile)
            except OSError as ose:
                logger.error('Error opening file ' + ose.filename + '\nDescription:\n' + ose.strerror)
        self.pruneCookieDB()

    def bake(self, userid):
        '''
            Generate and sign a new ``cookieVal``.

            This is the JSON Web Signature (JWS) of the dictionary type data in (pseudo-code):

            .. code-block:: json

                { "userid" : "base64(randomBytes)" }

            where randomBytes are ``cookieSize`` cryptographically secure random bytes (from ``urandom``).

            An example of such a JWS value is::

                eyJhbGciOiJIUzI1NiJ9.eyJ4Ijo0Mn0.ZdTn1YyGz9Yx5B5wNpWRL221G1WpVE5fPCPKNuc6UAo
            
            :param userid: The username of the user for which we generate the new cookie.
            :type userid: str.
            :returns: str -- The ``cookieVal`` for the new cookie, signed with the ``key``.

        '''
        logger.debug("Baking cookie for user %s", userid)
        cookieVal = { userid : b64encode(os.urandom(self.cookieSize)).decode('utf-8') }
        signedCookieVal = self.baker.dumps(cookieVal).decode('utf-8')
        return signedCookieVal
    def store(self, cookieVal, expiration=None):
        '''
            Store a ``cookieVal`` in the ``cookieStorageFile``.

            What is actually stored is the bcrypt salted hash of ``cookieVal``.
            Each user can have many long-lived valid cookies at once (e.g. they could access the web app from more than one device).
            To permit this, the cookie database is of the form:

            .. code-block:: xml

		<cookiedb>
		  <user username="alice">
		    <cookie expiration="1496055235">$2b$12$qOVm.1JJFgsCtYRWTanaIu/VcZK8b1CATxIVLzWv7oSKksrVGttee</cookie>
		    <cookie expiration="1496051234">$2b$12$NQYMCavxqcu80dDNFMadjOs/f6iWK1.HaWwEIyAG9Iy68bq7FeGpy</cookie>
		  </user>
		  <user username="chftyrol">
		    <cookie expiration="1496055777">$2b$12$4nmV2L38SP5XX7xDalM0B.ISJil/4wimUaMw13j6HtMhwDVnRT3ce</cookie>
		  </user>
		</cookiedb>

            :param cookieVal: a ``cookieVal`` to store, as produced by :func:`bake`.
            :type cookieVal: str.
            :raises: ``xml.etree.ElementTree.ParseError``, ``OSError``.
            :returns: bool -- ``True`` if operation is successful, ``False`` otherwise.

        '''
        logger.debug("Storing cookie.")
        res = False
        # hash with bcrypt the cookieVal
        hashedCookieVal = bcrypt.hashpw(cookieVal.encode('utf-8'), bcrypt.gensalt())
        assert len(self.baker.loads(cookieVal).keys()) == 1 
        logger.debug("bcrypt hash calculated.")
        # get the userid from cookieVal
        userid = list(self.baker.loads(cookieVal).keys())[0]
        # open the cookie storage 
        try :
            with open(self.cookieStorageFile, 'r+') as f:
                try :
                    logger.debug("Trying to open cookieDB.")
                    cookiedb = ET.parse(f).getroot()
                except ET.ParseError as err:
                    logger.error('Error parsing the XML document ' + self.cookieStorageFile + '\nmessage:\n' + err.msg)
                    return res
                # after reading file go to the beginning, so we can write if we need to.
                f.seek(0)
                # if userid corresponds to a <user> node with attribute username=userid:
                userElement = cookiedb.find("./user[@username='" + userid + "']")
                if userElement:
                    logger.debug("Found user %s in cookieDB.", userid)
                    if hashedCookieVal not in [ el.text for el in userElement.findall('cookie') ]:
                        # if user is aleady in the cookiedb and he/she doesn't already have this cookie, save it
                        newCookieEl = ET.Element('cookie')
                        newCookieEl.text = hashedCookieVal.decode('utf-8')
                        newCookieEl.set("expiration", str(expiration))
                        userElement.append(newCookieEl)

                        # delete the contents of the file.
                        #It is necessary because we are in mode 'r+', which does not truncate the file at opening, because it needs to read it
                        f.truncate()

                        ET.ElementTree(cookiedb).write(f, encoding="unicode", method="html")
                        res = True
                        logger.debug("Cookie is now stored in cookieDB!")
                        # duplicate cookies are ignored
                else :
                    # if the user has no cookies he/she must be inserted in the cookiedb
                    logger.debug("User %s does not have an entry in cookieDB. Creating it.", userid)
                    newUserEl = ET.Element('user')
                    newUserEl.set('username', userid)
                    cookiedb.append(newUserEl)
                    logger.debug("User %s was added to cookieDB.", userid)
                    # then we give the new user the cookie
                    newCookieEl = ET.SubElement(newUserEl, 'cookie', attrib={"expiration": str(expiration)})
                    newCookieEl.text = hashedCookieVal.decode('utf-8')
                    logger.debug("User %s was given a cookie.", userid)
                    # dump to file
                    f.truncate()
                    ET.ElementTree(cookiedb).write(f, encoding="unicode", method="html")
                    res = True
                    logger.debug("Cookie for user %s is now stored in cookieDB!", userid)
        except OSError as ose:
            logger.error('Error opening file ' + ose.filename + '\nDescription:\n' + ose.strerror)


        return res # success

    def check(self, cookieVal):
        '''
            Check cookie integrity and wether ``cookieVal`` corresponds to an entry in our ``cookieStorageFile``.

            Another advantage of using JWS (apart from serialization) is that it enables us to notice if a cookie has been tampered with.
            This is because cookies are signed with a key.

            This function first verifies that the cookie presented was signed by this application's key and that was not tampered with.
            If all goes well it checks if there exists a user with that ``cookieVal`` in the cookie database.

            :param cookieVal: the ``cookieVal`` to check. Typically it is a cookie sent by the client.
            :type cookieVal: str.
            :returns: str, NoneType -- the username of the owner of the cookie if the check succeeds or ``None`` if it fails.
            :raises: ``xml.etree.ElementTree.ParseError``, ``itsdangerous.BadSignature``, ``OSError``.
        '''
        logger.debug("Checking cookie for integrity...")
        res = None
        # get userid from cookieVal
        try :
            userid = list(self.baker.loads(cookieVal).keys())[0]
            logger.debug("Cookie signature verified!")
        except BadSignature as err:
            logger.warning("Cookie has been tampered with! Abort!")
            return res
        try :
            logger.debug("Checking if cookie is in cookieDB...")
            with open(self.cookieStorageFile, 'r') as f:
                try :
                    cookiedb = ET.parse(f).getroot()
                except ET.ParseError as err:
                    logger.error('Error parsing the XML document ' + self.cookieStorageFile + '\nmessage:\n' + err.msg)
                # if the user is found in the cookiedb we examine his/her cookies for a match
                userElement = cookiedb.find("./user[@username='" + userid + "']")
                if userElement:
                    for c in [ el.text for el in userElement.findall('cookie') ]:
                        # cycle over the cookies in the array val, and look for a match.
                        if bcrypt.checkpw(cookieVal.encode('utf-8'), c.encode('utf-8')):
                            res = userid
                            logger.debug("Cookie was found in cookieDB!")
                            break
        except OSError as ose:
            logger.error('Error opening file ' + ose.filename + '\nDescription:\n' + ose.strerror)
 
        if not res:
            logger.debug("Cookie not found in cookieDB!")

        return res
    def delete(self, cookieVal):
        '''
            Remove a cookie from the cookie database, if it is there.

            :param cookieVal: the ``cookieVal`` to delete.
            :type cookieVal: str.
            :returns: bool -- ``True`` if deletion occurred successfully, ``False`` otherwise.
            :raises: ``xml.etree.ElementTree.ParseError``, ``OSError``.
        '''
        logger.debug("Deleting cookie from cookieDB.")
        res = False;
        # get userid from cookieVal
        userid = list(self.baker.loads(cookieVal).keys())[0]
        try :
            with open(self.cookieStorageFile, 'r+') as f:
                try :
                    cookiedb = ET.parse(f).getroot()
                except ET.ParseError as err:
                    logger.error('Error parsing the XML document ' + self.cookieStorageFile + '\nmessage:\n' + err.msg)
                    return res
                # after reading file go to the beginning, so we can write if we need to.
                f.seek(0)

                userElement = cookiedb.find("./user[@username='" + userid + "']")
                if userElement:
                    for c in [ el.text for el in userElement.findall('cookie') ]:
                        # cycle over the cookies in the array val, and look for a match.
                        if bcrypt.checkpw(cookieVal.encode('utf-8'), c.encode('utf-8')):
                            # we found a match, delete it from cookiedb and dump to file.
                            # must do this, XPath support in stock xml module is very limited...
                            for el in userElement.findall("cookie"):
                                if el.text == c:
                                    condemnedEl = el
                                    break
                            userElement.remove(condemnedEl)
                            f.truncate()
                            ET.ElementTree(cookiedb).write(f, encoding="unicode", method="html")
                            res = True
                            logger.debug("Cookie deleted successfully!")
        except OSError as ose:
            logger.error('Error opening file ' + ose.filename + '\nDescription:\n' + ose.strerror)

        if not res:
            logger.debug("Cookie not in cookieDB: ignoring...")

        return res
    def pruneCookieDB(self):
        '''
            Remove all expired cookies from the cookie database.

            This is called automatically when a new CookieBaker is created, to ensure that the cookie database does not fill up with useless data.

            :returns: bool -- ``True`` if cookies were pruned, ``False`` otherwise.
            :raises: ``xml.etree.ElementTree.ParseError``, ``OSError``.
        '''
        logger.debug("Pruning cookieDB.")
        modified = 0
        try :
            with open(self.cookieStorageFile, 'r+') as f:
                try :
                    cookiedb = ET.parse(f).getroot()
                except ET.ParseError as err:
                    logger.error('Error parsing the XML document ' + self.cookieStorageFile + '\nmessage:\n' + err.msg)
                    return res
                # after reading file go to the beginning, so we can write if we need to.
                f.seek(0)
                # look for expired cookies
                for it in cookiedb.findall(".//cookie"):
                    expTimestamp = it.get("expiration")
                    if int(expTimestamp) < int(datetime.datetime.now().timestamp()):
                        # if found, walk the db again from root. 
                        # ElementTree sucks ass: you can only remove an element using an instance of its direct parent, which you cannot access from the element itself.
                        for user in cookiedb.findall("./user"):
                            for cookie in user.findall("./cookie"):
                                if cookie == it:
                                    user.remove(it)
                                    modified += 1
                                    break
                if modified:
                    f.truncate()
                    ET.ElementTree(cookiedb).write(f, encoding="unicode", method="html")
                    logger.debug("CookieDB was pruned! %d cookies pruned.", modified)

        except OSError as ose:
            logger.error('Error opening file ' + ose.filename + '\nDescription:\n' + ose.strerror)

        return modified

if __name__ == "__main__":
    print("This module is not meant to be run on its own.")
    quit()
