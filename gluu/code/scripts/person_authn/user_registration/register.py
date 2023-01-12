from org.gluu.oxauth.model.common import ZTrustPerson, WebKeyStorage
from org.gluu.service.cdi.util import CdiUtil
from org.gluu.oxauth.security import Identity
from org.gluu.model import GluuStatus

from org.gluu.model.custom.script.type.auth import PersonAuthenticationType
from org.gluu.oxauth.service import UserService, AuthenticationService

from org.gluu.oxauth.service.common import ConfigurationService
from org.gluu.oxauth.service.common import EncryptionService

from org.gluu.oxauth.util import ServerUtil
from org.gluu.util import StringHelper, ArrayHelper
from java.util import Arrays
from javax.faces.application import FacesMessage
from org.gluu.jsf2.message import FacesMessages
from org.gluu.jsf2.service import FacesService

from org.gluu.service import MailService

# cert
from org.gluu.oxauth.cert.fingerprint import FingerprintHelper
from org.gluu.oxauth.cert.validation import GenericCertificateVerifier, PathCertificateVerifier, OCSPCertificateVerifier, CRLCertificateVerifier
from org.gluu.oxauth.cert.validation.model import ValidationStatus
from org.gluu.oxauth.util import CertUtil
from org.gluu.oxauth.model.util import CertUtils
from org.gluu.oxauth.service.net import HttpService
from org.apache.http.params import CoreConnectionPNames
from datetime import datetime, timedelta
from java.util import GregorianCalendar, TimeZone

from javax.faces.context import FacesContext
import org.codehaus.jettison.json.JSONArray as JSONArray

from javax.activation import CommandMap

from org.gluu.model import SmtpConnectProtectionType
from org.gluu.util.security import SecurityProviderUtility

import json
import ast
import java
import random
import jarray
import smtplib

import sys
import base64
import urllib
import re
import os.path

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


