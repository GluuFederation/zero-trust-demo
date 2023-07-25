#!/usr/bin/python3

import sys
import os
import shutil

import subprocess
import tempfile
import zipfile

import optparse


def init(argv):

    global opt_parser;

    global cust_tmp_dname;
    global cust_in_fpath;
    global branch_name;
    global gluu_depl_dpath;
    global chown_cmd;
    global cp_cmp;
    global cust_root;
    global process_files;
    
    opt_parser = optparse.OptionParser();
    
    in_arch_fpath_default = "./zero-trust-demo-main.zip";
    out_base_dpath_default = "/opt/jans";

    opt_parser.add_option("-i", "--in_arch_fpath", dest="in_arch_fpath", default=in_arch_fpath_default, help="input archive file path (default: '%s')" % in_arch_fpath_default);
    opt_parser.add_option("-o", "--out_base_dpath", dest="out_base_dpath", default=out_base_dpath_default, help="base output directory path (default: '%s')" % out_base_dpath_default);

    (options, args) = opt_parser.parse_args();

    cust_in_fpath = options.in_arch_fpath;
    
    cust_root = get_root_dir_zip(cust_in_fpath);

    cust_tmp_dname = "ztrust-jans-tmp";

    gluu_depl_dpath = options.out_base_dpath;

    chown_cmd = "/usr/bin/chown";
    cp_cmp = "/usr/bin/cp";
   
    process_files = [
        
            # <root-dir>/jans/code/scripts/person_authn/assets/layout
            # jetty/jans-auth/custom/pages/WEB-INF/incl/layout
            (
                ("login-template.xhtml",),
                "%s/jans/code/scripts/person_authn/assets/layout" % cust_root,
                "jetty/jans-auth/custom/pages/WEB-INF/incl/layout"
            ),

            # <root-dir>/jans/code/scripts/person_authn/assets/removefooter
            # jetty/jans-auth/custom/pages/WEB-INF/incl/layout
            (
                ("authorize-extended-template.xhtml","login-extended-template.xhtml",),
                "%s/jans/code/scripts/person_authn/assets/removefooter" % cust_root,
                "jetty/jans-auth/custom/pages/WEB-INF/incl/layout"
            ),

            # <root-dir>/jans/code/scripts/person_authn/assets/removefooter
            # jetty/jans-auth/custom/pages
            (
                ("error.xhtml",),
                "%s/jans/code/scripts/person_authn/assets/removefooter" % cust_root,
                "jetty/jans-auth/custom/pages"
            ),

            # <root-dir>/jans/code/scripts/person_authn/casa/pages 
            # jetty/jans-auth/custom/pages/casa
            (
                ("login.xhtml",),
                "%s/jans/code/scripts/person_authn/casa/pages" % cust_root,
                "jetty/jans-auth/custom/pages/casa"
            ),

            # <root-dir>/jans/code/scripts/person_authn/email_2fa_plugin/pages
            # jetty/jans-auth/custom/pages/email_auth    
            (
                ("entertoken.xhtml",),
                "%s/jans/code/scripts/person_authn/email_2fa_plugin/pages" % cust_root,
                "jetty/jans-auth/custom/pages/auth/email_auth"
            ),

            # <root-dir>/jans/code/scripts/person_authn/user_registration/pages
            # jetty/jans-auth/custom/pages/register
            (
                ("entertoken.xhtml",),
                "%s/jans/code/scripts/person_authn/user_registration/pages" % cust_root, 
                "jetty/jans-auth/custom/pages/auth/register"
            ),

            # <root-dir>/jans/code/scripts/person_authn/user_registration/pages
            # jetty/jans-auth/custom/pages/register
            (
                ("reg.xhtml","regtr.xhtml","reg_status.xhtml"),
                "%s/jans/code/scripts/person_authn/user_registration/pages" % cust_root, 
                "jetty/jans-auth/custom/pages/auth"
            ),
            
            # <root-dir>/jans/code/scripts/person_authn/assets/img
            # jetty/jans-auth/custom/static/img
            (
                ("logo.png","zero_trust.png","ver_code.png"),
                "%s/jans/code/scripts/person_authn/assets/img" % cust_root,
                "jetty/jans-auth/custom/static/img"
            )
        ];


