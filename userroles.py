#!/usr/bin/env python
#

# Displays roles for each user by project
# Outputs to console and to spreadsheet

from keystoneclient.v2_0 import client
import os
import sys
import xlwt

osauthurl = os.getenv('OS_AUTH_URL')
osusername = os.getenv('OS_USERNAME')
ospassword = os.getenv('OS_PASSWORD')
ostenantname = os.getenv('OS_TENANT_NAME')
keystone = client.Client(auth_url=osauthurl, username=osusername, password=ospassword, project_name=ostenantname)
projects = keystone.tenants.list()
projectlist = []
iterproject = 0
for x in projects:
    projectlist.append({})
    projectlist[iterproject]['name'] = str(x.name).strip()
    projectlist[iterproject]['id'] = str(x.id).strip()
    projectlist[iterproject]['users'] = []
    for i in x.list_users():
        userid = { 'username': i.username, 'userid': i.id }
        projectlist[iterproject]['users'].append(userid)
    iterproject += 1

book = xlwt.Workbook(encoding='utf-8')

for x in projectlist:
    print('======================')
    print('-= PROJECT : %s =-' % (x['name']))
    sheet = book.add_sheet(x['name'])
    row_num = 0
    column_num = 0
    for i in x['users']:
        sheet.write(row_num, column_num, i['username']); column_num += 1
        for a in keystone.roles.roles_for_user(i['userid'], tenant=x['id']):
            sheet.write(row_num, column_num, a.name); column_num += 1
            print i['username'], '\t', a.name
        column_num = 0
        row_num += 1
    print('======================')

book.save('role_list.xls')
