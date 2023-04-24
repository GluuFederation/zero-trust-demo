#!/usr/bin/python

import pydevd
import debugpy

import sys
import os
import os.path
import json
import traceback
import time
import argparse
import tempfile
import zipfile
import shutil
import glob

from urllib.parse import urlparse
from urllib.request import urlretrieve
from urllib import request
from pathlib import Path

debugpy.listen(("0.0.0.0", 5678));
debugpy.wait_for_client();

debugpy.breakpoint();

class SetupCasa:
# inherited from JettyInstaller
# inheritance will be defined later (after creating of an instance)

    casa_python_libs = ['Casa.py', 'casa-external_fido2.py', 'casa-external_otp.py', 'casa-external_super_gluu.py', 'casa-external_twilio_sms.py']

    casa_client_id_prefix = '3000.'
    service_name = 'casa'

    def __init__(self, install_dpath):

        self.casa_web_resources_fpath = os.path.join(casa_dist_dpath, casa_web_resources_fname)
        self.casa_war_fpath = os.path.join(casa_dist_dpath, 'casa.war')
        self.casa_config_fpath = os.path.join(casa_dist_dpath, 'casa-config.jar')

        self.twillo_fpath = os.path.join(casa_dist_dpath, 'twilio.jar')
        self.fido2_client_fpath = os.path.join(jans_dist_dpath, 'jans-fido2-client.jar')

        self.py_lib_dpath = os.path.join(Config.jansOptPythonFolder, 'libs')

        self.casa_script_fpath = os.path.join(casa_dist_dpath, 'pylib', SetupCasa.casa_python_libs[0])

        self.dwnl_files = [
                (os.path.join(app_versions['BASE_SERVER_CASA'], '_out/_extras/casa_web_resources.xml'), self.casa_web_resources_fpath),
                (os.path.join(app_versions['BASE_SERVER_CASA'], '_out/casa-config-5.0.0-12.jar'), self.casa_config_fpath),
                (os.path.join(downloads.base.current_app.app_info['TWILIO_MAVEN'], '{0}/twilio-{0}.jar'.format(downloads.base.current_app.app_info['TWILIO_VERSION'])), self.twillo_fpath),
                (os.path.join(app_versions['BASE_SERVER_JANS'], '_out/Fido2-Client.jar'), self.fido2_client_fpath)
            ]

#        self.dwnl_files = [
#                ('https://raw.githubusercontent.com/GluuFederation/flex/main/casa/extras/casa_web_resources.xml', self.casa_web_resources_fpath),
#                (os.path.join(app_versions['GLUU_MAVEN'], 'maven/org/gluu/casa-config/{0}/casa-config-{0}.jar'.format(argsp.casa_version)), self.casa_config_fpath),
#                (os.path.join(base.current_app.app_info['TWILIO_MAVEN'], '{0}/twilio-{0}.jar'.format(base.current_app.app_info['TWILIO_VERSION'])), self.twillo_fpath),
#                (os.path.join(base.current_app.app_info['JANS_MAVEN'], 'maven/io/jans/jans-fido2-client/{0}{1}/jans-fido2-client-{0}{1}.jar'.format(base.current_app.app_info['JANS_APP_VERSION'], base.current_app.app_info['JANS_BUILD'])), self.fido2_client_fpath),
#            ]

        if base.argsp.profile == DISA_STIG_PROFILE:
            self.dwnl_files.append((os.path.join(app_versions['BASE_SERVER_CASA'], '_out/casa-fips-5.0.0-12.war'), self.casa_war_fpath))
#            self.dwnl_files.append((os.path.join(app_versions['GLUU_MAVEN'], 'maven/org/gluu/casa/{0}/casa-fips-{0}.war'.format(argsp.casa_version)), self.casa_war_fpath))

        else:
            self.dwnl_files.append((os.path.join(app_versions['BASE_SERVER_CASA'], '_out/casa-5.0.0-12.war'), self.casa_war_fpath))
