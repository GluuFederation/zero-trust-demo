import readline
import os
import shutil
import json

dist_dir = '/opt/dist'

lb_host = input('Load Balancer FQDN: ')
node_11_ip = input('Ip address of Node 1-1 (this machine): ')
node_12_ip = input('Ip address of Node 1-2 : ')
node_21_ip = input('Ip address of Node 2-1 : ')
node_22_ip = input('Ip address of Node 2-2 : ')

config = {
    'node_11_ip': node_11_ip,
    'node_12_ip': node_12_ip,
    'node_21_ip': node_21_ip,
    'node_22_ip': node_22_ip,
    'load_balancer': lb_host
    }

unit_files =  ['casa.service',
               'oxd-server.service',
               'identity.service',
               'oxauth.service',
               'opendj.service']

print("Copying files")

os.system('cp -f /install/community-edition-setup/pylib/pyDes.py /opt/gluu/bin')

if os.path.exists('/opt/etc'):
    shutil.rmtree('/opt/etc')

os.mkdir('/opt/etc/')

os.system('cp -r -f -p /etc/certs /opt/etc/certs')
os.system('cp -r -f -p /etc/default /opt/etc/default')
os.system('cp -r -f -p /etc/gluu /opt/etc/gluu')

os.mkdir('/opt/etc/httpd')
os.system('cp -p /etc/httpd/conf/httpd.conf /opt/etc/httpd')
os.system('cp -p /etc/httpd/conf.d/https_gluu.conf /opt/etc/httpd')

os.mkdir('/opt/etc/systemd')
for uf in unit_files:
    src = os.path.join('/etc/systemd/system', uf)
    os.system('cp -p {} /opt/etc/systemd'.format(src))

os.system('cp -p /etc/passwd /opt/etc')
os.system('cp -p /etc/group /opt/etc')

ldappw_fn = '/root/.ldappwd'

for l in open('/etc/gluu/conf/gluu-ldap.properties'):
    if l.startswith('bindPassword'):
        ldapencpw = l[13:].strip()
        ldappw = os.popen('/opt/gluu/bin/encode.py -D ' + ldapencpw).read().strip()
        with open(ldappw_fn, 'w') as w:
            w.write(ldappw)
        break

with open('/opt/etc/cluster.json', 'w') as configfile:
    json.dump(config, configfile, indent=2)

print("Making opendj listen all interfaces")
os.system('''/opt/opendj/bin/dsconfig -h localhost -p 4444 -D 'cn=directory manager' -j /root/.ldappwd -n set-administration-connector-prop --set listen-address:%s -X''' % node_11_ip)
os.system('''/opt/opendj/bin/dsconfig -h localhost -p 4444 -D 'cn=directory manager' -j /root/.ldappwd -n set-connection-handler-prop --handler-name 'LDAPS Connection Handler' --set enabled:true --set listen-address:0.0.0.0 -X''')

print("Stopping services")
for uf in unit_files:
    os.system('systemctl stop ' + uf)

print("Creating archive gluu-opt.tgz")
os.system('tar -zcf gluu-opt.tgz /opt')

unit_files.reverse()
print("Starting services")
for uf in unit_files:
    os.system('systemctl start ' + uf)

os.remove(ldappw_fn)
print("Copy gluu-opt.tgz to other nodes and execute 'python3 node-secondary.py'")
