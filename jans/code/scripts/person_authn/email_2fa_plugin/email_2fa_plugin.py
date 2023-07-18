from io.jans.as.server.service import AuthenticationService
from io.jans.as.server.service import UserService
from io.jans.as.server.auth import Authenticator
from io.jans.as.server.security import Identity
from io.jans.model.custom.script.type.auth import PersonAuthenticationType
from io.jans.service.cdi.util import CdiUtil
from io.jans.orm.util import StringHelper
from io.jans.as.server.util import ServerUtil
from io.jans.as.common.service.common import ConfigurationService
from io.jans.as.common.service.common import EncryptionService
from io.jans.jsf2.message import FacesMessages
from jakarta.faces.application import FacesMessage
from io.jans.orm.exception import AuthenticationException

from datetime import datetime, timedelta
from java.util import GregorianCalendar, TimeZone
from javax.activation import CommandMap
from io.jans.model import SmtpConnectProtectionType
from io.jans.util.security import SecurityProviderUtility

#Email Signing
from org.bouncycastle.asn1 import ASN1EncodableVector
from org.bouncycastle.asn1.cms import AttributeTable
from org.bouncycastle.asn1.cms import IssuerAndSerialNumber
from org.bouncycastle.asn1.smime import SMIMECapabilitiesAttribute
from org.bouncycastle.asn1.smime import SMIMECapability
from org.bouncycastle.asn1.smime import SMIMECapabilityVector
from org.bouncycastle.asn1.smime import SMIMEEncryptionKeyPreferenceAttribute
from org.bouncycastle.asn1.x500 import X500Name
from org.bouncycastle.cert.jcajce import JcaCertStore
from org.bouncycastle.cms import CMSAlgorithm
from org.bouncycastle.cms.jcajce import JcaSimpleSignerInfoGeneratorBuilder
from org.bouncycastle.cms.jcajce import JceCMSContentEncryptorBuilder
from org.bouncycastle.cms.jcajce import JceKeyTransRecipientInfoGenerator
from org.bouncycastle.mail.smime import SMIMEEnvelopedGenerator
from org.bouncycastle.mail.smime import SMIMESignedGenerator

#dealing with JKS
from java.security import KeyStore
from java.io import File
from java.io import FileInputStream
from java.util import Enumeration, Properties

#dealing with smtp server
from java.security import Security
from javax.mail.internet import MimeMessage, InternetAddress
from javax.mail import Session, Message, Transport

# This one is from core Java
from java.util import Arrays

# to generate string token
import random
import string

# regex
import re

import urllib
import java
import os.path

import json
import ast


class EmailValidator():
    '''
    Class to check e-mail format
    '''
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

    def check(self, email):
        '''
        Check if email format is valid
        returns: boolean
        '''

        if(re.search(self.regex,email)):
            print "Email 2FA - %s is a valid email format" % email
            return True
        else:
            print "Email 2FA - %s is an invalid email format" % email
            return False


class Token:
    #class that deals with string token

    def generateToken(self,lent):
        ''' method to generate token string
        returns: String
        '''
        letters = string.ascii_lowercase

        #token lenght
        lenght = 20

        #generate token
        rand1="1234567890123456789123456789"
        rand2="9876543210123456789123456789"

        first = int(rand1[:int(lent)])
        first1 = int(rand2[:int(lent)])
        token = random.randint(first, first1)
        print "Email 2FA - Generating token"

        return token


