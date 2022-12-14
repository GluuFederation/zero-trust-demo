ffdays=`date -d "-45 days" "+%Y%m%d%H%M%S"`
tdays=`date -d "-30 days" "+%Y%m%d%H%M%S"`

echo $DM_PW > /home/root/.pw

echo "Getting users to deactivate..."
/opt/opendj/bin/ldapsearch -h localhost -p 1636 -Z -X -D 'cn=directory manager' -j /home/ldap/.pw -b o=gluu -s sub "&(lastLogin>=$ffdays)(lastLogin<=$tdays)" 1.1  > /opt/opendj/bin/toDeactivate.ldif
echo "Getting users to remove..."
/opt/opendj/bin/ldapsearch -h localhost -p 1636 -Z -X -D 'cn=directory manager' -j /home/ldap/.pw -b o=gluu -s sub "(lastLogin<=$ffdays)" 1.1  > /opt/opendj/bin/toRemove.ldif

echo "Deactivating the users..."
for i in `cat /opt/opendj/bin/toDeactivate.ldif`; do /opt/opendj/bin/ldapmodify -Z -X  -h localhost -p 1636  -D "cn=directory manager" -j /home/ldap/.pw  << EOF
dn:$i
changetype:modify
replace:gluuStatus
gluuStatus:inactive
EOF
done

echo "Removing inactive users..."
for i in `cat /opt/opendj/bin/toRemove.ldif`; do /opt/opendj/bin/ldapmodify -Z -X  -h localhost -p 1636  -D "cn=directory manager" -j /home/ldap/.pw  << EOF
dn:$i
changetype: delete
EOF
done

rm /home/root/.pw
