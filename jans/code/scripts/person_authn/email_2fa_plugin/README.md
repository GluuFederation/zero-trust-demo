# README Email 2fa Plugin

Name of the script in **janssen** (for example, using **/opt/jans/jans-cli/config-cli.py** or **/opt/jans/jans-cli/config-cli-tui.py**).

Following are the configuration properties for the *email_2fa_plugin.py* script (**ztrust-email_2fa_plugin**):

Parameters of the script:

- **email_templates_json_file_path**:

This file contains parameters, which are used, during generation of validation email (this email will contain **OTP**).

Example of the attributes json file (defined by **email_templates_json_file_path**):

```json
{
    "email_subject": "Janssen Authentication Token",
    "email_msg_template": "Here is your token : %%otp%%"
}
```

, where:  
**"email_subject"** - text of email subject, that is sent, during registration;  
**"email_msg_template"** - template of text of email;

This template can use follow variables:

**%%otp%%** - OTP (one-time password/code).  

- **token_length**:     It determines the length of the characters of the One time Password sent to the user:
    + required parameter;
    + default value: not defined;
- **token_lifetime**:   It determines the time period for which the sent token is active:
    + required parameter;
    + default value: not defined;
- **SCRIPT_FUNCTION**: It determines if the script will execute for email 2FA or Forgot Password:
    + nonrequired parameter;
    + default value: *email_2fa*;
- **Signer_Cert_KeyStore**: Filename of the Keystore
    + nonrequired parameter;
    + default value: value, defined in **Janssen** (**/opt/jans/jans-cli/config-cli-tui.py**): *SMTP*/*KeyStore*;
        * for example: */etc/certs/smtp-keys.bcfks*;
- **Signer_Cert_KeyStorePassword**: Keystore Password
    + nonrequired parameter;
    + default value: value, defined in **Janssen** (**/opt/jans/jans-cli/config-cli-tui.py**): *SMTP*/*KeyStore Password*;
        * for example: *tRmJpb$1_&BzlEUC7*;
- **Signer_Cert_Alias**: Alias of the Keystore.
    + nonrequired parameter;
    + default value: value, defined in **Janssen** (**/opt/jans/jans-cli/config-cli-tui.py**): *SMTP*/*KeyStore Alias*;
        * for example: *smtp_sig_ec256*;
- **Signer_SignAlgorithm**: Name of Signing Algorithm
    + nonrequired parameter;
    + default value: value, defined in **Janssen** (**/opt/jans/jans-cli/config-cli-tui.py**): *SMTP*/*KeyStore Algorithm*;
    + by default algirithm is used by signing of certificate from the Keystore;
        * for example: *SHA256withECDSA*
