HOST1_IP=172.16.113.148
LOCAL_IP=172.16.113.145

HOST1_PWD=OpenSASTeam_2020
LOCAL_PWD=OpenSASTeam_2020

sudo sh /tmp/enableDSSecurity.sh

echo ---------------------------------------
echo Start OpenDJ DSReplication
echo ---------------------------------------

cd /opt/opendj/bin/

./dsreplication enable --host1 $HOST1_IP --port1 4444 --bindDN1 "cn=directory manager" --bindPassword1 $HOST1_PWD --replicationPort1 8989 --host2 $LOCAL_IP --port2 4444 --bindDN2 "cn=directory manager" --bindPassword2 $LOCAL_PWD --replicationPort2 8989 --adminUID admin --adminPassword $HOST1_PWD --baseDN "o=gluu" -X -n

./dsreplication initialize --baseDN "o=gluu" --adminUID admin --adminPassword $HOST1_PWD --hostSource $HOST1_IP --portSource 4444  --hostDestination $LOCAL_IP --portDestination 4444 -X -n


./dsreplication enable --host1 $HOST1_IP --port1 4444 --bindDN1 "cn=directory manager" --bindPassword1 $HOST1_PWD --replicationPort1 8989 --host2 $LOCAL_IP --port2 4444 --bindDN2 "cn=directory manager" --bindPassword2 $LOCAL_PWD --replicationPort2 8989 --adminUID admin --adminPassword $HOST1_PWD --baseDN "o=site" -X -n

./dsreplication initialize --baseDN "o=site" --adminUID admin --adminPassword $HOST1_PWD --hostSource $HOST1_IP --portSource 4444  --hostDestination $LOCAL_IP --portDestination 4444 -X -n

echo ---------------------------------------
echo Start OpenDJ DSReplication - DONE
echo ---------------------------------------

sudo sh /tmp/enableDSSecurity.sh
