## README Auditing Authentication Attempts

*application_session.py* is application session script used for auditing login attempts of the user.

**ztrust-application_session**  

**metric_audit_ou_name**: Name of the audit OU.*(Logaudit)*  

**metric_audit_conf_json_file_path**: configuration file (for example): **/etc/jans/conf/ztrust-metric-audit.json**  

```json
{
    "event_types": [ "AUTHENTICATED", "UNAUTHENTICATED", "UPDATED", "GONE" ],
    "audit_data": [ 
        "id",
        "outsideSid",
        "lastUsedAt",
        "authenticationTime",
        "state",
        "expirationDate",
        "sessionState",
        "permissionGranted",
        "permissionGrantedMap",
        "deviceSecrets",

        "sessionAttributes"
    ]    
}
```

or

```json
{
    "event_types": [ "AUTHENTICATED", "UNAUTHENTICATED", "UPDATED", "GONE" ],
    "audit_data": [ 
        "id",
        "outsideSid",
        "lastUsedAt",
        "authenticationTime",
        "state",
        "expirationDate",
        "sessionState",
        "permissionGranted",
        "permissionGrantedMap",
        "deviceSecrets",

        "auth_external_attributes",
        "opbs",
        "response_type",
        "client_id",
        "auth_step",
        "acr",
        "casa_logoUrl",
        "remote_ip",
        "scope",
        "acr_values",
        "casa_faviconUrl",
        "redirect_uri",
        "state",
        "casa_prefix",
        "casa_contextPath",
        "casa_extraCss"
    ]
}
```

**"sessionAttributes"** defines follow attributes:  

```text

"sessionAttributes":

        "auth_external_attributes",
        "opbs",
        "response_type",
        "client_id",
        "auth_step",
        "acr",
        "casa_logoUrl",
        "remote_ip",
        "scope",
        "acr_values",
        "casa_faviconUrl",
        "redirect_uri",
        "state",
        "casa_prefix",
        "casa_contextPath",
        "casa_extraCss"

```

.
