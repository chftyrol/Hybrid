#!/usr/bin/python3

'''
    This file is part of Hybrid.

    Hybrid is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Hybrid is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with Hybrid.  If not, see <http://www.gnu.org/licenses/>.
'''

import json
import sys
import getpass
import hashlib
import bcrypt

LOGIN_DB_FILE = sys.path[0] + '/db/login.json'
SALT_CONST = '-hybrid_server'

def check(username, storedpw):
    thesalt = username + SALT_CONST
    oldpass_hashed = hashlib.sha256((getpass.getpass('Enter the password for user ' + username + ': ') + thesalt).encode('utf-8')).hexdigest()
    return bcrypt.checkpw(oldpass_hashed.encode('utf-8'), storedpw.encode('utf-8'))

def mkhash(username):
    thesalt = username + SALT_CONST
    newpass_hashed = hashlib.sha256((getpass.getpass('Enter the NEW password for user ' + username + ': ') + thesalt).encode('utf-8')).hexdigest()
    newpass_hashed_again = hashlib.sha256((getpass.getpass('Once more, just to be sure: ') + thesalt).encode('utf-8')).hexdigest()
    if newpass_hashed == newpass_hashed_again:
        newpass_hashed = bcrypt.hashpw(newpass_hashed.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return newpass_hashed
    else :
        print('Error: Passwords do not match!')
        quit()

def dump(db):
    res = False
    try :
        with open(LOGIN_DB_FILE, 'w') as f:
            try :
                json.dump(db, f)
                res = True
            except json.JSONDecodeError as err:
                print('Error dumping to the JSON document ' + LOGIN_DB_FILE + '\nmessage:\n' + err.msg)
    except OSError as e:
        print('Error opening file ' + e.filename + '\ndescription:\n' + e.strerror)
    return res

if __name__ == "__main__":
    db_changed = False
    try :
        with open(LOGIN_DB_FILE, 'r') as f:
            try :
                db = json.load(f)
            except json.JSONDecodeError as err:
                print('Error parsing the JSON document ' + LOGIN_DB_FILE + '\nmessage:\n' + err.msg)
                quit()
        username = input('Enter username (or just press [Enter] for a list of accounts): ')
        if username == "":
            print("The current users have accounts:")
            for k in db:
                print(k)
            quit()
        if not username in db:
            choice = input(username + ' will be given a new account. Proceed? [y/n] ')
            if choice.lower() == 'y':
                db[username] = mkhash(username)
                db_changed = True
        else :
            print("User " + username + " already has an account")
            choice = input('Change password for user ' + username + '? [y/n] ')
            if choice.lower() == "y":
                allowed = False
                attempts = 0
                while not allowed:
                    if attempts > 2 :
                        print('Too many attempts! Quitting...')
                        quit()
                    allowed = check(username, db[username])
                    attempts += 1
                if allowed:
                    db[username] = mkhash(username)
                    db_changed = True
            elif choice.lower() == "n":
                choice = input('Do you wish to delete user ' + username + '? [y/n] ')
                if choice.lower() == 'y':
                    choice = input('Are you sure? [y/n] ')
                    if choice.lower() == 'y':
                        attempts = 0
                        allowed = False
                        while not allowed:
                            if attempts > 2 :
                                print('Too many attempts! Quitting...')
                                quit()
                            allowed = check(username, db[username])
                            attempts += 1
                        if allowed:
                            del db[username]
                            db_changed = True
                            print('User ' + username + ' was deleted!')
            else :
                quit()
        if db_changed:
            if dump(db):
                print('Password db updated successfully!')
    except OSError as e:
        print('Error opening file ' + e.filename + '\ndescription:\n' + e.strerror)
    except KeyboardInterrupt :
        quit()
