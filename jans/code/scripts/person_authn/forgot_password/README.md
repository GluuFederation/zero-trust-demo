# README Forgot Password

Name of the script in **oxTrust** (**identity**) *Configuration*/*Person Authentication Scripts*: **ztrust-forgot_password**.

Following are the configuration properties for the *forgot_password.py* script (**ztrust-forgot_password**):

Parameters of the script:

- **attributes_json_file_path**:

    Example of the attributes json file (defined by **attributes_json_file_path**):

```json
    {
        "ids": [
                "givenName",
                "sn",
                "familyName",
                "certificate",
                "captcha_elem"
            ],

        "passStrength": 2
    }
```

, where:  
**"ids"** - arrays of IDs of elements, that should be used, by **reg.xhtml**, **regtr.xhtml** pages;  
        here is the array, that contains all possible IDs:  

```text
    var allIds = [
        "givenName",
        "familyName",
        "sn",
        "certificate",
        "captcha_elem"
    ];
```

;  
You can customize array "ids", using necessary IDs, that should be filled/defined during registering;  
    "passStrength" - **Password Strength**;  
    There are follow levels:  

```text
            var strength = {
                0: "Worst ",
                1: "Bad ",
                2: "Weak ",
                3: "Good ",
                4: "Strong ",
            };
```

**"passStrength"** defines lower level of a password strength, that can be approved on pages: **reg.xhtml**, **regtr.xhtml**.  

- **regex_json_file_path**:

Example of the attributes json file (defined by **regex_json_file_path**):

```json
{
    "mail_regex": "^[a-zA-Z0-9\\.\\!\\#\\$\\%\\&\\'\\*\\+\\\\\/\\=\\?\\^\\_\\`\\{\\|\\}\\~\\-]+@(?:[a-zA-Z0-9]){1}(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
    "pass_regex": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[\\~\\`\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\-\\_\\+\\=\\{\\}\\[\\]\\|\\\\\/\\:\\;\\\"\\'\\<\\>\\,\\.\\?])[A-Za-z\\d\\~\\`\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\-\\_\\+\\=\\{\\}\\[\\]\\|\\\\\/\\:\\;\\\"\\'\\<\\>\\,\\.\\?]{15,}$"
}
```

, where:  
**"mail_regex"** - regular expression, that defines requiremets to an email, entered on pages: **reg.xhtml**, **regtr.xhtml**;  
For example, if we have follow requirement:  

```text
        **Valid email domain validation**
```

then follow "mail_regex" value should be used:  

```text
        ^[a-zA-Z0-9\.\!\#\$\%\&\'\*\+\\\/\=\?\^\_\`\{\|\}\~\-]+@(?:[a-zA-Z0-9]){1}(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$
```

;  
this value should be updated to follow format in attributes json file:  

```text
       ^[a-zA-Z0-9\\.\\!\\#\\$\\%\\&\\'\\*\\+\\\\\/\\=\\?\\^\\_\\`\\{\\|\\}\\~\\-]+@(?:[a-zA-Z0-9]){1}(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$
```

;  
**"pass_regex"** - regular expression, that defines additional requiremets to a password, entered on pages **reg.xhtml**, **regtr.xhtml**;  
For example, if we have follow requirement:  

```text
**Password strength algorithm**  The minimum password length is 15
characters, containing at least one lowercase letter, one uppercase letter, one
number, and one special character.
```

then follow "pass_regex" value should be used:  

```text
        ^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\~\`\!\@\#\$\%\^\&\*\(\)\-\_\+\=\{\}\[\]\|\\\/\:\;\"\'\<\>\,\.\?])[A-Za-z\d\~\`\!\@\#\$\%\^\&\*\(\)\-\_\+\=\{\}\[\]\|\\\/\:\;\"\'\<\>\,\.\?]{15,}$
```  

this value should be updated to follow format  in attributes json file:  

```text
        ^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[\\~\\`\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\-\\_\\+\\=\\{\\}\\[\\]\\|\\\\\/\\:\\;\\\"\\'\\<\\>\\,\\.\\?])[A-Za-z\\d\\~\\`\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\-\\_\\+\\=\\{\\}\\[\\]\\|\\\\\/\\:\\;\\\"\\'\\<\\>\\,\\.\\?]{15,}$
```

.

File **regex_json_file_path** can be updated manually or using plug-in **passw-policy_plugin**.

- **email_templates_json_file_path**:

This file contains parameters, which are used, during generation of validation email (this email will contain **OTP**).

Example of the attributes json file (defined by **email_templates_json_file_path**):

```json
{
    "email_subject": "Gluu Authentication Token",
    "email_msg_template": "Here is your token : %%otp%%"
}
```

, where:  
**"email_subject"** - text of email subject, that is sent, during registration;  
**"email_msg_template"** - template of text of email;

This template can use follow variables:

**%%otp%%** - OTP (one-time password/code).  

- **token_length**: Determines the length of the OTP sent to the user:
    + required parameter;
    + default value: not defined;
- **token_lifetime**: Determines how long the token is active:
    + required parameter;
    + default value: not defined;
- **SCRIPT_FUNCTION**: Determines if the script will execute for email 2FA or Forgot Password:
    + optional parameter;
    + default value: *forgot_password*;
- **Signer_Cert_KeyStore**: Filename of the keystore
    + optional parameter;
    + default value: value, defined in **oxTrust** (**identity**): *Configuration*/*Organization Configuration*/*SMTP Server Configuration*/*KeyStore File Path*;
        * for example: */etc/certs/smtp-keys.bcfks*;
- **Signer_Cert_KeyStorePassword**: keystore Password
    + optional parameter;
    + default value: value, defined in **oxTrust** (**identity**): *Configuration*/*Organization Configuration*/*SMTP Server Configuration*/*KeyStore Password*;
        * for example: *tRmJpb$1_&BzlEUC7*;
- **Signer_Cert_Alias**: Alias of the keystore.
    + optional parameter;
    + default value: value, defined in **oxTrust** (**identity**): *Configuration*/*Organization Configuration*/*SMTP Server Configuration*/*KeyStore Alias*;
        * for example: *smtp_sig_ec256*;
- **Signer_SignAlgorithm**: Name of signing algorithm
    + optional parameter;
    + default value: value, defined in **oxTrust** (**identity**): *Configuration*/*Organization Configuration*/*SMTP Server Configuration*/*Signing Algorithm*;
    + Default algorithm used to sign;
        * for example: *SHA256withECDSA*
