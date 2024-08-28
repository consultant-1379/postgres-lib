#!/bin/bash

if ! python3 -c 'import sys; assert sys.version_info >= (3,0)' > /dev/null 2>&1;
then
  py_version=/usr/bin/python
else
  py_version=/usr/bin/python3
fi
clear

$py_version -W ignore /opt/ericsson/postgres/pglib/admin/document_db_admin.py
