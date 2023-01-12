
## Example of tuning of Auth Scripts:

-----------------------------------------------------------------------------------------------

### **ztrust-cert**

ztrust-cert  

Following are the configuration properties for the *cert.py* script:  

|Propery | Value|
|------| --------- |
| credentials_file      |  /etc/certs/cert_creds.json  |
| crl_max_response_size |  5242880                     |
| map_user_cert         |  true                        |
| use_crl_validator     |  false                       |
| use_generic_validator |  true                        |
| use_ocsp_validator    |  true                        |
| use_path_validator    |  true                        |
| chain_cert_file_path  |  /etc/certs/ztrust.chain     |

-----------------------------------------------------------------------------------------------

### **ztrust-email_2fa_plugin**

ztrust-email_2fa_plugin  

Following are the configuration properties for the *email_2fa_plugin.py* script:  

|Propery | Value|
|------| --------- |
| email_templates_json_file_path    | /etc/gluu/conf/ztrust-email-email_2fa.json    |
| token_length                      | 7                                             |
| token_lifetime                    | 15                                            |  
| SCRIPT_FUNCTION                   | email_2fa                                     |

-----------------------------------------------------------------------------------------------

### **ztrust-forgot_password**

ztrust-forgot_password  

Following are the configuration properties for the *forgot_password.py* script:  

|Propery | Value|
|------| --------- |
| attributes_json_file_path         | /etc/gluu/conf/ztrust-attributes.json             |
| regex_json_file_path              | /etc/gluu/conf/ztrust-regex.json                  |
| email_templates_json_file_path    | /etc/gluu/conf/ztrust-email-forgot_password.json  |
| token_length                      | 7                                                 |
| token_lifetime                    | 15                                                |
| SCRIPT_FUNCTION                   | forgot_password                                   |

-----------------------------------------------------------------------------------------------

### **ztrust-register**

ztrust-register  

Following are the configuration properties for the *register.py* script:  

|Propery | Value|
|------| --------- |
| attributes_json_file_path         | /etc/gluu/conf/ztrust-attributes.json             |
| regex_json_file_path              | /etc/gluu/conf/ztrust-regex.json                  |
| email_templates_json_file_path    | /etc/gluu/conf/ztrust-email-register.json         |
| crl_max_response_size             | 5242880                                           |
| use_crl_validator                 | false                                             |
| use_generic_validator             | true                                              |
| use_ocsp_validator                | true                                              |
| use_path_validator                | true                                              |
| chain_cert_file_path              | /etc/certs/ztrust.chain                           |
| token_length                      | 7                                                 |
| token_lifetime                    | 15                                                |
| Enable_User                       | true                                              |
| Require_Email_Confirmation        | true                                              |

-----------------------------------------------------------------------------------------------
