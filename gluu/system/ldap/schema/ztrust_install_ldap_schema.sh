 #!/bin/sh

# ztrust_install_ldap_schema.sh <password> <password_fpath> <shema_dpath>
# password              - LDAP admin password;
# password_fpath        - file path, where password will be saved;
#                             will be removed after finishing;
#                             default: "/tmp/opendj_pw.dat"
# opendj_dpath          - directory path, where opendj is placed;
#                             default: "/opt/opendj"

password="$1";
pw_fpath="$2";
opendj_dpath="$3";

if [ -z "$pw_fpath" ]; then
    pw_fpath="/tmp/opendj_pw.dat";
fi;

if [ -z "$schema_dpath" ]; then
    opendj_dpath="/opt/opendj";
fi;

echo "-----------------------------";

echo "password = $password";
echo "pw_fpath = $pw_fpath";
echo "opendj_dpath = $opendj_dpath";

echo "-----------------------------";

if [ -f $pw_fpath ]; then
    echo "File: $pw_fpath is found. removing...";
    rm $pw_fpath
    echo "File: $pw_fpath is removed.";
fi;

echo "Creating file: $pw_fpath";

echo "$password">"$pw_fpath";

if [ $? == 0 ]; then
    echo "File: $pw_fpath has been created";
else
    echo "File: $pw_fpath hasn't been created";
    exit 1;
fi;

echo "Copying file: 102-ztrustPerson.ldif";
cp 102-ztrustPerson.ldif "$opendj_dpath/config/schema";
if [ $? == 0 ]; then
    echo "File: 102-ztrustPerson.ldif has been copied";
else
    echo "File: 102-ztrustPerson.ldif hasn't been copied";
    exit 1;
fi;

echo "Setup owner 'ldap:ldap' of the file: $opendj_dpath/config/schema/102-ztrustPerson.ldif";
chown ldap:ldap "$opendj_dpath/config/schema/102-ztrustPerson.ldif";
if [ $? == 0 ]; then
    echo "Owner 'ldap:ldap' is Ok";
else
    echo "Owner 'ldap:ldap' isn't Ok";
    exit 1;
fi;

echo "Restarting service 'opendj'";
service opendj restart;
if [ $? == 0 ]; then
    echo "Service 'opendj' has been restarted";
else
    echo "Service 'opendj' hasn't been restarted";
    exit 1;
fi;

echo "Copying file: ztrust-oxtrust-attributes.ldif";
cp ztrust-oxtrust-attributes.ldif "$opendj_dpath/ldif";
if [ $? == 0 ]; then
    echo "File: ztrust-oxtrust-attributes.ldif has been copied";
else
    echo "File: ztrust-oxtrust-attributes.ldif hasn't been copied";
    exit 1;
fi;

echo "Setup owner 'ldap:ldap' of the file: $opendj_dpath/ldif/ztrust-oxtrust-attributes.ldif";
chown ldap:ldap "$opendj_dpath/ldif/ztrust-oxtrust-attributes.ldif";
if [ $? == 0 ]; then
    echo "Owner 'ldap:ldap' is Ok";
else
    echo "Owner 'ldap:ldap' isn't Ok";
    exit 1;
fi;


echo "Running $opendj_dpath/bin/ldapmodify";
$opendj_dpath/bin/ldapmodify -h localhost -p 1636 -Z -D "cn=Directory Manager" -j "$pw_fpath" -a -f "$opendj_dpath/ldif/ztrust-oxtrust-attributes.ldif";
if [ $? == 0 ]; then
    echo "$opendj_dpath/bin/ldapmodify is Ok";
else
    echo "$opendj_dpath/bin/ldapmodify isn't Ok";
    exit 1;
fi;

echo "Running $opendj_dpath/bin/dsconfig create-backend-index";
$opendj_dpath/bin/dsconfig create-backend-index -h localhost -p 4444 -D "cn=Directory Manager" -j "$pw_fpath" --no-prompt --backend-name userRoot --type generic --index-name userStatus --set index-type:presence --set index-type:equality --set index-entry-limit:4000;
if [ $? == 0 ]; then
    echo "$opendj_dpath/bin/ldapmodify is Ok";
else
    echo "$opendj_dpath/bin/ldapmodify isn't Ok";
    exit 1;
fi;

echo "Running $opendj_dpath/bin/rebuild-index";
$opendj_dpath/bin/rebuild-index -h localhost -p 4444 -D "cn=Directory Manager" -j "$pw_fpath" -b o=gluu --index userStatus --start 0;
if [ $? == 0 ]; then
    echo "$opendj_dpath/bin/ldapmodify is Ok";
else
    echo "$opendj_dpath/bin/ldapmodify isn't Ok";
    exit 1;
fi;

echo "Restarting service 'opendj'";
service opendj restart;
if [ $? == 0 ]; then
    echo "Service 'opendj' has been restarted";
else
    echo "Service 'opendj' hasn't been restarted";
    exit 1;
fi;

if [ -f $pw_fpath ]; then
    echo "File: $pw_fpath is found. removing...";
    rm $pw_fpath
    echo "File: $pw_fpath is removed.";
fi;

exit 0;
