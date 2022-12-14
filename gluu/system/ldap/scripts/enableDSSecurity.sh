LOCAL_IP=172.16.113.145
LOCAL_PWD=OpenSASTeam_2020


echo ---------------------------------------
echo Enable OpenDJ Security
echo ---------------------------------------

cd /opt/opendj/bin/

./dsconfig --trustAll --no-prompt --hostname localhost --port 4444 --bindDN "cn=directory manager" -w $LOCAL_PWD set-administration-connector-prop --set listen-address:0.0.0.0

./dsconfig --trustAll --no-prompt --hostname localhost --port 4444 --bindDN "cn=directory manager" -w $LOCAL_PWD set-connection-handler-prop --handler-name "LDAPS Connection Handler" --set enabled:true --set listen-address:0.0.0.0

./dsconfig -h $LOCAL_IP -p 4444 -D "cn=Directory Manager" -w $LOCAL_PWD --trustAll -n set-crypto-manager-prop --set ssl-encryption:true

echo ---------------------------------------
echo Enable OpenDJ Security - DONE
echo ---------------------------------------
