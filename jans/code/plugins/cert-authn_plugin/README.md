# Certificate Authentication Plugin
### Plugin allows enrollment and authentication via client certificates

Steps:

- Enable **ztrust-cert** custom script in **Janssen** (**config-cli-tui**).
- Log in to casa, in casa admin console, go to "Enabled authentication methods" from the menu. Select "ztrust-cert" as a 2fa method for authentication.
- Add the plugin jar file from the admin console
- Notice the newly created menu that reads "User Certificates" in the menu bar.