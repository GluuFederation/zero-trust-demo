# EMail 2FA Authentication Plugin
## Plugin allows enrollment and authentication via user email address
Steps:

### 1. Intializing of SMTP server

This SMTP server and his account parameters will be used for sending emails with OTP.
Follow account parameters should be initialized, using **/opt/jans/jans-cli/config-cli.py** or **/opt/jans/jans-cli/config-cli-tui.py**, **SMTP** section:

- **SMTP Host**: domain name of smtp server:
    * for example: *smtp.gmail.com*, *smtp.mail.yahoo.com*;
- **From Name**: user name:
    * for example: *John Doe*;
- **From Email Address**: email address:
    * for example: *john.doe@gmail.com*;
- **Requires Authentication**
- **SMTP User Name**: acount id:
    * for example: *john.doe@gmail.com*, in some cases on some servers: *john.doe*;
- **SMTP Password**
- **SMTP Connect Protection**: secure protocol of the connection (*NONE*, *SSL/TLS*, *STARTTLS*):
    * for example: *smtp.gmail.com*: *SSL/TLS* - 465 port, *STARTTLS* - 587 port;
- **Trust Server**: If set, the **SMTP Host** will be marked as trusted server;
- **SMTP Port**: Number of TCP/IP port of the **SMTP Host**.

### 2. Intializing of Keystore

This Keystore and his keypair (*private key** and **public key/certificate**) will be used for singing emails.
Follow account parameters should be initialized, using **/opt/jans/jans-cli/config-cli.py** or **/opt/jans/jans-cli/config-cli-tui.py**, **SMTP** section:

- **KeyStore:**: keystore file path:
    * for example: */etc/certs/smtp-keys.bcfks*;
- **Keystore Password:**: keystore/alias password:
    * for example: *tRmJpb$1_&BzlEUC7*;
- **Keystore Alias:**: alias of an entry (keypair: **private key** and **public key/certificate**) in the keystore:
    * for example: *smtp_sig_ec256*;
- **Keystore Signing Alg**: algorithm is used for signing of an email:
    * for example: *SHA256withECDSA*;

After initializing **SMTP Server** and **Keystore**, applications (including the plug-in **email_2fa_plugin**) can sign emails and send them, using SMTP Server and his account.

### 2. Installing plug-in script **email_2fa_plugin**

- Launch **config-cli-tui.py** (**python3 -W ignore /opt/jans/jans-cli/config-cli-tui.py**);
- Navigate to *Scripts*, and click **Add Script**;
- Specify the name as `ztrust-email_2fa_plugin` and properties, defined in *README.md* (*<root-dir>/code/scripts/person_authn/email_2fa_plugin*);
- Script can be installed and used as Authentication Method without installed **Casa** and plug-in **email_2fa_plugin**;

### 3. Installing casa plug-in **email_2fa_plugin**

- For installing casa plug-ins, it's necessary enable **Administrative mode**. It can be executed, creating file *.administrable* in the home directory of **Casa**
(*/opt/jans/jetty/casa*). After re-launching **Casa**, **Administrative mode** will be enabled;
- Login as **Admin User**;
- Install (*Add a plugin*) of the plugin **email_2fa_plugin** (**ztrust-email_2fa_plugin**) on the page *Manage your Gluu Casa plugins* of **Casa**;

Installed plug-in:

![installed plugin](./img/1.installed_plugin.png)

### 4. Enabling casa plug-in **email_2fa_plugin**

- If plug-in script **email_2fa_plugin** (**ztrust-email_2fa_plugin**) has been added this plug-in can be enabled on the page: *Enabled authentication methods* of **Casa**;

Enabled plug-in:

![enabled plugin](./img/2.enabled_plugin.png)

### 5. Tuning casa plug-in **email_2fa_plugin** (**Email 2FA Plugin**)

- If plug-in **email_2fa_plugin** has been enabled, user can get the plug-in **email_2fa_plugin** (**Email 2FA Plugin**) on the page:
*Manage your trusted credentials for account access* of **Casa**;
- Open the plug-in **email_2fa_plugin** (**Email 2FA Plugin**);
- Enter necessary email;

Manage your trusted credentials:

![Manage your trusted credentials](./img/3.manage_creds.png)

Email 2FA Plugin:

![Manage your trusted credentials](./img/4.email_2fa_plugin.png)

### 6. Enabling Tuning casa plug-in **email_2fa_plugin** (**Email 2FA Plugin**) as 2FA Plugin of **Casa**

- After setting up casa plug-in on the page: *Manage your trusted credentials for account access* of **Casa** the plug-in **email_2fa_plugin** (**Email 2FA Plugin**)
can be used as 2FA Plugin of **Casa**;
- Tune Second Factor Authentication if the required **Casa** requirements are implemented;

Tuning Second Factor Authentication:

![Tuning Second Factor Authentication](./img/5.second_factor_auth.png)

### 7. 2FA Authentication, using **email_2fa_plugin** (**Email 2FA Plugin**) plugin of **Casa** or **delegated admin** plugin (**casa**) of **Casa**

Welcome Login Page:

![Tuning Second Factor Authentication](./img/6.login_welcome.png)

2FA Login Page, that contains entered OTP:

![Tuning Second Factor Authentication](./img/7.login_auth_token.png)