class PersonAuthentication(PersonAuthenticationType):

    sf = "email_2fa"
    jks_keystore = None
    keystore_password = None
    alias = None
    sign_alg = None

    def __init__(self, currentTimeMillis):
        self.currentTimeMillis = currentTimeMillis

    def init(self, customScript, configurationAttributes):

        sf_val = configurationAttributes.get("SCRIPT_FUNCTION")

        jks_keystore_val = configurationAttributes.get("Signer_Cert_KeyStore")
        keystore_password_val = configurationAttributes.get("Signer_Cert_KeyStorePassword")
        alias_val = configurationAttributes.get("Signer_Cert_Alias")
        sign_alg_val = configurationAttributes.get("Signer_SignAlgorithm")

        if sf_val != None:
            self.sf = sf_val.getValue2()

        if jks_keystore_val != None:
            self.jks_keystore = jks_keystore_val.getValue2()

        if keystore_password_val != None:
            self.keystore_password = keystore_password_val.getValue2()

        if alias_val != None:
            self.alias = alias_val.getValue2()

        if sign_alg_val != None:
            self.sign_alg = sign_alg_val.getValue2()

        if not (configurationAttributes.containsKey("email_templates_json_file_path")):
            print "Register. Initialization. Property email_templates_json_file_path is mandatory"
            return False

        self.email_templates_json_file_path = configurationAttributes.get(
            "email_templates_json_file_path").getValue2()

        print "Email 2FA - Initialized successfully"
        return True

    def destroy(self, configurationAttributes):
        print "Email 2FA - Destroyed successfully"
        return True

    def getApiVersion(self):
        # I'm not sure why is 11 and not 2
        return 11

    def isValidAuthenticationMethod(self, usageType, configurationAttributes):
        return True

    def getAuthenticationMethodClaims(self, configurationAttributes):
        return None

    def getAlternativeAuthenticationMethod(self, usageType, configurationAttributes):
        return None

    def authenticate(self, configurationAttributes, requestParameters, step):
        '''
        Authenticates user
        Step 1 will be defined according to SCRIPT_FUNCTION custom attribute
        returns: boolean
        '''

        print "Email 2FA - %s - Authenticate for step %s" % (self.sf, step)

        identity = CdiUtil.bean(Identity)
        credentials = identity.getCredentials()
        user_name = credentials.getUsername()
        user_password = credentials.getPassword()
        facesMessages = CdiUtil.bean(FacesMessages)
        facesMessages.setKeepMessages()

        if step == 1:

            if self.sf == "forgot_password":

                authenticationService = CdiUtil.bean(AuthenticationService)

                logged_in = authenticationService.authenticate(user_name, user_password)

                if not logged_in:

                    email = ServerUtil.getFirstValue(requestParameters, "ForgotPasswordForm:useremail")
                    validator = EmailValidator()
                    if not validator.check(email):
                        print "Email 2FA - Email format invalid"
                        return False

                    else:
                        print "Email 2FA -Email format valid"

                        print "Email 2FA - Entered email is %s" % email
                        identity.setWorkingParameter("useremail",email)

                        # Just trying to get the user by the email
                        user_service = CdiUtil.bean(UserService)
                        user2 = user_service.getUserByAttribute("mail", email)

                        if user2 is not None:

                            print user2
                            print "Email 2FA - User with e-mail %s found." % user2.getAttribute("mail")

                            # send email
                            lent = configurationAttributes.get("token_length").getValue2()
                            new_token = Token()
                            token = new_token.generateToken(lent)
                            sender = EmailSender()
                            print "Email: %s" % email
                            print "Token: %d" % token

                            fmt_dict = {
                                "%%otp%%": str(token)
                            }

                            email_subject, email_msg_template = self.getEmailParameters()

                            print "email_subject = %s" % email_subject
                            print "email_msg_template = %s" % email_msg_template

                            body = ""
                            if isinstance(email_msg_template, (list, tuple)):
                                for template_line in email_msg_template:
                                    body += self.formatLine(template_line, fmt_dict)
                            if isinstance(email_msg_template, str):
                                body += self.formatLine(email_msg_template, fmt_dict)
                            print "body = %s" % body