def get_root_dir_zip(zip_fpath):
    # ziph is zipfile handle
    zip_root = None;
    
    for root, dirs, files in os.walk(zip_fpath):
        print ("get_root_dir_zip : root = " + root);
        zip_root = root;

    if zip_root is None:
        zip_fname = os.path.basename(zip_fpath);
        zip_root = os.path.splitext(zip_fname)[0];

    return zip_root;


def main(argv):

    try:
        print("Resources Deployment: Started...");

        temp_dpath = "%s%s%s" % (tempfile.gettempdir(), os.path.sep, cust_tmp_dname);

        if os.path.exists(temp_dpath):
            shutil.rmtree(temp_dpath);

        if not os.path.exists(temp_dpath):
            os.makedirs(temp_dpath);

        with zipfile.ZipFile(cust_in_fpath, 'r') as cust_in_zip_ref:
            cust_in_zip_ref.extractall(temp_dpath);

        create_dir(gluu_depl_dpath, "jetty/jans-auth/custom/pages/auth");
        create_dir(gluu_depl_dpath, "jetty/jans-auth/custom/pages/casa");
        create_dir(gluu_depl_dpath, "jetty/jans-auth/custom/pages/auth/email_auth");
        create_dir(gluu_depl_dpath, "jetty/jans-auth/custom/pages/auth/register");

        create_dir(gluu_depl_dpath, "jetty/jans-auth/custom/pages/WEB-INF");
        create_dir(gluu_depl_dpath, "jetty/jans-auth/custom/pages/WEB-INF/incl");
        create_dir(gluu_depl_dpath, "jetty/jans-auth/custom/pages/WEB-INF/incl/layout");

        create_dir(gluu_depl_dpath, "jetty/jans-auth/custom/static/img");

        for process_file in process_files:
        
            for process_fname in process_file[0]:
                print("-------------------------------------------------------");            
                in_fpath = "%s%s%s%s%s" % (temp_dpath, os.path.sep, process_file[1], os.path.sep, process_fname);
                out_dpath = "%s%s%s" % (gluu_depl_dpath, os.path.sep, process_file[2]);            

                print("in_fpath = %s" % in_fpath);
                print("out_dpath = %s" % out_dpath); 
            
                run_cmd([cp_cmp, "-f", in_fpath, out_dpath]);
                
                print("-------------------------------------------------------");

        run_cmd([chown_cmd, "-R", "jetty:jetty", get_full_dpath(gluu_depl_dpath, "jetty/jans-auth/custom")]);

        if os.path.exists(temp_dpath):
            shutil.rmtree(temp_dpath);

        print("Resources Deployment: Finished...");

    except Exception as ex:
        print("Resources Deployment: Exception: ", ex);

        
def get_full_dpath(base_dpath, sub_dpath):
    return base_dpath + os.path.sep + sub_dpath;

     
def create_dir(base_dpath, sub_dpath):
    try:
        res_dpath = base_dpath + os.path.sep + sub_dpath;
        if not os.path.exists(res_dpath):
            os.makedirs(res_dpath);
    except Exception as ex:
        print("Creating Directory: Exception: ", ex);


def run_cmd(args, cwd=None, env=None, useWait=False, shell=False, get_stderr=False):
    output = '';
    args_prn = ' '.join(args) if type(args) is list else args;
    print('Running: %s' % args_prn);

    try:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=env, shell=shell);
        if useWait:
            code = p.wait();
            print('Run: %s with result code: %d' % (' '.join(args), code) );
        else:
            output, err = p.communicate();
            output = output.decode('utf-8');
            err = err.decode('utf-8');

            if output:
                print("Output: " + output);
            if err:
                print("Error: " + err);
    except Exception as ex:
        print("Error running command: %s" % " ".join(args));
        print("Running command: Exception: ", ex);

    if get_stderr:
        return output, err

    return output


if __name__ == "__main__":

    init(sys.argv[1:]);
    main(sys.argv[1:]);