#            self.dwnl_files.append((os.path.join(app_versions['GLUU_MAVEN'], 'maven/org/gluu/casa/{0}/casa-{0}.war'.format(argsp.casa_version)), self.casa_war_fpath))

        self.jans_auth_dpath = os.path.join(Config.jetty_base, jans_auth_installer.service_name)
        self.jans_auth_custom_lib_dpath = os.path.join(self.jans_auth_dpath, 'custom/libs')

        self.source_dpath = cur_dpath

        self.output_dpath = os.path.join(self.source_dpath, 'output')

        Config.templateRenderingDict['admin_ui_apache_root'] = os.path.join(httpd_installer.server_root, 'admin')
        Config.templateRenderingDict['casa_web_port'] = '8080'

        self.source_files = [(self.casa_war_fpath,)]

    def download_files(self):

        for dwnl_url, target_fpath in self.dwnl_files:
            if not os.path.exists(target_fpath):
                target_dpath = os.path.dirname(os.path.realpath(target_fpath))
                if not os.path.exists(target_dpath):
                    os.makedirs(target_dpath)
                print("Downloading {0} to {1}".format(dwnl_url, target_fpath))
                download_tries = 1
                while download_tries < 4:
                    try:
                        urlretrieve(dwnl_url, target_fpath)
                        print("Download size: {0} bytes".format(os.path.getsize(target_fpath)))
                        time.sleep(0.1)
                    except:
                        print("Error downloading {0}. Download will be re-tried once more".format(dwnl_url))
                        download_tries += 1
                        time.sleep(1)
                    else:
                        break

    def install_casa(self):
    
        print ("Installing Casa")

        debugpy.breakpoint();

        jans_auth_web_app_xml = jans_auth_installer.readFile(jans_auth_installer.web_app_xml_fn)

        if os.path.basename(self.casa_config_fpath) not in jans_auth_web_app_xml:
            print("Adding casa config to jans-auth")
            self.copyFile(self.casa_config_fpath, self.jans_auth_custom_lib_dpath)
            casa_config_class_fpath = os.path.join(self.jans_auth_custom_lib_dpath, os.path.basename(self.casa_config_fpath))
            jans_auth_installer.add_extra_class(casa_config_class_fpath)

        if os.path.basename(self.twillo_fpath) not in jans_auth_web_app_xml:
            print("Adding twillo to jans-auth")
            self.copyFile(self.twillo_fpath, self.jans_auth_custom_lib_dpath)
            twillo_config_class_fpath = os.path.join(self.jans_auth_custom_lib_dpath, os.path.basename(self.twillo_fpath))
            jans_auth_installer.add_extra_class(twillo_config_class_fpath)

        if os.path.basename(self.fido2_client_fpath) not in jans_auth_web_app_xml:
            print("Adding Fido2 Client lib to jans-auth")
            self.copyFile(self.fido2_client_fpath, self.jans_auth_custom_lib_dpath)
            fido2_class_fpath = os.path.join(self.jans_auth_custom_lib_dpath, os.path.basename(self.fido2_client_fpath))
            jans_auth_installer.add_extra_class(fido2_class_fpath)

        # copy casa scripts
        if not os.path.exists(self.py_lib_dpath):
            os.makedirs(self.py_lib_dpath)
        for fpath in glob.glob(os.path.join(casa_dist_dpath, 'pylib/*.py')):
            print("Copying", fpath, "to", self.py_lib_dpath)
            self.copyFile(fpath, self.py_lib_dpath)

        if not os.path.exists(self.output_dpath):
            os.makedirs(self.output_dpath)

        self.run([paths.cmd_chown, '-R', '{0}:{0}'.format(Config.jetty_user), self.py_lib_dpath])

        # prepare casa scipt ldif
        casa_auth_script_fpath = os.path.join(casa_dist_templates_dpath, 'casa_person_authentication_script.ldif')
        base64_script_file = self.generate_base64_file(self.casa_script_fpath, 1)
        Config.templateRenderingDict['casa_person_authentication_script'] = base64_script_file
        self.renderTemplateInOut(casa_auth_script_fpath, casa_dist_templates_dpath, self.output_dpath)

        Config.templateRenderingDict['casa_redirect_uri'] = 'https://{}/casa'.format(Config.hostname)
        Config.templateRenderingDict['casa_redirect_logout_uri'] = 'https://{}/casa/bye.zul'.format(Config.hostname)
        Config.templateRenderingDict['casa_frontchannel_logout_uri'] = 'https://{}/casa/autologout'.format(Config.hostname)

        self.casa_client_fpath = os.path.join(casa_dist_templates_dpath, 'casa_client.ldif')
        self.casa_config_fpath = os.path.join(casa_dist_templates_dpath, 'casa_config.ldif')

        if not is_string_blank(base.argsp.casa_client_id):
            setattr(Config, 'casa_client_id', base.argsp.casa_client_id)

        if not is_string_blank(base.argsp.casa_client_pw):
            setattr(Config, 'casa_client_pw', base.argsp.casa_client_pw)

        self.check_clients([('casa_client_id', SetupCasa.casa_client_id_prefix)])

        if not Config.get('casa_client_encoded_pw'):
            Config.casa_client_encoded_pw = jans_auth_installer.obscure(Config.casa_client_pw)

        print()
        print("Casa Client ID:", Config.casa_client_id)
        print("Casa Client Secret:", Config.casa_client_pw)
        print()

        print("Importing LDIF Files")

        self.renderTemplateInOut(self.casa_client_fpath, casa_dist_templates_dpath, self.output_dpath)
        self.renderTemplateInOut(self.casa_config_fpath, casa_dist_templates_dpath, self.output_dpath)
        self.dbUtils.import_ldif([
                os.path.join(self.output_dpath, os.path.basename(self.casa_client_fpath)),
                os.path.join(self.output_dpath, os.path.basename(self.casa_config_fpath)),
                os.path.join(self.output_dpath, os.path.basename(casa_auth_script_fpath)),
                ])

        Config.installCasa = True

        self.copyFile(os.path.join(casa_dist_templates_dpath, 'casa.default'), os.path.join(Config.templateFolder, 'jetty/casa'))

        self.jetty_app_configuration[SetupCasa.service_name] = {
                    "memory": {
                        "max_allowed_mb": 1024,
                        "metaspace_mb": 128,
                        "jvm_heap_ration": 0.7,
                        "ratio": 0.1
                        },
                    "jetty": {
                        "modules": "server,deploy,resources,http,http-forwarded,console-capture,jsp,cdi-decorate"
                    },
                    "installed": False,
                    "name": SetupCasa.service_name
                }

        print("Calculating application memory")

        installedComponents = []

        # Jetty apps
        for config_var, service in [('installOxAuth', 'jans-auth'),
                                    ('installScimServer', 'jans-scim'),
                                    ('installFido2', 'jans-fido2'),
                                    ('installConfigApi', 'jans-config-api'),
                                    ('installEleven', 'jans-eleven'),
                                    ('installCasa', SetupCasa.service_name),
                                    ]:

            if Config.get(config_var) and service in self.jetty_app_configuration:
                installedComponents.append(self.jetty_app_configuration[service])

        self.calculate_aplications_memory(Config.application_max_ram, self.jetty_app_configuration, installedComponents)

        print("Deploying casa as Jetty application")
        self.installJettyService(self.jetty_app_configuration[SetupCasa.service_name], True)
        self.copyFile(os.path.join(casa_dist_templates_dpath, 'casa.service'), '/etc/systemd/system')
        jetty_service_dpath = os.path.join(Config.jetty_base, SetupCasa.service_name)
        jetty_service_webapps_dpath = os.path.join(jetty_service_dpath, 'webapps')

        self.run([paths.cmd_mkdir, '-p', os.path.join(jetty_service_dpath, 'static')])
        self.run([paths.cmd_mkdir, '-p', os.path.join(jetty_service_dpath, 'plugins')])
        self.copyFile(self.casa_war_fpath, jetty_service_webapps_dpath)
        self.copyFile(self.casa_web_resources_fpath, jetty_service_webapps_dpath)
        jans_auth_installer.chown(jetty_service_dpath, Config.jetty_user, Config.jetty_group, recursive=True)
        jans_auth_installer.chown(self.jans_auth_custom_lib_dpath, Config.jetty_user, Config.jetty_group, recursive=True)

        self.add_apache_directive('<Location /casa>', 'casa_apache_directive')

        self.enable()

    def add_apache_directive(self, check_str, template):

        debugpy.breakpoint();

        print("Updating apache configuration")
        apache_directive_template_text = self.readFile(os.path.join(casa_dist_templates_dpath, template))
        apache_directive_text = self.fomatWithDict(apache_directive_template_text, Config.templateRenderingDict)

        https_jans_text = self.readFile(httpd_installer.https_jans_fn)

        if check_str not in https_jans_text:
            https_jans_list = https_jans_text.splitlines()
            n = 0

            for i, l in enumerate(https_jans_list):
                if l.strip() == '</LocationMatch>':
                    n = i

            https_jans_list.insert(n+1, '\n' + apache_directive_text + '\n')
            self.writeFile(httpd_installer.https_jans_fn, '\n'.join(https_jans_list))

        self.enable_apache_mod_dir()

    def enable_apache_mod_dir(self):

        debugpy.breakpoint();

        # Enable mod_dir for apache

        cmd_a2enmod = shutil.which('a2enmod')

        if base.clone_type == 'deb':
            httpd_installer.run([cmd_a2enmod, 'dir'])

        elif base.os_type == 'suse':
            httpd_installer.run([cmd_a2enmod, 'dir'])
            cmd_a2enflag = shutil.which('a2enflag')
            httpd_installer.run([cmd_a2enflag, 'SSL'])

        else:
            base_mod_path = Path('/etc/httpd/conf.modules.d/00-base.conf')
            mod_load_content = base_mod_path.read_text().splitlines()
            modified = False

            for i, l in enumerate(mod_load_content[:]):
                ls = l.strip()
                if ls.startswith('#') and ls.endswith('mod_dir.so'):
                    mod_load_content[i] = ls.lstrip('#')
                    modified = True

            if modified:
                base_mod_path.write_text('\n'.join(mod_load_content))

    def remove_apache_directive(self, directive):

        debugpy.breakpoint();

        https_jans_current = self.readFile(httpd_installer.https_jans_fn)
        tmp_ = directive.lstrip('<').rstrip('>').strip()
        dir_name, dir_arg = tmp_.split()
        dir_fname = '/'+dir_name

        https_jans_list = []
        append_c = 2

        for l in https_jans_current.splitlines():
            if dir_name in l and dir_arg in l:
                append_c = 0
            elif append_c == 0 and dir_fname in l:
                append_c = 1

            if append_c > 1:
                https_jans_list.append(l)

            if append_c == 1:
                append_c = 2

        self.writeFile(httpd_installer.https_jans_fn, '\n'.join(https_jans_list))

    def uninstall_casa(self):

        debugpy.breakpoint();

        print("Uninstalling Gluu Casa")
        for fpath in (os.path.join(Config.os_default, 'casa'), os.path.join(Config.unit_files_path, 'casa.service')):
            if os.path.exists(fpath):
                print('  - Deleting', fpath)
                self.run(['rm', '-f', fpath])

        print("  - Removing casa directives from apache configuration")
        self.remove_apache_directive('<Location /casa>')

        jans_auth_plugins = jans_auth_installer.get_plugins(paths=True)

        casa_config_class_path = os.path.join(self.jans_auth_custom_lib_dpath, os.path.basename(self.casa_config_fpath))

        if os.path.exists(casa_config_class_path):
            print('  - Deleting', casa_config_class_path)
            self.run(['rm', '-f', casa_config_class_path])

        if casa_config_class_path in jans_auth_plugins:
            print("  - Removing plugin {} from Jans Auth Configuration".format(casa_config_class_path))
            jans_auth_plugins.remove(casa_config_class_path)
            jans_auth_installer.set_class_path(jans_auth_plugins)

        for plib in SetupCasa.casa_python_libs:
            plib_fpath = os.path.join(self.py_lib_dpath, plib)
            if os.path.exists(plib_fpath):
                print('  - Deleting', plib_fpath)
                self.run(['rm', '-f', plib_fpath])

        result = self.dbUtils.search('ou=clients,o=jans', '(&(inum={}*)(objectClass=jansClnt))'.format(SetupCasa.casa_client_id_prefix))
        if result:
            print("  - Deleting casa client from db backend")
            self.dbUtils.delete_dn(result['dn'])

        print("  - Deleting casa configuration from db backend")
        self.dbUtils.delete_dn('ou=casa,ou=configuration,o=jans')

        print("  - Deleting script 3000-F75A from db backend")
        self.dbUtils.delete_dn('inum=3000-F75A,ou=scripts,o=jans')

        casa_dir = os.path.join(Config.jetty_base, SetupCasa.service_name)
        if os.path.exists(casa_dir):
            print('  - Deleting', casa_dir)
            self.run(['rm', '-f', '-r', casa_dir])

    def check_if_casa_installed(self):

        jetty_service_dpath = os.path.join(Config.jetty_base, SetupCasa.service_name)
        jetty_service_webapps_dpath = os.path.join(jetty_service_dpath, 'webapps')

        casa_webapps_fpath = os.path.join(jetty_service_webapps_dpath, os.path.basename(self.casa_war_fpath))
        casa_default_fpath = os.path.join(Config.os_default, 'casa')
        casa_service_fpath = os.path.join(Config.unit_files_path, 'casa.service')

        if os.path.exists(casa_webapps_fpath) and os.path.exists(casa_default_fpath) and os.path.exists(casa_service_fpath):
            return True
        else:
            return False