class PersonAuthentication(PersonAuthenticationType):

    jks_keystore = None
    keystore_password = None
    alias = None
    sign_alg = None

    def __init__(self, currentTimeMillis):
        self.currentTimeMillis = currentTimeMillis
        self.emailid = None
        self.identity = CdiUtil.bean(Identity)

    def init(self, customScript, configurationAttributes):

        print "Register. Initialization"
        
        jks_keystore_val = configurationAttributes.get("Signer_Cert_KeyStore")
        keystore_password_val = configurationAttributes.get("Signer_Cert_KeyStorePassword")
        alias_val = configurationAttributes.get("Signer_Cert_Alias")
        sign_alg_val = configurationAttributes.get("Signer_SignAlgorithm")

        if jks_keystore_val != None:
            self.jks_keystore = jks_keystore_val.getValue2()

        if keystore_password_val != None:
            self.keystore_password = keystore_password_val.getValue2()

        if alias_val != None:
            self.alias = alias_val.getValue2()

        if sign_alg_val != None:
            self.sign_alg = sign_alg_val.getValue2()        

        if not (configurationAttributes.containsKey("attributes_json_file_path")):
            print "Register. Initialization. Property attributes_json_file_path is mandatory"
            return False

        self.attributes_json_file_path = configurationAttributes.get(
            "attributes_json_file_path").getValue2()

        if not (configurationAttributes.containsKey("regex_json_file_path")):
            print "Register. Initialization. Property regex_json_file_path is mandatory"
            return False

        self.regex_json_file_path = configurationAttributes.get(
            "regex_json_file_path").getValue2()

        if not (configurationAttributes.containsKey("email_templates_json_file_path")):
            print "Register. Initialization. Property email_templates_json_file_path is mandatory"
            return False

        self.email_templates_json_file_path = configurationAttributes.get(
            "email_templates_json_file_path").getValue2()

        if not (configurationAttributes.containsKey("chain_cert_file_path")):
            print "Register. Initialization. Property chain_cert_file_path is mandatory"
            return False

        self.chain_cert_file_path = configurationAttributes.get("chain_cert_file_path").getValue2()

        self.chain_certs = CertUtil.loadX509CertificateFromFile(self.chain_cert_file_path)
        if self.chain_certs == None:
            print "Register. Initialization. Failed to load chain certificates from '%s'" % chain_cert_file_path
            return False

        print "Register. Initialization. Loaded '%d' chain certificates" % self.chain_certs.size()

        crl_max_response_size = 5 * 1024 * 1024  # 5Mb
        if configurationAttributes.containsKey("crl_max_response_size"):
            crl_max_response_size = StringHelper.toInteger(configurationAttributes.get(
                "crl_max_response_size").getValue2(), crl_max_response_size)
            print "Register. Initialization. CRL max response size is '%d'" % crl_max_response_size

        # Define array to order methods correctly
        self.validator_types = ['generic', 'path', 'ocsp', 'crl']
        self.validators = {'generic': [GenericCertificateVerifier(), False],
                           'path': [PathCertificateVerifier(False), False],
                           'ocsp': [OCSPCertificateVerifier(), False],
                           'crl': [CRLCertificateVerifier(crl_max_response_size), False]}

        for type in self.validator_types:
            validator_param_name = "use_%s_validator" % type
            if configurationAttributes.containsKey(validator_param_name):
                validator_status = StringHelper.toBoolean(
                    configurationAttributes.get(validator_param_name).getValue2(), False)
                self.validators[type][1] = validator_status

            print "Register. Initialization. Validation method '%s' status: '%s'" % (type, self.validators[type][1])

        print "Register. Initialized successfully"

        return True

    def destroy(self, configurationAttributes):
        print "Register. Destroy"
        print "Register. Destroyed successfully"
        return True

    def getApiVersion(self):
        return 11

    def isValidAuthenticationMethod(self, usageType, configurationAttributes):
        return True

    def getAlternativeAuthenticationMethod(self, usageType, configurationAttributes):
        return None

    def authenticate(self, configurationAttributes, requestParameters, step):
        print "inside authenticateeeee"
        userService = CdiUtil.bean(UserService)
        identity = CdiUtil.bean(Identity)
        authenticationService = CdiUtil.bean(AuthenticationService)

        facesMessages = CdiUtil.bean(FacesMessages)
        facesMessages.setKeepMessages()

        facesService = CdiUtil.bean(FacesService)

        session_attributes = self.identity.getSessionId().getSessionAttributes()
        form_passcode = ServerUtil.getFirstValue(requestParameters, "passcode")
        form_name = ServerUtil.getFirstValue(requestParameters, "RegisterloginForm")
        cert = None
        print "Register. form_response_passcode: %s" % str(form_passcode)

        if step == 1:
            print "inside step 1"
            ufnm = str(ServerUtil.getFirstValue(requestParameters, "fnm"))
            ulnm = str(ServerUtil.getFirstValue(requestParameters, "lnm"))
            umnm = str(ServerUtil.getFirstValue(requestParameters, "mnm"))
            umail = str(ServerUtil.getFirstValue(requestParameters, "email"))
            upass = str(ServerUtil.getFirstValue(requestParameters, "pass"))
            urepass = str(ServerUtil.getFirstValue(requestParameters, "repass"))
            cert = ServerUtil.getFirstValue(requestParameters, "cert")
            certString = str(ServerUtil.getFirstValue(requestParameters, "certString"))
            upassd=ServerUtil.getFirstValue(requestParameters, "pass")

            identity.setWorkingParameter("vufnm", ufnm)
            identity.setWorkingParameter("vulnm", ulnm)
            identity.setWorkingParameter("vumnm", umnm)
            identity.setWorkingParameter("vumail", umail)
            identity.setWorkingParameter("vupass", upass)
            identity.setWorkingParameter("vurepass", urepass)

            #Check If user exists
            userByMail = None
            userByMail = userService.getUserByAttribute("mail", umail)
            if userByMail is not None:
                facesMessages.add(FacesMessage.SEVERITY_ERROR, "User with same email exists.")
                return False
            # Generate Random six digit code and store it in array
            code = random.randint(100000, 999999)

            # Get code and save it in LDAP temporarily with special session entry

            identity.setWorkingParameter("code", code)

            return True;

        elif step == 2:
            print "step 2"
            rand1="1234567890123456789123456789"
            rand2="9876543210123456789123456789"
            lent = configurationAttributes.get("token_length").getValue2()
            first = int(rand1[:int(lent)])
            first1 = int(rand2[:int(lent)])
            code = random.randint(first, first1)
            identity.setWorkingParameter("code", code)

            ufnm = str(ServerUtil.getFirstValue(requestParameters, "fnm"))
            ulnm = str(ServerUtil.getFirstValue(requestParameters, "lnm"))
            umnm = str(ServerUtil.getFirstValue(requestParameters, "mnm"))
            umail = str(ServerUtil.getFirstValue(requestParameters, "email"))
            upass = str(ServerUtil.getFirstValue(requestParameters, "pass"))
            upassd=ServerUtil.getFirstValue(requestParameters, "pass")
            urepass = str(ServerUtil.getFirstValue(requestParameters, "repass"))

            certDN = session_attributes.get("certDN")
            if certDN is not None:
                certCNs = self.getCNFromDN(certDN)
                if certCNs is not None:
                    i = 0
                    while i < len(certCNs):
                        if len(certCNs[i]) > 0:
                            if i == 0:
                                ulnm = certCNs[i]
                            elif i == 1:
                                ufnm = certCNs[i]
                            elif i == 2:
                                umnm = certCNs[i]
                        i += 1

            identity.setWorkingParameter("vufnm", ufnm)
            identity.setWorkingParameter("vulnm", ulnm)
            identity.setWorkingParameter("vumnm", umnm)
            identity.setWorkingParameter("vumail", umail)
            identity.setWorkingParameter("vupass", upass)
            identity.setWorkingParameter("vurepass", urepass)

            userByMail = None
            userByMail = userService.getUserByAttribute("mail", umail)

            if userByMail is not None:
                facesMessages.add(FacesMessage.SEVERITY_ERROR, "User with same email exists.")
                return False

            attributes = self.getAttributes()

            pass_regex = attributes["pass_regex"]
            print "pass_regex = %s" % pass_regex

            pat = re.compile(pass_regex)
            mat = re.search(pat, upassd)
            if mat:
                print("Password is valid.")
            else:
                print("Password invalid !!")
                facesMessages.add(FacesMessage.SEVERITY_ERROR, "Password Policy is incorrect.")
                return False

            mail_regex = attributes["mail_regex"]
            print "mail_regex = %s" % mail_regex

            patmail = re.compile(mail_regex)
            matmail = re.search(patmail, umail)
            if matmail:
                print "Email is valid."
            else:
                print "Email domain is  invalid !!"
                facesMessages.add(FacesMessage.SEVERITY_ERROR, "Email domain is invalid.")
                return False

            #### Email Confirmation Required ####
            requireEmailConfirmation = StringHelper.toBoolean(configurationAttributes.get("Require_Email_Confirmation").getValue2(),False)

            if requireEmailConfirmation:

                fmt_dict = {
                    "%%fn%%": ufnm,
                    "%%ln%%": ulnm,
                    "%%mn%%": umnm,
                    "%%email%%": umail,
                    "%%otp%%": str(code)
                }

                email_subject, email_msg_template = self.getEmailParameters()

                print "email_subject = %s" % email_subject
                print "email_msg_template = %s" % email_msg_template

                newpassword = upass

                try:
                    mailService = CdiUtil.bean(MailService)
                    body = ""
                    if isinstance(email_msg_template, (list, tuple)):
                        for template_line in email_msg_template:
                            body += self.formatLine(template_line, fmt_dict)
                    if isinstance(email_msg_template, str):
                        body += self.formatLine(template_line, fmt_dict)
                    print "body = %s" % body

                    #mailService.sendMail(umail, None, email_subject, body, body)

                    #### Email Signing Code Begin ####

                    sender = EmailSender()
                    sender.sendEmail(self.alias, self.jks_keystore, self.keystore_password, self.sign_alg, umail, email_subject, body)

                    #### Email Signing Code End ####

                    print "OTP Sent"
                    otptime1 = datetime.now()

                    tess = str(otptime1)

                    listee = tess.split(':')

                    identity.setWorkingParameter("sentmin", listee[1])
                    return True
                except Exception, ex:
                    facesMessages.add(FacesMessage.SEVERITY_ERROR,
                                      "Failed to send email")
                    print "Register. Error sending message to SMTP"
                    print "Register. Unexpected error:", ex

            else:
                createddate = (datetime.now()+timedelta(days=90))
                currdate = datetime.now()
                #user.setAttribute("oxPasswordExpirationDate", str(createddate.strftime("%Y%m%d%H%M%S.%f+0000")))

                userCertificate = session_attributes.get("userCertificate")
                certDN = session_attributes.get("certDN")
                x509_json = {"value": userCertificate,"display":certDN ,"type":"","primary":"" }
                externalUID = session_attributes.get("externaluid")

                if certDN is not None:
                    certCNs = self.getCNFromDN(certDN)
                    if certCNs is not None:
                        i = 0
                        while i < len(certCNs):
                            if len(certCNs[i]) > 0:
                                if i == 0:
                                    ulnm = certCNs[i]
                                elif i == 1:
                                    ufnm = certCNs[i]
                                elif i == 2:
                                    umnm = certCNs[i]
                            i += 1

                print "ufnm = %s" % ufnm
                print "ulnm = %s" % ulnm
                print "umnm = %s" % umnm

                newUser = ZTrustPerson()

                newUser.setAttribute("givenName", ufnm)
                newUser.setAttribute("sn", ulnm)
                newUser.setAttribute("middleName", umnm)
                newUser.setAttribute("mail", umail)
                newUser.setAttribute("uid", umail)
                newUser.setAttribute("userPassword", upass)
                newUser.setAttribute("updatedAt", str(currdate.strftime("%Y%m%d%H%M%S.%f+0000")))
                newUser.setAttribute("oxPasswordExpirationDate", str(createddate.strftime("%Y%m%d%H%M%S.%f+0000")))
                newUser.setAttribute("userCertificate", userCertificate)
                newUser.setAttribute("oxTrustx509Certificate", json.dumps(x509_json))
                newUser.setAttribute("oxExternalUid", externalUID)

                #### Enable user on Registration ####
                enableUser = StringHelper.toBoolean(configurationAttributes.get("Enable_User").getValue2(), False)

                if not enableUser:
                    newUser.setAttribute("userStatus", "pending")
                    newUser.setAttribute("gluuStatus", "inactive")
                else:
                    newUser.setAttribute("userStatus", "active")
                    newUser.setAttribute("gluuStatus", "active") 

                userService.addUser(newUser, enableUser)

                logged_in = False

                if enableUser:
                    logged_in = authenticationService.authenticate(umail, upass)
                else:
                    newUser.setAttribute("gluuStatus", "inactive")
                    userService.updateUser(newUser)

                if not logged_in:
                    status_msg = "User %s %s with status: %s has been created" % (newUser.getAttribute("givenName"),
                            newUser.getAttribute("sn"), newUser.getAttribute("gluuStatus"))
                    status_msg += ". Login isn't success"
                    facesMessages.add(FacesMessage.SEVERITY_INFO, status_msg)
                    facesService.redirect("/auth/reg_status.xhtml")

                    return False

                return True

            return False

        elif step == 3:

            # Retrieve the session attribute
            print "Register. Step 3 SMS/OTP Authentication"
            code = session_attributes.get("code")
            rufnm = session_attributes.get("vufnm")
            rulnm = session_attributes.get("vulnm")
            rumnm = session_attributes.get("vumnm")
            rumail = session_attributes.get("vumail")
            rupass = session_attributes.get("vupass")
            rurepass = session_attributes.get("vurepass")
            externalUID = session_attributes.get("externaluid")
            cert = session_attributes.get("cert")
            userCertificate = session_attributes.get("userCertificate")
            min11 = int(identity.getWorkingParameter("sentmin"))
            certDN = session_attributes.get("certDN")
            print "Cert DN"
            print certDN
            x509_json = {"value": userCertificate,"display":certDN ,"type":"","primary":"" }

            #### Email Confirmation Required ####
            requireEmailConfirmation = StringHelper.toBoolean(configurationAttributes.get("Require_Email_Confirmation").getValue2(),False)

            if requireEmailConfirmation:

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

                print "----------------------------------"
                #print "Register. Code: %s" % str(code)
                print "----------------------------------"

                if code is None:
                    print "Register. Failed to find previously sent code"
                    return False

                if form_passcode is None:
                    print "Register. Passcode is empty"
                    return False

                #if len(form_passcode) != 6:
                    #print "Register. Passcode from response is not 6 digits: %s" % form_passcode
                    #return False



                if form_passcode == code:
                    print "Register, SUCCESS! User entered the same code!"

                    createddate = (datetime.now()+timedelta(days=90))
                    currdate = datetime.now()

                    #user.setAttribute("oxPasswordExpirationDate", str(createddate.strftime("%Y%m%d%H%M%S.%f+0000")))

                    if certDN is not None:
                        certCNs = self.getCNFromDN(certDN)
                        i = 0
                        while i < len(certCNs):
                            if len(certCNs[i]) > 0:
                                if i == 0:
                                    rulnm = certCNs[i]
                                elif i == 1:
                                    rufnm = certCNs[i]
                                elif i == 2:
                                    rumnm = certCNs[i]
                            i += 1

                    print "rufnm = %s" % rufnm
                    print "rulnm = %s" % rulnm
                    print "rumnm = %s" % rumnm

                    newUser = ZTrustPerson()

                    newUser.setAttribute("givenName", rufnm)
                    newUser.setAttribute("sn", rulnm)
                    newUser.setAttribute("middleName", rumnm)
                    newUser.setAttribute("mail", rumail)
                    newUser.setAttribute("uid", rumail)
                    newUser.setAttribute("userPassword", rupass)
                    newUser.setAttribute("updatedAt", str(currdate.strftime("%Y%m%d%H%M%S.%f+0000")))
                    newUser.setAttribute("oxPasswordExpirationDate", str(createddate.strftime("%Y%m%d%H%M%S.%f+0000")))
                    newUser.setAttribute("userCertificate", userCertificate)
                    newUser.setAttribute("oxTrustx509Certificate", json.dumps(x509_json))
                    newUser.setAttribute("oxExternalUid", externalUID)
                    #newUser.setAttribute("oxPreferredMethod", "1")

                    #### Enable user on Registration ####
                    enableUser = StringHelper.toBoolean(configurationAttributes.get("Enable_User").getValue2(), False)

                    if not enableUser:
                        newUser.setAttribute("userStatus", "pending")
                        newUser.setAttribute("gluuStatus", "inactive")
                    else:
                        newUser.setAttribute("userStatus", "active")
                        newUser.setAttribute("gluuStatus", "active")

                    userService.addUser(newUser, enableUser)

                    if not enableUser:
                        newUser.setAttribute("gluuStatus", "inactive")
                        userService.updateUser(newUser)

                    logged_in = False

                    if enableUser:
                        logged_in = authenticationService.authenticate(rumail, rupass)
                    else:
                        newUser.setAttribute("gluuStatus", "inactive")
                        userService.updateUser(newUser)

                    if not logged_in:
                        status_msg = "User %s %s with status: %s has been created" % (newUser.getAttribute("givenName"),
                                newUser.getAttribute("sn"), newUser.getAttribute("gluuStatus"))
                        status_msg += ". Login isn't success"
                        facesMessages.add(FacesMessage.SEVERITY_INFO, status_msg)
                        facesService.redirect("/auth/reg_status.xhtml")

                        return False

                    return True
            else:
                    createddate = (datetime.now()+timedelta(days=90))
                    currdate = datetime.now()

                    newUser = ZTrustPerson()
                    
                    newUser.setAttribute("givenName", rufnm)
                    newUser.setAttribute("sn", rulnm)
                    newUser.setAttribute("middleName", rumnm)
                    newUser.setAttribute("mail", rumail)
                    newUser.setAttribute("uid", rumail)
                    newUser.setAttribute("userPassword", rupass)
                    newUser.setAttribute("updatedAt", str(currdate.strftime("%Y%m%d%H%M%S.%f+0000")))
                    newUser.setAttribute("oxPasswordExpirationDate", str(createddate.strftime("%Y%m%d%H%M%S.%f+0000")))
                    newUser.setAttribute("userCertificate", userCertificate)
                    newUser.setAttribute("oxTrustx509Certificate", json.dumps(x509_json))
                    newUser.setAttribute("oxExternalUid", externalUID)

                    #### Enable user on Registration ####
                    enableUser = StringHelper.toBoolean(configurationAttributes.get("Enable_User").getValue2(), False)

                    if not enableUser:
                        newUser.setAttribute("userStatus", "pending")
                        newUser.setAttribute("gluuStatus", "inactive")
                    else:
                        newUser.setAttribute("userStatus", "active")
                        newUser.setAttribute("gluuStatus", "active")

                    userService.addUser(newUser, enableUser)

                    if not enableUser:
                        newUser.setAttribute("gluuStatus", "inactive")
                        userService.updateUser(newUser)

                    logged_in = False
                    logged_in = authenticationService.authenticate(rumail, rupass)

                    if (not logged_in):
                        return False

                    return True

                # return True

            print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
            print "Register. FAIL! User entered the wrong code! %s != %s" % (form_passcode, code)
            print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
            #facesMessages.add(facesMessage.SEVERITY_ERROR, "Incorrect Twilio code, please try again.")
            return False

    def prepareForStep(self, configurationAttributes, requestParameters, step):
        identity = CdiUtil.bean(Identity)
        session_attributes = self.identity.getSessionId().getSessionAttributes()
        userService = CdiUtil.bean(UserService)
        facesMessages = CdiUtil.bean(FacesMessages)
        facesMessages.setKeepMessages()
        if step == 1:
            print "Register. Prepare for Step 1"
            attributes = self.getAttributes()
                
            attributes["mail_regex"] = attributes["mail_regex"].replace("\\","\\\\")
            attributes["pass_regex"] = attributes["pass_regex"].replace("\\","\\\\")

            # this transform depends on, which symbol is used in the text of 
            # reg.xhtml and regtr.xhtml
            # if
            #   email_regex = `#{identity.getWorkingParameter('mail_regex')}`;
            #   pass_regex = `#{identity.getWorkingParameter('pass_regex')}`;
            # in this case replace("\\\\`","\\`") should be used;
            # if
            #   email_regex = "#{identity.getWorkingParameter('mail_regex')}";
            #   pass_regex = "#{identity.getWorkingParameter('pass_regex')}";
            # in this case replace('\\\\"','\\"') should be used.
            attributes["mail_regex"] = attributes["mail_regex"].replace("\\\\`","\\`")
            attributes["pass_regex"] = attributes["pass_regex"].replace("\\\\`","\\`")

            print "attributes['ids'] = %s" % attributes["ids"]
            print "attributes['pass_strength'] = %s" % attributes["pass_strength"]
            print "attributes['pass_regex'] = %s" % attributes["pass_regex"]
            print "attributes['mail_regex'] = %s" % attributes["mail_regex"]

            identity.setWorkingParameter("ids", attributes["ids"])
            identity.setWorkingParameter("passStrength", str(attributes["pass_strength"]))
            identity.setWorkingParameter("pass_regex", attributes["pass_regex"])
            identity.setWorkingParameter("mail_regex", attributes["mail_regex"])

            print "Register. Prepare for Step 1. True"
            
            return True
        elif step == 2:
            print "Register. Prepare for Step 2"
            # Store certificate in session
            facesContext = CdiUtil.bean(FacesContext)
            externalContext = facesContext.getExternalContext()
            request = externalContext.getRequest()

            clientSDN = externalContext.getRequestHeaderMap().get("X-ClientSDN")
            print "Register. Prepare for step 2. clientSDN = %s" % clientSDN

            # Try to get certificate from header X-ClientCert
            clientCertificate = externalContext.getRequestHeaderMap().get("X-ClientCert")

            x509Certificatee = None
            certString1 = None

            if clientCertificate != None:
                x509Certificatee = self.certFromPemString(clientCertificate)

            if x509Certificatee != None:
                certString1 =  self.certToString(x509Certificatee)

            if certString1 != None:
                identity.setWorkingParameter("userCertificate", certString1)

            if certString1 == None:
                print "not selected"
                #return False;

            if clientCertificate != None:
                x509Certificate = self.certFromPemString(clientCertificate)
                identity.setWorkingParameter("cert_x509",  self.certToString(x509Certificate))
                print "Register. Prepare for step 2. Storing user certificate obtained from 'X-ClientCert' header"

                certString =  self.certToString(x509Certificate)
                print "certString:%s" % certString
                if certString != None:
                    print "Register. Prepare for step 2. Storing user certificate obtained from 'X-ClientCert' header"

                    x509Certificate = self.certFromString(certString)

                    subjectX500Principal = x509Certificate.getSubjectX500Principal()
                    identity.setWorkingParameter("certDN",  str(subjectX500Principal))
                    print "Register. Authenticate for step 2. User selected certificate with DN '%s'" % subjectX500Principal
                    valid = self.validateCertificate(x509Certificate)
                    if not valid:
                        print "Register. Authenticate for step 2. Certificate DN '%s' is not valid" % subjectX500Principal
                        facesMessages.add(FacesMessage.SEVERITY_ERROR, "Certificate is not valid.")
                        # Return True to inform user how to reset workflow
                        return False
                    x509CertificateFingerprint = self.calculateCertificateFingerprint(x509Certificate)
                    cert_user_external_uid = "cert:%s" % x509CertificateFingerprint

                    userByUid = userService.getUserByAttribute("oxExternalUid", cert_user_external_uid)
                    if userByUid != None:
                        facesMessages.add(FacesMessage.SEVERITY_ERROR, "The certificate is already enrolled for another user.")
                        facesMessages.add(FacesMessage.SEVERITY_ERROR, "Please contact System Administrator.")
                        return False
                    print cert_user_external_uid
                    # print "Register. Step 1 Password Authentication"
                    identity.setWorkingParameter("externaluid", str(cert_user_external_uid))

                    return True

            # Try to get certificate from attribute javax.servlet.request.X509Certificate
            x509Certificates = request.getAttribute('javax.servlet.request.X509Certificate')
            if (x509Certificates != None) and (len(x509Certificates) > 0):
                identity.setWorkingParameter("cert_x509", self.certToString(x509Certificates[0]))
                print "Register. Prepare for step 2. Storing user certificate obtained from 'javax.servlet.request.X509Certificate' attribute"
                return True

        elif step == 3:
            print "Prapare for step 3"
            return True
        return False

    def getExtraParametersForStep(self, configurationAttributes, step):
        if step == 1:
            return Arrays.asList("ids","passStrength","mail_regex","pass_regex")
        elif step == 2:
            return Arrays.asList("code","vufnm","vulnm","vumnm","vumail","vupass","vurepass","externaluid","cert","cert_x509","userCertificate","certDN")
        elif step == 3:
            return Arrays.asList("code","vufnm","vulnm","vumnm","vumail","vupass","vurepass","externaluid","cert","cert_x509","sentmin","userCertificate","certDN")

        return None

    def getCountAuthenticationSteps(self, configurationAttributes):
        identity = CdiUtil.bean(Identity)
        requireEmailConfirmation = StringHelper.toBoolean(configurationAttributes.get("Require_Email_Confirmation").getValue2(),False)

        if requireEmailConfirmation and identity.isSetWorkingParameter("code"):
            return 3
        else:
            return 2

    def getPageForStep(self, configurationAttributes, step):
        identity = CdiUtil.bean(Identity)
        #### Email Confirmation Requried ####
        requireEmailConfirmation = StringHelper.toBoolean(configurationAttributes.get("Require_Email_Confirmation").getValue2(),False)
        if step == 1:
            return "/auth/reg.xhtml"
        elif step == 2:
            return "/auth/regtr.xhtml"
        elif step == 3:
            if requireEmailConfirmation:
                return "/auth/register/entertoken.xhtml"
            else:
                return ""
        return ""

    def logout(self, configurationAttributes, requestParameters):
        return True

    def getAttributes(self):
        f = open(self.attributes_json_file_path)
        data = json.load(f)
        data = ast.literal_eval(json.dumps(data))

        ids = data["ids"]
        ids_str = ",".join(ids)
        strength = data["passStrength"]

        f = open(self.regex_json_file_path)
        data = json.load(f)
        data = ast.literal_eval(json.dumps(data))        
        
        pass_regex = data["pass_regex"]
        mail_regex = data["mail_regex"]

        attribs = {"ids":ids_str,"pass_strength":strength,"pass_regex":pass_regex,"mail_regex":mail_regex}
        return attribs

    def getSessionAttribute(self, attribute_name):
        identity = CdiUtil.bean(Identity)

        # Try to get attribute value from Seam event context
        if identity.isSetWorkingParameter(attribute_name):
            return identity.getWorkingParameter(attribute_name)

        # Try to get attribute from persistent session
        session_id = identity.getSessionId()
        if session_id == None:
            return None

        session_attributes = session_id.getSessionAttributes()
        if session_attributes == None:
            return None

        if session_attributes.containsKey(attribute_name):
            return session_attributes.get(attribute_name)

        return None

    def calculateCertificateFingerprint(self, x509Certificate):
        print "Register. Calculate fingerprint for certificate DN '%s'" % x509Certificate.getSubjectX500Principal()

        publicKey = x509Certificate.getPublicKey()

        # Use oxAuth implementation
        fingerprint = FingerprintHelper.getPublicKeySshFingerprint(publicKey)

        return fingerprint

    def validateCertificate(self, x509Certificate):
        subjectX500Principal = x509Certificate.getSubjectX500Principal()

        print "Register. Validating certificate with DN '%s'" % subjectX500Principal

        validation_date = java.util.Date()

        for type in self.validator_types:
            if self.validators[type][1]:
                result = self.validators[type][0].validate(
                    x509Certificate, self.chain_certs, validation_date)
                print "Register. Validate certificate: '%s'. Validation method '%s' result: '%s'" % (subjectX500Principal, type, result)

                if (result.getValidity() != ValidationStatus.CertificateValidity.VALID):
                    print "Register. Certificate: '%s' is invalid" % subjectX500Principal
                    return False

        return True

    def certToString(self, x509Certificate):
        if x509Certificate == None:
            return None
        return base64.b64encode(x509Certificate.getEncoded())

    def certFromString(self, x509CertificateEncoded):
        x509CertificateDecoded = base64.b64decode(x509CertificateEncoded)
        return CertUtils.x509CertificateFromBytes(x509CertificateDecoded)

    def certFromPemString(self, pemCertificate):
        x509CertificateEncoded = pemCertificate.replace("-----BEGIN CERTIFICATE-----", "").replace("-----END CERTIFICATE-----", "").strip()
        return self.certFromString(x509CertificateEncoded)

    def getCNFromDN(self, dn_value):
        regex_str = "^(?:.*)CN\\s*=\\s*([A-Za-z0-9\\_\\-]+)\\.([A-Za-z0-9\\_\\-]+)\\.([A-Za-z0-9\\_\\-]+)\\.(\\d{10})\\s*,*(?:.*)"
        cert_names = [ '' ] * 4
        ref_expr_obj = re.search(regex_str, dn_value)
        if ref_expr_obj is not None:
            ref_expr_groups = ref_expr_obj.groups()
            if ref_expr_groups is not None:
                i = 0
                for ref_expr_group in ref_expr_groups:
                    cert_names [i] = ref_expr_group
                    i += 1
        return cert_names

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
        get SMTP config from Gluu Server
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
                'user' : smtpconfig.getUserName(),
                'from' : smtpconfig.getFromEmailAddress(),
                'pwd_decrypted' : encryptionService.decrypt(smtpconfig.getPassword()),
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

        properties.put("mail.from", "Gluu Casa")

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
