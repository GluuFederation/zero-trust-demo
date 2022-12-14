#
# NOTE: REMEMBER TO REMOVE THE SERVERS USING THE CLUSTER MANAGER GUI FIRST
#

echo ---------------------------------------
echo Stop and disable services
echo ---------------------------------------

sudo systemctl stop casa
sudo systemctl disable casa
sudo systemctl stop oxauth-rp
sudo systemctl disable oxauth-rp
sudo systemctl stop oxauth
sudo systemctl disable oxauth
sudo systemctl stop idp
sudo systemctl disable idp
sudo systemctl stop identity
sudo systemctl disable identity
sudo systemctl stop opendj
sudo systemctl disable opendj
sudo yum remove -y gluu-server-nochroot

echo ---------------------------------------
echo Stop and disable services - DONE
echo ---------------------------------------

echo ---------------------------------------
echo Remove symbolic links
echo ---------------------------------------

cd /opt/
sudo unlink gluu-server
sudo unlink jetty
sudo unlink jre
sudo unlink jython
sudo unlink node

echo ---------------------------------------
echo Remove symbolic links - DONE
echo ---------------------------------------

echo ---------------------------------------
echo Clean up installation files
echo ---------------------------------------

sudo rm -rf /opt/amazon-corretto-11.0.8.10.1-linux-x64/ /opt/dist/ /opt/jetty-9.4/ /opt/jython-2.7.2/ /opt/node-v12.18.3-linux-x64/ /opt/opendj/ /opt/oxd-server/ /opt/shibboleth-idp/ /opt/gluu/ /opt/logo.png /opt/favicon.ico
sudo rm -rf /etc/default/casa /etc/default/identity /etc/default/idp /etc/default/oxauth /etc/default/oxd-server /etc/default/oxauth-rp
sudo rm -rf /install /etc/certs /etc/gluu /var/gluu
sudo rm -rf /root/setup.properties /etc/cron.daily/super_gluu_lisence_renewer

echo ---------------------------------------
echo Clean up installation files - DONE
echo ---------------------------------------