def download_jans_installer(setup_branch):

    debugpy.breakpoint();
#    jans_archieve_url = 'https://github.com/JanssenProject/jans/archive/refs/heads/{}.zip'.format(setup_branch)
    jans_archieve_url = 'http://192.168.64.4/jans/jans.2278.zip'
    with tempfile.TemporaryDirectory() as tmp_dir:
        jans_zip_fpath = os.path.join(tmp_dir, os.path.basename(jans_archieve_url))
        print("Downloading {} as {}".format(jans_archieve_url, jans_zip_fpath))
        request.urlretrieve(jans_archieve_url, jans_zip_fpath)
        if not os.path.exists(jans_dist_dpath):
            os.makedirs(jans_dist_dpath)
        shutil.copyfile(jans_zip_fpath, os.path.join(jans_dist_dpath, 'jans.zip'))
        print("Extracting jans-setup package")
        jans_zip = zipfile.ZipFile(jans_zip_fpath)
        parent_dir = jans_zip.filelist[0].orig_filename
        unpack_dir = os.path.join(tmp_dir, 'unpacked')
        shutil.unpack_archive(jans_zip_fpath, unpack_dir)
        shutil.copytree(os.path.join(unpack_dir, parent_dir, 'jans-linux-setup/jans_setup'), jans_setup_dpath)
        jans_zip.close()

