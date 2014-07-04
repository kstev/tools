#!/usr/bin/env python
#

import os
from sys import exit
import pyrax
import argparse
import getpass

def create_creds(cfile):
    if 'y' in str(raw_input('Would you like to enter Rackspace public cloud credentials? (y/n) ')).lower()[0]:
        u_name = str(raw_input('Enter your Cloud Files username '))
        api_key = str(getpass.getpass('Enter your Cloud Files API key '))
        with open(cfile, 'w+') as f:
            f.write('[rackspace_cloud]')
            f.write('\nusername = ' + u_name)
            f.write('\napi_key = ' + api_key)
            f.write('\n\n')
    if 'y' in str(raw_input('Would you like to enter private Keystone credentials? (y/n) ')).lower()[0]:
        u_name = str(raw_input('Enter your Keystone username '))
        ten_id = str(raw_input('Enter your Keystone project ID '))
        u_pass = str(getpass.getpass('Enter your user password '))
        if os.path.exists(cfile):
            o_mode = 'a'
        else:
            o_mode = 'w+'
        with open(cfile, o_mode) as f:
            f.write('[keystone]')
            f.write('\nusername = ' + u_name)
            f.write('\npassword = ' + u_pass)
            f.write('\ntenant_id = ' + ten_id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--identity', help='Identity type (rackspace / keystone) DEFAULT=rackspace', action='store', default='rackspace', type=str)
    parser.add_argument('--container', help='Container to upload objects to DEFAULT=cfpush_container', action='store', default='cfpush_container', type=str)
    parser.add_argument('--files', help='File (full path) to upload', action='append')
    parser.add_argument('--folder', help='Folder (full path) to upload', type=str)
    parser.add_argument('--links', help='CDN-Enable the container and list links to all objects', action='store_true')
    args = parser.parse_args()

    pyrax.set_setting("identity_type", args.identity)
    creds_file = os.getenv('HOME') + '/.rax_rc'
    try:
        pyrax.set_credential_file(creds_file)
    except:
        create_creds(creds_file)
    cf = pyrax.cloudfiles

    try:
        cont = cf.get_container(args.container)
        if args.links:
            cont.make_public(ttl=1200)
            cont_uri = cont.cdn_uri
    except pyrax.exceptions.NoSuchContainer:
        print('Creating container ' + args.container)
        cont = cf.create_container(args.container)
        if args.links:
            cont.make_public(ttl=1200)
            cont_uri = cont.cdn_uri

    if args.folder:
        print('Syncing folder %s to Cloud Files container %s' % (args.folder, args.container))
        cf.sync_folder_to_container(args.folder, cont)
        objects = cont.get_objects()
        print('Objects uploaded')
        if args.links:
            for obj in objects:
                print(cont_uri + '/' + obj.name)
        else:
            for obj in objects:
                print(obj.name)

    if args.files:
        f_count = 0
        obj = []
        for i in args.files:
#            obj[f_count] = cf.store_object(cont, i, content)
            pass
