#!/usr/bin/python3

import os
import sys

import argparse

parser = argparse.ArgumentParser(description=" Jans LDAP to RDBM migrator script")

parser.add_argument('-rdbm-user', help="RDBM username",  required = True)
parser.add_argument('-rdbm-password', help="RDBM password",  required = True)
parser.add_argument('-rdbm-port', help="RDBM port", type=int)
parser.add_argument('-rdbm-db', help="RDBM database",  required = True)
parser.add_argument('-rdbm-host', help="RDBM host",  required = True)
parser.add_argument('-in-ldif-fpath', help="Input ldif file path",  required = True)
parser.add_argument('-in-json-fpath', help="Input json file path",  required = True)
parser.add_argument('-jans-setup-dpath', help="Input json file path", default="/opt/jans/jans-setup", required = False)

argsp = parser.parse_args()
rdbm_config_params = ('rdbm_user', 'rdbm_password', 'rdbm_host', 'rdbm_db', 'rdbm_host', 'rdbm_port', 'in_ldif_fpath', 'in_json_fpath', 'jans_setup_dpath')
argsp_dict = { a: getattr(argsp, a) for a in rdbm_config_params }
argsp_dict['rdbm_type'] = 'pgsql'

if os.path.exists(argsp_dict['jans_setup_dpath']):
    sys.path.insert(0, argsp_dict['jans_setup_dpath'])

import warnings
warnings.filterwarnings("ignore")

import pydevd
import debugpy

import json

from setup_app import paths

from setup_app.utils import base

base.current_app.profile = 'disa-stig'

from setup_app.config import Config
from setup_app.utils.setup_utils import SetupUtils
from setup_app.utils.properties_utils import PropertiesUtils
from setup_app.utils.ldif_utils import myLdifParser
from setup_app.utils.db_utils import dbUtils

debugpy.listen(("0.0.0.0",5678));
debugpy.wait_for_client();


def main():

    debugpy.breakpoint();

    base.argsp = argsp

    base.argsp.opendj_keystore_type = "bcfks"
    base.argsp.j = True

    Config.init(paths.INSTALL_DIR)

    for x in Config.mapping_locations.keys():
        Config.mapping_locations[x] = 'rdbm'

    Config.installed_instance = True

    print('Config.mapping_locations = {}'.format(Config.mapping_locations))

    Config.rdbm_type = argsp_dict['rdbm_type']
    Config.rdbm_host = argsp_dict['rdbm_host']
    Config.rdbm_port = argsp_dict['rdbm_port']
    Config.rdbm_db = argsp_dict['rdbm_db']
    Config.rdbm_user = argsp_dict['rdbm_user']
    Config.rdbm_password = argsp_dict['rdbm_password']

    print('Config.rdbm_type = {}'.format(Config.rdbm_type))
    print('Config.rdbm_host = {}'.format(Config.rdbm_host))
    print('Config.rdbm_port = {}'.format(Config.rdbm_port))
    print('Config.rdbm_db   = {}'.format(Config.rdbm_db))
    print('Config.rdbm_user = {}'.format(Config.rdbm_user))
    print('Config.rdbm_password = {}'.format(Config.rdbm_password))

    print('in_json_fpath = {}'.format(argsp_dict['in_json_fpath']))
    print('in_ldif_fpath = {}'.format(argsp_dict['in_ldif_fpath']))

    schema_ = base.readJsonFile(argsp_dict['in_json_fpath'])
    jans_attributes = schema_.get('attributeTypes', [])

    print('jans_attributes = {}'.format(jans_attributes))
    
    in_json_files = []
    in_json_files.append(argsp_dict['in_json_fpath'])

    debugpy.breakpoint();

    print('dbUtils.bind() ------------------------ >>')
    dbUtils.bind()
    print('dbUtils.bind() ------------------------ <<')

    print('create_tables ------------------------ >>')
    create_tables(in_json_files)
    print('create_tables ------------------------ <<')

    debugpy.breakpoint();

    print('dbUtils.import_ldif ------------------------ >>')
    dbUtils.import_ldif([argsp_dict['in_ldif_fpath']])
    print('dbUtils.import_ldif ------------------------ <<')
    
    print('return')

    return