#                            subject = "Janssen Authentication Token" #subject
#                            body = "Here is your token: %s" % token

                            sender.sendEmail(self.alias, self.jks_keystore, self.keystore_password, self.sign_alg, email, email_subject, body)

                            otptime1 = datetime.now()

                            tess = str(otptime1)

                            listee = tess.split(':')

                            identity.setWorkingParameter("sentmin", listee[1])
                            identity.setWorkingParameter("useremail",email)
                            identity.setWorkingParameter("token", token)

                        else:
                            print "Email 2FA - User with e-mail %s not found" % email

                        return True

                else:
                    # if user is already authenticated, returns true.

                    user = authenticationService.getAuthenticatedUser()
                    print "Email 2FA - User %s is authenticated" % user.getUserId()

                    return True

            if self.sf == "email_2fa":

                try:
                    # Just trying to get the user by the uid

                    authenticated_user = self.processBasicAuthentication(credentials)

                    if authenticated_user == None:
                        return False

                    print 'email_2FA user_name: ' + str(authenticated_user.getUserId())

                    user_service = CdiUtil.bean(UserService)
                    user2 = user_service.getUserByAttribute("uid", user_name)

                    if user2 is not None:

                        print "user:"
                        print user2
                        print "Email 2FA - User with e-mail %s found." % user2.getAttribute("mail")
                        email = user2.getAttribute("mail")
                        uid = user2.getAttribute("uid")

                        # send token
                        # send email
                        lent = configurationAttributes.get("token_length").getValue2()
                        new_token = Token()
                        token = new_token.generateToken(lent)
                        print "Email: %s" % email
                        print "Token: %d" % token

                        fmt_dict = {
                            "%%otp%%": str(token)
                        }

                        email_subject, email_msg_template = self.getEmailParameters()

                        print "email_subject = %s" % email_subject
                        print "email_msg_template = %s" % email_msg_template

                        body = ""
                        if isinstance(email_msg_template, (list, tuple)):
                            for template_line in email_msg_template:
                                body += self.formatLine(template_line, fmt_dict)
                        if isinstance(email_msg_template, str):
                            body += self.formatLine(email_msg_template, fmt_dict)
                        print "body = %s" % body

