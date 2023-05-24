## README CAC card/Certificate Login

Following are the configuration properties for the *cert-authn_plugin.py* script (**ztrust-cert**):

- **credentials_file**: mandatory property pointing to credentials file in [json] format.

Example of the attributes json file (defined by **credentials_file**):

```json
{
    "recaptcha":{
        "enabled":false,
        "site_key":"",
        "secret_key":""
    }
}
```

- **crl_max_response_size**: specifies the maximum allowed size of [CRL][crl] response.
- **map_user_cert**: specifies if the script should map new user to local account.
- **use_crl_validator**: enable/disable specific certificate validation.
- **use_generic_validator**: enable/disable specific certificate validation
- **use_ocsp_validator**: enable/disable specific certificate validation.
- **use_path_validator**: enable/disable specific certificate validation.
- **chain_cert_file_path**: mandatory property pointing to certificate chains in [pem] format.
