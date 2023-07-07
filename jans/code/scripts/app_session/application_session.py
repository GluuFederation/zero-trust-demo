
# Example custom application_session script to enforce one login
# and to write an extra audit log to the LDAP server

from io.jans.model.custom.script.type.session import ApplicationSessionType

from io.jans.service.cdi.util import CdiUtil
from io.jans.orm import PersistenceEntryManager
from io.jans.as.model.config import StaticConfiguration

from jakarta.faces.application import FacesMessage
from io.jans.jsf2.message import FacesMessages

from java.util import Date
from java.util import Calendar

#### Audit Entries Additional Imports ####
from io.jans.as.server.security import Identity
from io.jans.as.server.service import MetricService

from io.jans.orm.model.base import SimpleBranch
from io.jans.model.metric import MetricType

from io.jans.model import ApplicationType

from io.jans.as.server.service.external.session import SessionEventType

from io.jans.as.common.model.session import SessionId
from io.jans.as.common.model.session import SessionIdState

from io.jans.model.metric.sql import ZTrustMetricEntry

import java

import uuid
import time
import json
import ast

class ApplicationSession(ApplicationSessionType):

    session_attributes_keys = [
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

    def __init__(self, currentTimeMillis):
        self.currentTimeMillis = currentTimeMillis

    def init(self, configurationAttributes):
        print "ApplicationSession.init: begin"
        
        self.metric_audit_ou_name = None
        self.metric_audit_conf_json_file_path = None
        
        self.event_types = None
        self.audit_data = None
        
        self.init_ok = False
        
        self.entryManager = CdiUtil.bean(PersistenceEntryManager)
        self.staticConfiguration = CdiUtil.bean(StaticConfiguration)
        self.metricService = CdiUtil.bean(MetricService)
        self.identity = CdiUtil.bean(Identity)

        try:
            self.metric_audit_ou_name = configurationAttributes.get("metric_audit_ou_name").getValue2()
            self.metric_audit_conf_json_file_path = configurationAttributes.get("metric_audit_conf_json_file_path").getValue2()
            self.event_types, self.audit_data = self.getMetricAuditParameters(self.metric_audit_conf_json_file_path)
            if self.event_types and self.audit_data:
                self.init_ok = True
        except Exception as ex:
            print("ApplicationSession.init: error of initializing: ex = {}".format(ex))

        print("ApplicationSession.init: self.event_types = {}".format(self.event_types))
        print("ApplicationSession.init: self.audit_data = {}".format(self.audit_data))

        print("ApplicationSession.init: self.init_ok = {}".format(self.init_ok))
        return True

    def destroy(self, configurationAttributes):
        print("ApplicationSession.destroy")
        return True

    def getApiVersion(self):
        return 2

    # Called each time specific session event occurs
    # event is org.gluu.oxauth.service.external.session.SessionEvent
    def onEvent(self, event):

        print("ApplicationSession.onEvent: event = {}".format(event))
        print("ApplicationSession.onEvent: event.getType() = {}".format(event.getType()))
        print("ApplicationSession.onEvent: event.getSessionId() = {}".format(event.getSessionId()))

        if not self.init_ok:
            print("ApplicationSession.onEvent: isn't initialized")
            return
            
        if not(str(event.getType()).upper() in (event_type.upper() for event_type in self.event_types)):
            print("ApplicationSession.onEvent: event {} will not be processed".format(event.getType()))
            return;

        remote_ip = event.getSessionId().getSessionAttributes()["remote_ip"]
        print("ApplicationSession.onEvent: remote_ip = {}".format(remote_ip))
            
        session = None
        sessionAttrs = None
        session_id = None
        userDN = None 
        user = None
        uid = None
        ip = None
        
        session = event.getSessionId()
        if session:
            sessionAttrs = session.getSessionAttributes()
            session_id = session.getId()
            userDN = session.getUserDn()
            user = session.getUser()
        
        if user:
            uid = user.getUserId()

        if sessionAttrs:
            client_id = sessionAttrs.get("client_id")
            redirect_uri = sessionAttrs.get("redirect_uri")
            acr = sessionAttrs.get("acr_values")
        
        httpRequest = event.getHttpRequest()
        
        if httpRequest:
            ip = httpRequest.getRemoteAddr()

        print('ApplicationSession.onEvent: {"sessionId": "%s", "uid": "%s", "client_id": "%s", "redirect_uri": "%s", "acr": "%s", "ip": "%s", "type": "%s"}' %
            (session_id, uid, client_id, redirect_uri, acr, ip, str(event.getType())))

        # Don't allow more then one session!
        entity = SessionId()
        entity.setDn(self.staticConfiguration.getBaseDn().getSessions())
        entity.setUserDn(userDN)
        entity.setState(SessionIdState.UNAUTHENTICATED)
        results = self.entryManager.findEntries(entity)
        if results == 1:
            facesMessages = CdiUtil.bean(FacesMessages)
            facesMessages.add(FacesMessage.SEVERITY_ERROR, "Please, end active session first!")
            print("ApplicationSession.onEvent: User %s denied session--must end active session first" % uid)
            return

        # Audit Log enhancements to store additional data in LDAP.
        #
        # The goal is to create a record here that can be exported and
        # reported on at a later time.
        now = time.localtime(time.time())
        yearMonth = time.strftime("%Y%m", now)
        
        if self.entryManager.hasBranchesSupport(""):
            print("ApplicationSession.onEvent: self.entryManager.hasBranchesSupport("") = %s" % str(self.entryManager.hasBranchesSupport("")))
            # Create a base organization unit, for example
            # ou=audit,o=metric
            metricDN = self.staticConfiguration.getBaseDn().getMetric().split(",")[1]
            print("ApplicationSession.onEvent: metricDN = %s" % metricDN)
            auditDN = "ou=%s,ou=statistic,%s" % (self.metric_audit_ou_name, metricDN)
            print("ApplicationSession.onEvent: auditDN = %s" % auditDN)

            # If audit organizational unit does not exist, create it
            ouExists = self.entryManager.contains(auditDN, SimpleBranch)
            print("ApplicationSession.onEvent: ouExists = %s" % ouExists)
            if not ouExists:
                print("ApplicationSession.onEvent: Creating organizational unit: %s" % auditDN)
                branch = SimpleBranch()
                branch.setOrganizationalUnitName(self.metric_audit_ou_name)
                branch.setDn(auditDN)
                print("ApplicationSession.onEvent: branch = %s" % branch)
                self.entryManager.persist(branch)

            # If there is no audit organizational unit for this month, create it
            yearMonthDN = "ou=%s,%s" % (yearMonth, auditDN)
            print("ApplicationSession.onEvent: yearMonthDN = %s" % yearMonthDN)
            ouExists = self.entryManager.contains(yearMonthDN, SimpleBranch)
            print("ApplicationSession.onEvent: ouExists = %s" % ouExists)
            if not ouExists:
                print("ApplicationSession.onEvent: Creating organizational unit: %s" % yearMonthDN)
                branch = SimpleBranch()
                branch.setOrganizationalUnitName(yearMonth)
                branch.setDn(yearMonthDN)
                print("ApplicationSession.onEvent: branch = %s" % branch)
                self.entryManager.persist(branch)

        # Write the log
        # TODO Need to figure out edipi
        uniqueIdentifier = str(uuid.uuid4())
        print("ApplicationSession.onEvent: uniqueIdentifier = %s" % uniqueIdentifier)
        calendar_curr_date = Calendar.getInstance()
        curr_date = calendar_curr_date.getTime()

        dn = "uniqueIdentifier=%s,ou=%s,ou=%s,ou=statistic,o=metric" % (uniqueIdentifier, yearMonth, self.metric_audit_ou_name)

        metricEntity = ZTrustMetricEntry()

        metricEntity.setDn(dn)
        metricEntity.setId(uniqueIdentifier)
        metricEntity.setCreationDate(curr_date)
        metricEntity.setApplicationType(ApplicationType.OX_AUTH)
        metricEntity.setMetricType("audit")

        data = self.generateJansData(event, self.audit_data)

        metricEntity.setJansData(data)

        print("ApplicationSession.onEvent: metricEntity = %s" % metricEntity)
        self.entryManager.persist(metricEntity)
        print("ApplicationSession.onEvent: Wrote metric entry %s" % dn)
        print("ApplicationSession.onEvent: end")            

        return

    # This method is called for both authenticated and unauthenticated sessions
    #   httpRequest is javax.servlet.http.HttpServletRequest
    #   sessionId is org.gluu.oxauth.model.common.SessionId
    #   configurationAttributes is java.util.Map<String, SimpleCustomProperty>
    def startSession(self, httpRequest, sessionId, configurationAttributes):
        print("ApplicationSession.startSession")
        if not self.init_ok:
            print("ApplicationSession.startSession: isn't initialized")
            return

        ip = None
        if httpRequest:
            ip = httpRequest.getRemoteAddr()
            
        remote_ip = sessionId.getSessionAttributes()["remote_ip"]
        print("ApplicationSession.startSession: remote_ip = {}".format(remote_ip))

        print("ApplicationSession.startSession: httpRequest = {}".format(httpRequest))            
        print("ApplicationSession.startSession: sessionId = {}".format(sessionId))
        print("ApplicationSession.startSession: ip = {}".format(ip))
        print("ApplicationSession.startSession: configurationAttributes = {}".format(configurationAttributes))
        
        print("ApplicationSession.startSession for sessionId: {}".format(sessionId.getId()))
        
        return True

    # Application calls it at end session request to allow notify 3rd part systems
    #   httpRequest is javax.servlet.http.HttpServletRequest
    #   sessionId is org.gluu.oxauth.model.common.SessionId
    #   configurationAttributes is java.util.Map<String, SimpleCustomProperty>
    def endSession(self, httpRequest, sessionId, configurationAttributes):
        print("ApplicationSession.endSession")
        if not self.init_ok:
            print("ApplicationSession.endSession: isn't initialized")
            return

        ip = None
        if httpRequest:
            ip = httpRequest.getRemoteAddr()

        remote_ip = sessionId.getSessionAttributes()["remote_ip"]
        print("ApplicationSession.endSession: remote_ip = {}".format(remote_ip))

        print("ApplicationSession.endSession: httpRequest = {}".format(httpRequest))
        print("ApplicationSession.endSession: sessionId = {}".format(sessionId))
        print("ApplicationSession.endSession: ip = {}".format(ip))
        print("ApplicationSession.endSession: configurationAttributes = {}".format(configurationAttributes))
        
        print("ApplicationSession.endSession for sessionId: {}".format(sessionId.getId()))        
            
        return True

    def getMetricAuditParameters(self, metric_audit_conf_json_file_path):
        file_data = None
        event_types = None
        audit_data = None
        try:
            file = open(metric_audit_conf_json_file_path)
            file_data = json.load(file)
            file_data = ast.literal_eval(json.dumps(file_data))
            event_types = file_data["event_types"]
            audit_data = file_data["audit_data"]
        except Exception as ex:
            print("ApplicationSession.getMetricAuditParameters: Errror Reading of config file: ex = {}".format(ex))
        print("ApplicationSession.getMetricAuditParameters() event_types = {}".format(event_types))
        print("ApplicationSession.getMetricAuditParameters() audit_data = {}".format(audit_data))
        return event_types, audit_data

    def generateJansData(self, event, audit_data):
        session = event.getSessionId()
        first_added = False
        
        jans_data = '{ '
        
        if "type".upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            if first_added:
                jans_data += ','
            else:
                first_added = True
            jans_data += '"type": "%s"' % event.getType()

        if "dn".upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            if first_added:
                jans_data += ','
            else:
                first_added = True
            jans_data += '"dn": "%s"' % session.getUserDn() if session else "None"

        if "id".upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            if first_added:
                jans_data += ','
            else:
                first_added = True
            jans_data += '"id": "%s"' % session.getId() if session else "None"

        if "outsideSid".upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            if first_added:
                jans_data += ','
            else:
                first_added = True
            jans_data += '"outsideSid": "%s"' % session.getOutsideSid() if session else "None"

        if "lastUsedAt".upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            if first_added:
                jans_data += ','
            else:
                first_added = True
            jans_data += '"lastUsedAt": "%s"' % session.getLastUsedAt() if session else "None"

        if "authenticationTime".upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            if first_added:
                jans_data += ','
            else:
                first_added = True
            jans_data += '"authenticationTime": "%s"' % session.getAuthenticationTime() if session else "None"

        if "state".upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            if first_added:
                jans_data += ','
            else:
                first_added = True
            jans_data += '"state": "%s"' % session.getState() if session else "None"

        if "expirationDate".upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            if first_added:
                jans_data += ','
            else:
                first_added = True
            jans_data += '"expirationDate": "%s"' % session.getExpirationDate() if session else "None"

        if "sessionState".upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            if first_added:
                jans_data += ','
            else:
                first_added = True
            jans_data += '"sessionState": "%s"' % session.getSessionState() if session else "None"

        if "permissionGranted".upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            if first_added:
                jans_data += ','
            else:
                first_added = True
            jans_data += '"permissionGranted": "%s"' % session.getPermissionGranted() if session else "None"

        if "permissionGrantedMap".upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            if first_added:
                jans_data += ','
            else:
                first_added = True
            jans_data += '"permissionGrantedMap": "%s"' % session.getPermissionGrantedMap() if session else "None"

        if "deviceSecrets".upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            if first_added:
                jans_data += ','
            else:
                first_added = True
            jans_data += '"deviceSecrets": "%s"' % session.getDeviceSecrets() if session else "None"

        session_attributes = {}

        if session:
            session_attributes = session.getSessionAttributes()

        try:
            for session_attributes_key in self.session_attributes_keys:
                if ("sessionAttributes".upper() in (audit_data_el.upper() for audit_data_el in audit_data) or
                        not ("sessionAttributes".upper() in (audit_data_el.upper() for audit_data_el in audit_data)) and
                        session_attributes_key.upper() in (audit_data_el.upper() for audit_data_el in audit_data)):
                    if first_added:
                        jans_data += ','
                    else:
                        first_added = True
                    jans_data += '"%s": "%s"' % (session_attributes_key, session_attributes[session_attributes_key] if session else "None")
        except Exception as ex:
            print("ApplicationSession.generateJansData: Error: ex = {}".format(ex))

        jans_data += ' }'

        return jans_data