#                        subject = "Janssen Authentication Token" #subject
#                        body = "Here is your token: %s" % token

                        sender = EmailSender()
                        sender.sendEmail(self.alias, self.jks_keystore, self.keystore_password, self.sign_alg, email, email_subject, body)

                        #### Email Signing Code End ####

                        otptime1 = datetime.now()

                        tess = str(otptime1)

                        listee = tess.split(':')

                        identity.setWorkingParameter("sentmin", listee[1])
                        identity.setWorkingParameter("useremail",email)
                        identity.setWorkingParameter("token", token)

                        return True

                except AuthenticationException as err:
                    print err
                    return False

        if step == 2:
            # step 2 user enters token
            credentials = identity.getCredentials()
            user_name = credentials.getUsername()
            user_password = credentials.getPassword()

            authenticationService = CdiUtil.bean(AuthenticationService)
            logged_in = authenticationService.authenticate(user_name, user_password)

            # retrieves token typed by user
            input_token = ServerUtil.getFirstValue(requestParameters, "ResetTokenForm:inputToken")

            print "Email 2FA - Token inputed by user is %s" % input_token

            token = str(identity.getWorkingParameter("token"))
            print "Email 2FA - Retrieved token"
            email = identity.getWorkingParameter("useremail")
            print "Email 2FA - Retrieved email"

            min11 = int(identity.getWorkingParameter("sentmin"))

            nww = datetime.now()

            te = str(nww)

            listew = te.split(':')

            curtime = int(listew[1])

            token_lifetime = int(configurationAttributes.get("token_lifetime").getValue2())
            if ((min11<= 60) and (min11>= 50)):
                if ((curtime>=50) and (curtime<=60)):
                    timediff1 =  curtime -  min11
                    if timediff1>token_lifetime:
                        #print "OTP Expired"
                        facesMessages.add(FacesMessage.SEVERITY_ERROR, "OTP Expired")
                        return False
                elif ((curtime>=0) or (curtime<=10)):
                    timediff1 = 60 - min11
                    timediff1 =  timediff1 + curtime
                    if timediff1>token_lifetime:
                        #print "OTP Expired"
                        facesMessages.add(FacesMessage.SEVERITY_ERROR, "OTP Expired")
                        return False

            if ((min11>=0) and (min11<=60) and (curtime>=0) and (curtime<=60)):
                timediff2 = curtime - min11
                if timediff2>token_lifetime:
                    #print "OTP Expired"
                    facesMessages.add(FacesMessage.SEVERITY_ERROR, "OTP Expired")
                    return False
            # compares token sent and token entered by user
            if input_token == token:
                print "Email 2FA - token entered correctly"
                identity.setWorkingParameter("token_valid", True)

                return True

            else:
                print "Email 2FA - wrong token"
                return False

        if step == 3:
            # step 3 enters new password (only runs if custom attibute is forgot_password

            user_service = CdiUtil.bean(UserService)

            email = identity.getWorkingParameter("useremail")
            user2 = user_service.getUserByAttribute("mail", email)

            user_name = user2.getUserId()

            new_password = ServerUtil.getFirstValue(requestParameters, "UpdatePasswordForm:newPassword")

            print "Email 2FA - New password submited"

            # update user info with new password
            user2.setAttribute("userPassword",new_password)

            user_service.updateUser(user2)

            # authenticates and login user
            authenticationService2 = CdiUtil.bean(AuthenticationService)
            login = authenticationService2.authenticate(user_name, new_password)

            return True

    def prepareForStep(self, configurationAttributes, requestParameters, step):
        print "Email 2FA - Preparing for step %s" % step
        return True

    # Return value is a java.util.List<String>
    def getExtraParametersForStep(self, configurationAttributes, step):
        return Arrays.asList("token","useremail","token_valid","sentmin")
    #return None


    # This method determines how many steps the authentication flow may have
    # It doesn't have to be a constant value
    def getCountAuthenticationSteps(self, configurationAttributes):

        # if option is forgot_token
        if self.sf == "forgot_password":
            print "Entered sf == forgot_password"
            return 3

        # if ption is email_2FA
        if self.sf == "email_2fa":
            print "Entered if sf=email_2fa"
            return 2

        else:
            print "Email 2FA - Custom Script Custom Property Incorrect, please check"


    # The xhtml page to render upon each step of the flow
    # returns a string relative to jans-auth webapp root
    def getPageForStep(self, configurationAttributes, step):

        if step == 1:
            if self.sf == "forgot_password":
                return "/auth/forgot_password/forgot.xhtml"

        if step == 2:
            if self.sf == "forgot_password":
                return "/auth/forgot_password/entertoken.xhtml"            

            if self.sf == "email_2fa":
                return "/auth/email_auth/entertoken.xhtml"

        if step == 3:
            if self.sf == "forgot_password":
                return "/auth/forgot_password/newpassword.xhtml"

        return ""

    def getNextStep(self, configurationAttributes, requestParameters, step):
        # Method used on version 2 (11?)
        return -1


    def logout(self, configurationAttributes, requestParameters):
        return True

    def hasEnrollments(self, configurationAttributes, user):
        return True

    def processBasicAuthentication(self, credentials):
        userService = CdiUtil.bean(UserService)
        authenticationService = CdiUtil.bean(AuthenticationService)

        user_name = credentials.getUsername()
        user_password = credentials.getPassword()

        logged_in = False
        if StringHelper.isNotEmptyString(user_name) and StringHelper.isNotEmptyString(user_password):
            logged_in = authenticationService.authenticate(user_name, user_password)

        if not logged_in:
            return None

        find_user_by_uid = authenticationService.getAuthenticatedUser()

        if find_user_by_uid == None:
            print "Email-2FA - Process basic authentication. Failed to find user '%s'" % user_name
            return None

        return find_user_by_uid

    def getEmailParameters(self):
        f = open(self.email_templates_json_file_path)
        data = json.load(f)
        data = ast.literal_eval(json.dumps(data))

        email_subject = data["email_subject"]
        email_msg_template = data["email_msg_template"]

        print "email_subject = %s" % email_subject
        print "type(email_msg_template) = %s" % type(email_msg_template)

        return email_subject, email_msg_template

    def formatLine(self, line, fmt_dict):

        for item in fmt_dict.items():
            line = line.replace(item[0], item[1])

        return line


#### Email Signing Code Begin ####