def create_tables(jans_schema_files):
    print("Creating tables for {}".format(jans_schema_files))
    tables = []
    all_schema = {}
    all_attribs = {}
    column_add = 'COLUMN ' if Config.rdbm_type == 'spanner' else ''
    alter_table_sql_cmd = 'ALTER TABLE %s{}%s ADD %s{};' % (get_qchar(), get_qchar(), column_add)

    debugpy.breakpoint();

    for jans_schema_fn in jans_schema_files:
        jans_schema = base.readJsonFile(jans_schema_fn)
        for obj in jans_schema['objectClasses']:
            all_schema[obj['names'][0]] = obj
        for attr in jans_schema['attributeTypes']:
            all_attribs[attr['names'][0]] = attr

    debugpy.breakpoint();

    subtable_attrs = {}
    for stbl in dbUtils.sub_tables.get(Config.rdbm_type):
        subtable_attrs[stbl] = [ scol[0] for scol in dbUtils.sub_tables[Config.rdbm_type][stbl] ]

    debugpy.breakpoint();

    for obj_name in all_schema:
        obj = all_schema[obj_name]

        if obj.get('sql', {}).get('ignore'):
            continue

        sql_tbl_name = obj['names'][0]
        sql_tbl_cols = []

        attr_list = obj['may']
        if 'sql' in obj:
            attr_list += obj['sql'].get('include',[])
            if 'includeObjectClass' in obj['sql']:
                for incobjcls in obj['sql']['includeObjectClass']:
                    attr_list += all_schema[incobjcls]['may']

        for s in obj['sup']:
            if s == 'top':
                continue
            attr_list += all_schema[s]['may']

        cols_ =[]
        for attrname in attr_list:
            if attrname in cols_:
                continue

            if attrname in subtable_attrs.get(sql_tbl_name, []):
                continue

            cols_.append(attrname)
            col_def = get_col_def(attrname, sql_tbl_name) 
            sql_tbl_cols.append(col_def)

        if not dbUtils.table_exists(sql_tbl_name):
            doc_id_type = get_sql_col_type('doc_id', sql_tbl_name)
            if Config.rdbm_type == 'pgsql':
                sql_cmd = 'CREATE TABLE "{}" (doc_id {} NOT NULL UNIQUE, "objectClass" VARCHAR(48), dn VARCHAR(128), {}, PRIMARY KEY (doc_id));'.format(sql_tbl_name, doc_id_type, ', '.join(sql_tbl_cols))
            elif Config.rdbm_type == 'spanner':
                sql_cmd = 'CREATE TABLE `{}` (`doc_id` {} NOT NULL, `objectClass` STRING(48), dn STRING(128), {}) PRIMARY KEY (`doc_id`)'.format(sql_tbl_name, doc_id_type, ', '.join(sql_tbl_cols))
            else:
                sql_cmd = 'CREATE TABLE `{}` (`doc_id` {} NOT NULL UNIQUE, `objectClass` VARCHAR(48), dn VARCHAR(128), {}, PRIMARY KEY (`doc_id`));'.format(sql_tbl_name, doc_id_type, ', '.join(sql_tbl_cols))
            dbUtils.exec_rdbm_query(sql_cmd)
            tables.append(sql_cmd)

    for attrname in all_attribs:
        attr = all_attribs[attrname]
        if attr.get('sql', {}).get('add_table'):
            col_def = get_col_def(attrname, sql_tbl_name)
            sql_cmd = alter_table_sql_cmd.format(attr['sql']['add_table'], col_def)

            if Config.rdbm_type == 'spanner':
                req = dbUtils.spanner_client.exec_sql(sql_cmd.strip(';'))
            else:
                dbUtils.exec_rdbm_query(sql_cmd)
            tables.append(sql_cmd)

    print("tables = {}".format(tables))

    write_file(os.path.join('/tmp', 'jans_tables.sql'), '\n'.join(tables))

def get_col_def(attrname, sql_tbl_name):
    data_type = get_sql_col_type(attrname, sql_tbl_name)
    col_def = '{0}{1}{0} {2}'.format(get_qchar(), attrname, data_type)
    if Config.rdbm_type == 'mysql' and data_type == 'JSON':
        col_def += ' comment "json"'
    return col_def

def get_sql_col_type(attrname, table=None):

    if attrname in dbUtils.sql_data_types:
        type_ = dbUtils.sql_data_types[attrname].get(Config.rdbm_type) or dbUtils.sql_data_types[attrname]['mysql']
        if table in type_.get('tables', {}):
            type_ = type_['tables'][table]
        if 'size' in type_:
            data_type = '{}({})'.format(type_['type'], type_['size'])
        else:
            data_type = type_['type']
    else:
        attr_syntax = dbUtils.get_attr_syntax(attrname)
        type_ = dbUtils.ldap_sql_data_type_mapping[attr_syntax].get(Config.rdbm_type) or dbUtils.ldap_sql_data_type_mapping[attr_syntax]['mysql']

        char_type = 'STRING' if Config.rdbm_type == 'spanner' else 'VARCHAR'

        if type_['type'] in char_type:
            if type_['size'] <= 127:
                data_type = '{}({})'.format(char_type, type_['size'])
            elif type_['size'] <= 255:
                data_type = 'TINYTEXT' if Config.rdbm_type == 'mysql' else 'TEXT'
            else:
                data_type = 'TEXT'
        else:
            data_type = type_['type']

    if data_type == 'TEXT' and Config.rdbm_type == 'spanner':
        data_type = 'STRING(MAX)'

    return data_type

def write_file(outFilePath, text):
    print("Writing file %s" % outFilePath)

    dir_name = os.path.dirname(outFilePath)
    if not os.path.exists(dir_name):
        run([paths.cmd_mkdir, '-p', dir_name])

    inFilePathText = None
    try:
        with open(outFilePath, 'w') as w:
            w.write(text)
    except:
        print("Error writing %s" % inFilePathText)

    return inFilePathText

def get_qchar():
    return '`' if Config.rdbm_type in ('mysql', 'spanner') else '"'

def run(*args, **kwargs):
    if kwargs:
        return base.run(*args, **kwargs)
    else:
        return base.run(*args)

if __name__ == "__main__":
    debugpy.breakpoint();
    base.logIt('jans_setup: main()')
    main()
