import os
import sys
import shutil
import glob
import json

print("Which node is this?")
node_list = (('Node 1-2', 'node_12_ip'), ('Node 2-1', 'node_21_ip'), ('Node 2-2', 'node_22_ip'))
for i, node in enumerate(node_list):
    print(i+1, node[0])

while True:
    node_number = input("Please enter 1-3: ")
    if node_number in ("1", "2", "3"):
        break

this_node = node_list[int(node_number)-1][1]

unit_files = ['casa.service',
              'oxd-server.service',
              'identity.service',
              'oxauth.service',
              'opendj.service']

print("Extracting gluu-opt.tgz")
os.system('tar -zxf gluu-opt.tgz -C /')

with open('/opt/etc/cluster.json') as configfile:
    config = json.load(configfile)

print("This is\033[1m", node_list[int(node_number)-1][0], "\033[0mwith IP Address\033[1m", config[this_node], "\033[0m")
while True:
    confirm = input("Is this right? [yes/N] ")
    if confirm=='yes' or confirm.lower().startswith('n'):
        break
    else:
        print("Please type \033[1m yes \033[0m to continue")

if confirm != 'yes':
    sys.exit()

print("Copying files")
os.system('cp -p -f /opt/etc/passwd /etc/')
os.system('cp -p -f /opt/etc/group /etc/')

os.system('cp -p -r -f /opt/etc/certs /etc')
os.system('cp -p -r -f /opt/etc/default /etc')
os.system('cp -p -r -f /opt/etc/gluu /etc')

os.system('cp -p /opt/etc/httpd/httpd.conf /etc/httpd/conf/')
os.system('cp -p -f /opt/etc/httpd/https_gluu.conf /etc/httpd/conf.d/')
os.system('cp -p -f /opt/etc/systemd/* /etc/systemd/system')


with open('/etc/hosts', 'a') as w:
    w.write('{}\t{}\n'.format(config[this_node], config['load_balancer']))

print("Starting services")

os.system('systemctl restart httpd')
os.system('systemctl enable httpd')

for uf in unit_files[::-1]:
    os.system("systemctl enable " + uf)
    os.system("systemctl start " + uf)

if this_node == 'node_22_ip':
    ldappw_fn = '/root/.ldappwd'

    for l in open('/etc/gluu/conf/gluu-ldap.properties'):
        if l.startswith('bindPassword'):
            ldapencpw = l[13:].strip()
            ldappw = os.popen('/opt/gluu/bin/encode.py -D ' + ldapencpw).read().strip()
            with open(ldappw_fn, 'w') as w:
                w.write(ldappw)
                break


    print("Enabling and initializing replications")

    primary = config['node_11_ip']

    for node in ('node_12_ip', 'node_21_ip', 'node_22_ip'):
        cmd_enable = '/opt/opendj/bin/dsreplication enable --host1 {} --port1 4444 --bindDN1 "cn=directory manager" --bindPasswordFile1 /root/.ldappwd --replicationPort1 8989 --host2 {} --port2 4444 --bindDN2 "cn=directory manager" --bindPasswordFile2 /root/.ldappwd --replicationPort2 8989 --adminUID admin -j /root/.ldappwd --baseDN "o=gluu" -X -n'.format(primary, config[node])
        print("Executing command", cmd_enable)
        os.system(cmd_enable)
        cmd_init = '/opt/opendj/bin/dsreplication initialize --baseDN "o=gluu" --adminUID admin -j /root/.ldappwd --hostSource {} --portSource 4444  --hostDestination {} --portDestination 4444 -X -n'.format(primary, config[node])
        print("Executing command", cmd_init)
        os.system(cmd_init)

    for node in ('node_11_ip', 'node_12_ip', 'node_21_ip', 'node_22_ip'):
        cmd_secure = '/opt/opendj/bin/dsconfig -h {} -p 4444 -D "cn=Directory Manager" -j /root/.ldappwd --trustAll -n set-crypto-manager-prop --set ssl-encryption:true'.format(config[node])
        print("Executing command", cmd_secure)
        os.system(cmd_secure)

    print("Checking Replication Status")
    cmd_status = '/opt/opendj/bin/dsreplication status -n -X -h {} -p 4444 -I admin -j /root/.ldappwd'.format(primary)
    print("Executing command", cmd_status)
    os.system(cmd_status)