def download_flex(flex_version):

    debugpy.breakpoint();
    flex_archieve_url = 'https://github.com/GluuFederation/flex/archive/refs/tags/v{}.zip'.format(flex_version)
    with tempfile.TemporaryDirectory() as tmp_dir:
        flex_zip_fpath = os.path.join(tmp_dir, os.path.basename(flex_archieve_url))
        print("Downloading {} as {}".format(flex_archieve_url, flex_zip_fpath))
        request.urlretrieve(flex_archieve_url, flex_zip_fpath)

        print("Extracting flex package")
        flex_zip = zipfile.ZipFile(flex_zip_fpath)

        unpack_dir = os.path.join(tmp_dir, 'unpacked')
        parent_dir = flex_zip.filelist[0].orig_filename
        shutil.unpack_archive(flex_zip_fpath, unpack_dir)

        if not os.path.exists(casa_dist_dpath):
            os.makedirs(casa_dist_dpath)

        if not os.path.exists(casa_dist_pylib_dpath):
            os.makedirs(casa_dist_pylib_dpath)

        if not os.path.exists(casa_dist_templates_dpath):
            os.makedirs(casa_dist_templates_dpath)

        for fpath in glob.glob(os.path.join(unpack_dir, parent_dir, 'casa/extras/*.py')):
            print("Copying", fpath, "to", casa_dist_pylib_dpath)
            shutil.copyfile(fpath, os.path.join(casa_dist_pylib_dpath, os.path.basename(fpath)))

        shutil.copyfile(os.path.join(unpack_dir, parent_dir, 'casa/extras/{}'.format(casa_web_resources_fname)), os.path.join(casa_dist_dpath, casa_web_resources_fname))
        
        casa_setup_templates_fnames = ( 'casa.default', 'casa.service', 'casa_apache_directive',
                    'casa_client.ldif', 'casa_config.ldif', 'casa_person_authentication_script.ldif', )

        for fname in casa_setup_templates_fnames:
            fpath = os.path.join(unpack_dir, parent_dir, 'flex-linux-setup/flex_linux_setup/templates', fname)
            print("Copying", fpath, "to", casa_dist_templates_dpath)
            shutil.copyfile(fpath, os.path.join(casa_dist_templates_dpath, fname))

        flex_zip.close()