class EmailSender():
    #class that sends e-mail through smtp

    time_out = 5000

    def __init__(self):
        mc = CommandMap.getDefaultCommandMap()

        mc.addMailcap("text/html;; x-java-content-handler=com.sun.mail.handlers.text_html")
        mc.addMailcap("text/xml;; x-java-content-handler=com.sun.mail.handlers.text_xml")
        mc.addMailcap("text/plain;; x-java-content-handler=com.sun.mail.handlers.text_plain")
        mc.addMailcap("multipart/*;; x-java-content-handler=com.sun.mail.handlers.multipart_mixed")
        mc.addMailcap("message/rfc822;; x-java-content- handler=com.sun.mail.handlers.message_rfc822")

    def getSmtpConfig(self):
        '''
        get SMTP config from Jansse Server
        return dict
        '''

        smtpconfig = CdiUtil.bean(ConfigurationService).getConfiguration().getSmtpConfiguration()

        if smtpconfig is None:
            print "Sign Email - SMTP CONFIG DOESN'T EXIST - Please configure"

        else:
            print "Sign Email - SMTP CONFIG FOUND"
            encryptionService = CdiUtil.bean(EncryptionService)
            smtp_config = {
                'host' : smtpconfig.getHost(),
                'port' : smtpconfig.getPort(),
                'user' : smtpconfig.getSmtpAuthenticationAccountUsername(),
                'from' : smtpconfig.getFromEmailAddress(),
                'pwd_decrypted' : encryptionService.decrypt(smtpconfig.getSmtpAuthenticationAccountPassword()),
                'connect_protection' : smtpconfig.getConnectProtection(),
                'requires_authentication' : smtpconfig.isRequiresAuthentication(),
                'server_trust' : smtpconfig.isServerTrust(),

                'key_store' : smtpconfig.getKeyStore(),
                'key_store_password' : encryptionService.decrypt(smtpconfig.getKeyStorePassword()),
                'key_store_alias' : smtpconfig.getKeyStoreAlias(),
                'signing-algorithm' : smtpconfig.getSigningAlgorithm()
            }

        return smtp_config

    def signMessage(self, alias, jksKeyStore, keyStorePassword, signingAlgorithm, message):

        isAliasWithPrivateKey = False

        keystore_ext = self.getExtension(jksKeyStore)

        print "EmailSender.  - signMessage - keystore_ext = %s" % keystore_ext

        if keystore_ext.lower() == ".jks":
            keyStore = KeyStore.getInstance("JKS", SecurityProviderUtility.getBCProvider())

        elif keystore_ext.lower() == ".pkcs12":
            keyStore = KeyStore.getInstance("PKCS12", SecurityProviderUtility.getBCProvider())

        elif keystore_ext.lower() == ".bcfks":
            keyStore = KeyStore.getInstance("BCFKS", SecurityProviderUtility.getBCProvider())

        file = File(jksKeyStore)
        keyStore.load(FileInputStream(file), list(keyStorePassword))
        es = keyStore.aliases()

        while (es.hasMoreElements()):
            alias = es.nextElement()
            if (keyStore.isKeyEntry(alias)):
                isAliasWithPrivateKey = True
                break

        if (isAliasWithPrivateKey):
            pkEntry = keyStore.getEntry(alias,KeyStore.PasswordProtection(list(keyStorePassword)))
            privateKey = pkEntry.getPrivateKey()

        chain = keyStore.getCertificateChain(alias)

        publicKey = chain[0]

        certificate = keyStore.getCertificate(alias)

        sign_algorithm = None

        if not signingAlgorithm or not signingAlgorithm.strip():
            sign_algorithm = certificate.getSigAlgName()
        else:
            sign_algorithm = signingAlgorithm

        # Create the SMIMESignedGenerator
        capabilities = SMIMECapabilityVector()
        capabilities.addCapability(SMIMECapability.dES_EDE3_CBC)
        capabilities.addCapability(SMIMECapability.rC2_CBC, 128)
        capabilities.addCapability(SMIMECapability.dES_CBC)
        capabilities.addCapability(SMIMECapability.aES256_CBC)

        attributes = ASN1EncodableVector()
        attributes.add(SMIMECapabilitiesAttribute(capabilities))

        issAndSer = IssuerAndSerialNumber(X500Name(publicKey.getIssuerDN().getName()),publicKey.getSerialNumber())

        attributes.add(SMIMEEncryptionKeyPreferenceAttribute(issAndSer))

        signer = SMIMESignedGenerator()

        signer.addSignerInfoGenerator(JcaSimpleSignerInfoGeneratorBuilder().setProvider(SecurityProviderUtility.getBCProvider()).setSignedAttributeGenerator(AttributeTable(attributes)).build(sign_algorithm, privateKey, publicKey))

        # Add the list of certs to the generator
        bcerts = JcaCertStore(Arrays.asList(chain))
        signer.addCertificates(bcerts)

        # Sign the message
        mm = signer.generate(message)

        # Set the content of the signed message
        message.setContent(mm, mm.getContentType())
        message.saveChanges()

        print "Sign Email - Message Signed"

        return message

    def sendEmail(self, keyStoreAlias, jksKeyStore, keyStorePassword, signingAlgorithm, useremail, subject, messageText):
        '''
        send token by e-mail to useremail
        '''

        # server connection
        smtp_config = self.getSmtpConfig()

        properties = Properties()

        properties.put("mail.from", "Casa")

        smtp_connect_protect = smtp_config['connect_protection']

        if smtp_connect_protect == SmtpConnectProtectionType.START_TLS:

            properties.put("mail.transport.protocol", "smtp")

            properties.put("mail.smtp.host", smtp_config['host'])
            properties.put("mail.smtp.port", str(smtp_config['port']))
            properties.put("mail.smtp.connectiontimeout", str(self.time_out))
            properties.put("mail.smtp.timeout", str(self.time_out))

            properties.put("mail.smtp.socketFactory.class", "com.sun.mail.util.MailSSLSocketFactory")
            properties.put("mail.smtp.socketFactory.port", str(smtp_config['port']))

            if smtp_config['server_trust'] == True:
                properties.put("mail.smtp.ssl.trust", smtp_config['host'])

            properties.put("mail.smtp.starttls.enable", "true")
            properties.put("mail.smtp.starttls.required", "true")

        elif smtp_connect_protect == SmtpConnectProtectionType.SSL_TLS:

            properties.put("mail.transport.protocol.rfc822", "smtps")

            properties.put("mail.smtp.host", smtp_config['host'])
            properties.put("mail.smtp.port", str(smtp_config['port']))
            properties.put("mail.smtp.connectiontimeout", str(self.time_out))
            properties.put("mail.smtp.timeout", str(self.time_out))

            properties.put("mail.smtp.socketFactory.class", "com.sun.mail.util.MailSSLSocketFactory")
            properties.put("mail.smtp.socketFactory.port", str(smtp_config['port']))

            if smtp_config['server_trust'] == True:
                properties.put("mail.smtp.ssl.trust", smtp_config['host'])

            properties.put("mail.smtp.ssl.enable", "true")

        session = Session.getDefaultInstance(properties)

        message = MimeMessage(session)
        message.setFrom(InternetAddress(smtp_config['from']))
        message.addRecipient(Message.RecipientType.TO,InternetAddress(useremail))
        message.setSubject(subject)
        message.setContent(messageText, "text/html")

        jks_keystore = None
        keystore_password = None
        alias = None
        sign_alg = None

        if jksKeyStore != None and len(jksKeyStore) > 0:
            jks_keystore = jksKeyStore
        else:
            jks_keystore = smtp_config['key_store']

        if keyStorePassword != None and len(keyStorePassword) > 0:
            keystore_password = keyStorePassword
        else:
            keystore_password = smtp_config['key_store_password']

        if keyStoreAlias != None and len(keyStoreAlias) > 0:
            alias = keyStoreAlias
        else:
            alias = smtp_config['key_store_alias']

        if signingAlgorithm != None and len(signingAlgorithm) > 0:
            sign_alg = signingAlgorithm
        else:
            sign_alg = smtp_config['signing-algorithm']

        print "Sign Email - Message Prepared"

        signMessage = self.signMessage(alias, jks_keystore, keystore_password, sign_alg, message)

        if smtp_connect_protect == SmtpConnectProtectionType.START_TLS:
            transport = session.getTransport("smtp")

        elif smtp_connect_protect == SmtpConnectProtectionType.SSL_TLS:
            transport = session.getTransport("smtps")

        transport.connect(properties.get("mail.smtp.host"),int(properties.get("mail.smtp.port")), smtp_config['user'], smtp_config['pwd_decrypted'])
        transport.sendMessage(signMessage,signMessage.getRecipients(Message.RecipientType.TO))

        print "Sign Email - Message Sent"

        transport.close()

    def getExtension(self, file_path):
        file_name_with_ext = os.path.basename(file_path)
        file_name, ext = os.path.splitext(file_name_with_ext)
        return ext

#### Email Signing Code End ####
