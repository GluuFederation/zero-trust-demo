# Zero Trust Framework Documentation (Janssen Server Customizing)  

Zero Trust Demo for Jans with OpenID

# Table of Contents











The purpose of the Zero Trust Framework (customizing) is to centralize authentication,
to enable Single Sign-on (SSO), and to provide a web portal to enable end-users to
view and manage their two-factor credentials. Diagram 1 provides an overview of
how federated SSO works. In this example, an End User starts his web browser,
navigates to the Training Website, and initiates a Login event. The Browser is
redirected to the Janssen Server, which returns the Login Page. After
authentication, the Training Website can obtain an Identity Assertion from the
Janssen Server which details the authentication event (e.g. who authenticated, when
they authenticated, how they authenticated), user claims (e.g. first name, last
name, role, email address, etc), and an access token (which the website can
present to other services to convey permissions). The End User can visit Casa to
enroll additional credentials or to register an email address or SMS phone
number.

## Use Cases

### Registration

1. **Register for new account with CAC/PIV card**  If a person has a smart card,
they can present it during the registration process, and we should pick up the
subject DN which has their name and `edipi`.
1. **Register for new account (no CAC/PIV card)**  If the person does not
yet have a CAC/PIV card, we should enroll email and an SMS number.
1. **Associate a CAC card against existing account**  This use case is possible
when a person registered before they obtained a CAC/PIV, and then want to
associate their smart card with their account.
1. **Confirmation of OTP to verify email address**
   1. Email OTP should expire after 15 minutes
   1. An admin can disable OTP email confirmation
1. **Sponsor Approval**  In this use case, an authorized person logs into Casa
to see a list of people who enrolled. They must then approve each registration
manually.
1. **Registration for account with duplicate email** Do not allow.
1. **Required fields for registration**
1. **CAPTCHA**
1. **Password strength algorithm** Password policy should be customized.  
Example of some implemented password policy:  
"The minimum password length is 15 characters, containing at least one lowercase letter,
one uppercase letter, one number, and one special character".
1. **Valid email domain validation**.
1. **Disable automatic account enablement**  The Janssen Server admin can
restrict enrollment to certain domains.
1. **Redirect from Smart Card Login for unregistered person**.
1. **Signed Verification email** The Janssen Server must sign emails.

### Authentication

1. **email identifier** The end-user's email address is used for identification
(i.e. the email is the username).
1. **Smart Card**  The end user clicks on a button, which should prompt their
browser to enable the selection of an X.509 certificate.
1. **SMS**  After successful password authentication, and SMS message is sent
with a one time code, which the person must enter within a certain timeframe.
1. **Email**  After successful password authentication, an email is sent with a
one time code, which the person must enter within a certain timeframe.
1. **Forgot Password** An end user can trigger an email to reset their password.
1. **Email** Janssen Server sends a signed email to a person's email account.

### Credential Management

1. **Smart Card** The end user should be able to enroll a CAC/PIV card, and to
view the details of an associated X.509 certificate.
1. **SMS**  The end user should be able to view, add, and remove an associated
phone number to receive SMS notifications.
1. **Email** The end user should be able to view, add, and remove an associated
email account (as long as the domain is allowed).
1. **Change Password** End users should be able to change their password,
provided the new password meets the associated password complexity.

### Audit Logging

An audit log of all session activity should be stored in the LDAP server, under
the `o=metric` suffix. A sample record is here:

```text
dn=uniqueIdentifier={guid},ou={year-month},ou=audit,o=metric
objectclass: top
objectclass: oxMetric
uniqueIdentifier: {guid}
oxMetricType: audit
creationDate: {timestamp}
oxApplicationType: client_id
oxData: {“uid”:”foobar”,
          “edipi”:”1234567”,
          “type”: “startSession”,
          "redirect_uri": "https://abc.xyz/cb"
          "ip": "10.10.10.10",
          "acr": "smartcard",
          "session_id": "1234"}

```

### Restrict to single sessions

The Janssen Server should only allow an end-user to have one active session (web
or mobile). If an end-user logs in, previous sessions should be terminated in
the Janssen Server. Note: this does not imply that all applications will logout the
end-user at that time. However, if an OpenID Relying Party attempts to obtain a
token after the session has been revoked, the Janssen Server will re-authenticated
the person.