def get_casa_setup_parser():

    parser = argparse.ArgumentParser(description="This script downloads Csas components and installs them")

    parser.add_argument('-jans-branch', help="Janssen github branch", default='main')
    parser.add_argument('-install-casa', help="Install casa", action='store_true')
    parser.add_argument('-uninstall-casa', help="Remove casa", action='store_true')
    parser.add_argument('-profile', help="Setup profile", choices=['jans', 'openbanking', 'disa-stig'], default='jans')
    parser.add_argument('-casa-version', help="Casa version", default='5.0.0-12')
    parser.add_argument('-casa-client-id', help="Casa client id")
    parser.add_argument('-casa-client-pw', help="Casa client password")

    return parser

def is_string_blank(in_string):

    return not (in_string and in_string.strip())

def main():

    debugpy.breakpoint();
    try:
        parser = get_casa_setup_parser()

        argsp,nargs = parser.parse_known_args()

        if argsp.install_casa and argsp.uninstall_casa:
            print("Options:")
            print("-install-casa = {}".format(argsp.install_casa))
            print("-uninstall-casa = {}".format(argsp.uninstall_casa))
            print("Incompatible Options...")

            return

        global cur_dpath
        global dist_dpath
        global jans_dist_dpath
        global casa_dist_dpath
        global casa_dist_pylib_dpath
        global casa_dist_templates_dpath
        global casa_web_resources_fname
        global jans_setup_dpath
        global app_versions

        global DISA_STIG_PROFILE

        cur_dpath = os.path.dirname(os.path.realpath(__file__))

        dist_dpath = '/opt/dist/'

        jans_dist_dpath = os.path.join(dist_dpath, 'jans')
        casa_dist_dpath = os.path.join(jans_dist_dpath, 'gluu-casa')
        casa_dist_pylib_dpath = os.path.join(casa_dist_dpath, 'pylib')
        casa_dist_templates_dpath = os.path.join(casa_dist_dpath, 'templates')

        casa_web_resources_fname = 'casa_web_resources.xml'

        jans_setup_dpath = '/opt/jans/jans-setup/'

        DISA_STIG_PROFILE = 'disa-stig'

        app_versions = {
            "BASE_SERVER": "http://192.168.64.4/jans",
            "BASE_SERVER_JANS": "http://192.168.64.4/jans",
            "BASE_SERVER_CASA": "http://192.168.64.4/casa"
        }

        #global app_versions = {
        #    "GLUU_MAVEN": "https://maven.gluu.org"
        #}

        install_casa = argsp.install_casa
        uninstall_casa = argsp.uninstall_casa

        print("install_casa = {}".format(install_casa))
        print("uninstall_casa = {}".format(uninstall_casa))

        profile = argsp.profile
        os.environ['JANS_PROFILE'] = profile

        debugpy.breakpoint();

        if os.path.exists(jans_setup_dpath):
            print("Backing up old Janssen setup directory")
            os.system('mv {} {}-{}'.format(jans_setup_dpath, jans_setup_dpath.rstrip('/'), time.ctime().replace(' ', '_')))

        download_jans_installer(argsp.jans_branch)

        if install_casa:
            download_flex(argsp.casa_version)

        debugpy.breakpoint();

        if os.path.exists(jans_setup_dpath):
            sys.path.append(jans_setup_dpath)

        global downloads
        global base
        global arg_parser

        from setup_app import downloads
        from setup_app.utils import base
        from setup_app.utils import arg_parser

        arg_parser.add_to_me(parser)
        argsp = arg_parser.get_parser()

        base.current_app.profile = profile
        base.argsp = argsp

        base.argsp.j = True

        downloads.base.current_app.app_info = base.readJsonFile(os.path.join(jans_setup_dpath, 'app_info.json'))

        downloads.download_sqlalchemy()
        downloads.download_cryptography()
        downloads.download_pyjwt()

        if 'SETUP_BRANCH' not in base.current_app.app_info:
            base.current_app.app_info['SETUP_BRANCH'] = argsp.jans_branch

        base.current_app.app_info['ox_version'] = base.current_app.app_info['JANS_APP_VERSION'] + base.current_app.app_info['JANS_BUILD']

        sys.path.insert(0, base.pylib_dir)
        
        global Properties
        global jwt
        global LDIFWriter
        global packageUtils
        global Config
        global CollectProperties
        global NodeInstaller
        global HttpdInstaller
        global ConfigApiInstaller
        global JettyInstaller
        global JansAuthInstaller
        global JansCliInstaller
        global propertiesUtils
        global myLdifParser

        from setup_app.pylib.jproperties import Properties
        from setup_app.pylib import jwt
        from setup_app.pylib.ldif4.ldif import LDIFWriter
        from setup_app.utils.package_utils import packageUtils
        from setup_app.config import Config
        from setup_app.utils.collect_properties import CollectProperties
        from setup_app.installers.node import NodeInstaller
        from setup_app.installers.httpd import HttpdInstaller
        from setup_app.installers.config_api import ConfigApiInstaller
        from setup_app.installers.jetty import JettyInstaller
        from setup_app.installers.jans_auth import JansAuthInstaller
        from setup_app.installers.jans_cli import JansCliInstaller
        from setup_app.utils.properties_utils import propertiesUtils
        from setup_app.utils.ldif_utils import myLdifParser

        debugpy.breakpoint();

        logs_dpath = os.path.join(cur_dpath, 'logs')

        if not os.path.exists(logs_dpath):
            os.makedirs(logs_dpath)

        if jans_setup_dpath not in sys.path:
            sys.path.append(jans_setup_dpath)

        global paths

        from setup_app import paths

        paths.LOG_FILE = os.path.join(logs_dpath, 'casa-setup.log')
        paths.LOG_ERROR_FILE = os.path.join(logs_dpath, 'casa-setup-error.log')

        print()
        print("Log Files:")
        print(paths.LOG_FILE)
        print(paths.LOG_ERROR_FILE)
        print()
        
        global static

        from setup_app import static

        if argsp.profile == DISA_STIG_PROFILE:
            base.argsp.opendj_keystore_type = 'bcfks'

        Config.init(paths.INSTALL_DIR)

        collectProperties = CollectProperties()
        collectProperties.collect()

        debugpy.breakpoint();

        Config.outputFolder = os.path.join(jans_setup_dpath, 'output')
        if not os.path.join(Config.outputFolder):
            os.makedirs(Config.outputFolder)

        debugpy.breakpoint();

        global httpd_installer
        global jans_auth_installer

        httpd_installer = HttpdInstaller()
        config_api_installer = ConfigApiInstaller()
        jans_auth_installer = JansAuthInstaller()

        debugpy.breakpoint();

        setup_casa = SetupCasa(cur_dpath)

        # creating SetupCasa (new class SetupCasaInstaller), that is delivered from JettyInstaller 
        class SetupCasaInstaller(setup_casa.__class__, JettyInstaller):
            pass

        setup_casa.__class__ = SetupCasaInstaller

        casa_installed = setup_casa.check_if_casa_installed()

        to_install_casa = install_casa and not casa_installed
        to_uninstall_casa = uninstall_casa and casa_installed

        setup_casa.logIt("to_install_casa   = {}".format(to_install_casa))
        setup_casa.logIt("to_uninstall_casa = {}".format(to_uninstall_casa))

        if to_install_casa and to_uninstall_casa:
            print("Incompatible Options...")

        if to_install_casa:
            setup_casa.download_files()
            setup_casa.install_casa()

        elif to_uninstall_casa:
            config_api_installer.stop(SetupCasa.service_name)
            setup_casa.uninstall_casa()

        if to_install_casa or to_uninstall_casa:
            print("Restarting Apache")
            httpd_installer.restart()

            print("Restarting Jans Auth")
            config_api_installer.restart('jans-auth')

            print("Restarting Janssen Config Api")
            config_api_installer.restart()

        if to_install_casa:
            print("Starting Casa")
            config_api_installer.start(SetupCasa.service_name)

            print("Installation was completed")
            print()
            print("Casa https://{}/casa".format(Config.hostname))

    except Exception as ex:
        print(ex)
        print(traceback.format_exc())

    debugpy.breakpoint();

    print()
    print("Exit Setup Casa")

if __name__ == '__main__':

    debugpy.breakpoint();
    main()

#    sys.exit()