### Logout

1. **Logout from Casa**  On hitting the logout button, the person's browser
should logout.
1. **Logout from OpenID Connect relying party (RP)**  Provided the RP has a
properly configured OpenID Connect client in the Janssen Server, and that it makes
the correct front-channel logout call, the Person's browser should be logged out
of the website.

### User expiration

1. Users who do not login for ___ days should be removed from the system and
forced to re-register.  

# Installation

## RHEL 8 installation

### Base installation with DISA STIG Security Profile

If you are installing RHEL 8 from media:

* Under Software Selection, select `Minimal Install`

* Under Security Policy, select the `DISA STIG Security Policy`

* Enable networking and assign an **FQDN** hostname.

* Set the timezone

* Add a user with admin privileges (not `root`)

* You will need to create a custom disk layout. The following folders must be on
a separate partition or logical volume:

| mount point | Size |
| ----------- |------|
|`/tmp`| 1G|
|`/boot`| 500M|
|`/boot/efi`| 2G|
|`/home`| 3G|
|`/var`| 5G|
|`/var/log`| 3G|
|`/var/log/audit`| 2G|
|`/var/tmp`| 1G|
|`swap`| RAM Size|
|`/`| (the rest of the space)|

If you are using a cloud image, you can also apply the
[DISA-STIG](https://github.com/RedHatGov/rhel8-stig-latest)
settings by running the shell script provided by Red Hat,
`# bash rhel8-script-stig.sh`, and then rebooting.

### RHEL 8 Server Firewall

The RHEL 8 system firewall should be running. You can check with this
command:

```bash
systemctl status firewalld
```

Open the `https` and `http` service for public access (http just
redirects to https, but opening it prevents some user confusion)

```bash
firewall-cmd --zone=public --permanent --add-service=https
firewall-cmd --zone=public --permanent --add-service=http
```

```bash
firewall-cmd --reload
```

To get the current state of the firewall:

```bash
firewall-cmd --list-all
```

## Janssen Server Installation

This initial base configuration happens on Server 1-1. After the configuration
of 1-1 is complete, you will initialize the other servers.

### Install Janssen GPG Key

* Download **Janssen** key:

```bash
wget https://repo.gluu.org/rhel/RPM-GPG-KEY-GLUU -O /etc/pki/rpm-gpg/RPM-GPG-KEY-GLUU
```

* Install **Janssen** key:

```bash
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-GLUU
```

* List of installed public keys:

```bash
rpm -qa gpg-pubkey*
```

* Get info about installed **Janssen** key:

```bash
rpm -qi gpg-pubkey-0544ba38-572aa647
```

### Install Janssen Server RPM

### Janssen Server setup

After installing

### Janssen Server Verification

1. Check the version of the installed Jannsen components

```bash
python3 ./show_version.py

Title: jans-config-api-server-fips
Version: 1.0.7-SNAPSHOT
Builddate:
Build: a798e35dcf82de58a75d2299639b355300a79042

Title: SCIM API Server (FIPS)
Version: 1.0.7-SNAPSHOT
Builddate:
Build: a798e35dcf82de58a75d2299639b355300a79042

Title: Fido2 API Server (FIPS)
Version: 1.0.7-SNAPSHOT
Builddate:
Build: a798e35dcf82de58a75d2299639b355300a79042

Title: Jans authentication server (FIPS)
Version: 1.0.7-SNAPSHOT
Builddate:
Build: a798e35dcf82de58a75d2299639b355300a79042
```

1. Verify Janssen Server Access

* use these configuration endpoints for checking access:

[Auth Server / Authorization](https://docs.jans.io/v1.0.7/admin/auth-server/endpoints/authorization/)  
[Auth Server / Crypto Keys](https://docs.jans.io/v1.0.7/admin/auth-server/crypto/keys/)  
.

* use these admin tools for checking access:

[jans-cli Module Command line Admin Tool](https://docs.jans.io/v1.0.7/admin/config-guide/tui/)  
[jans_cli_tui Text User Interface Admin Tool](https://docs.jans.io/v1.0.7/admin/config-guide/tui/)  


<dl>
  <dt>Note:</dt>
  <dd>You need to allow https in the RHEL system firewall. You should
  have done this already (see above.)</dd>
</dl>

## PostgreSQL Server Configuration

