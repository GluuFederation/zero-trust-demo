# Example custom application_session script to enforce one login
# and to write an extra audit log to the LDAP server

from org.gluu.model.custom.script.type.session import ApplicationSessionType
from org.gluu.service.cdi.util import CdiUtil
from org.gluu.persist import PersistenceEntryManager
from org.gluu.oxauth.model.config import StaticConfiguration
from org.gluu.oxauth.model.ldap import TokenLdap
from javax.faces.application import FacesMessage
from org.gluu.jsf2.message import FacesMessages
from org.gluu.oxauth.model.config import Constants
from java.util import Date

#### Audit Entries Additional Imports ####
from org.gluu.oxauth.security import Identity
from org.gluu.oxauth.service import MetricService
from org.gluu.search.filter import Filter
from org.gluu.persist.model.base import SimpleBranch
from org.gluu.model.metric import MetricType
from org.gluu.model import ApplicationType
from org.gluu.persist.model.base import CustomEntry
from org.gluu.persist.model.base import CustomAttribute

import uuid, time, java

class ApplicationSession(ApplicationSessionType):
    def __init__(self, currentTimeMillis):
        self.currentTimeMillis = currentTimeMillis

    def init(self, configurationAttributes):
        print "ApplicationSession.init: begin"
        self.entryManager = CdiUtil.bean(PersistenceEntryManager)
        self.staticConfiguration = CdiUtil.bean(StaticConfiguration)
        self.metricService= CdiUtil.bean(MetricService)
        self.identity = CdiUtil.bean(Identity)

        try:
            self.metric_audit_ou_name = configurationAttributes.get("metric_audit_ou_name").getValue2()
        except:
            print "ApplicationSession.init: metric_audit_ou_name not found"


        print "ApplicationSession.init: success"
        return True

    def destroy(self, configurationAttributes):
        print "ApplicationSession.destroy"
        return True

    def getApiVersion(self):
        return 2

    # Called each time specific session event occurs
    # event is org.gluu.oxauth.service.external.session.SessionEvent
    def onEvent(self, event):
        print "ApplicationSession.onEvent: start"
        if not(event.getType() == SessionEventType.AUTHENTICATED):
            return
        session = event.getSessionId()
        sessionAttrs = session.getSessionAttributes()
        session_id = session.getId()
        user = session.getUser()
        userDN = session.getUserDn()
        uid = user.getUid()
        # edipi = user.getAttribute("edipi")
        client_id = sessionAttrs.get("client_id")
        redirect_uri = sessionAttrs.get("redirect_uri")
        acr = sessionAttrs.get("acr_values")
        ip = httpRequest.getRemoteAddr()
        print 'ApplicationSession.startSession: {"sessionId": "%s", "uid": "%s", "client_id": "%s", "redirect_uri": "%s", "acr": "%s", "ip": "%s"}' % (session_id, uid, client_id, redirect_uri, acr, ip)

        ########################################################################
        # Don't allow more then one session!
        ########################################################################
        entity = SessionId()
        entity.setDn(self.staticConfiguration.getBaseDn().getSessions())
        entity.setUserDn(userDn)
        entity.setState(SessionIdState.AUTHENTICATED)
        results = self.entryManager.findEntries(entity)
        if not(results == 1):
            facesMessages = CdiUtil.bean(FacesMessages)
            facesMessages.add(FacesMessage.SEVERITY_ERROR, "Please, end active session first!")
            print "User %s denied session--must end active session first" % uid
            return False

        ########################################################################
        # Audit Log enhancements to store additional data in LDAP.
        #
        # The goal is to create a record here that can be exported and
        # reported on at a later time.
        #
        # dn=uniqueIdentifier={guid},ou={year-month},ou=audit,o=metric
        # objectclass: top
        # objectclass: oxMetric
        # uniqueIdentifier: {guid}
        # oxMetricType: audit
        # creationDate: {timestamp}
        # oxApplicationType: client_id
        # oxData: {“uid”:”foobar”,
        #          “edipi”:”12321321”,
        #          “type”: “startSession”,
        #          "redirect_uri": "https://abc.com/cb"
        #          "ip": "10.10.10.10",
        #          "acr": "smartcard",
        #          "session_id": "1234"}
        ########################################################################

        # Create a base organization unit, for example
        # ou=audit,o=metric
        metricDN = self.staticConfiguration.getBaseDn().getMetric().split(",")[1]
        auditDN = "ou=%s,%s" (self.metric_audit_ou_name, metricDN)
        now = time.localtime(time.time())

        # If audit organizational unit does not exist, create it
        ouExists = self.entryManager.contains(auditDN, SimpleBranch)
        if not ouExists:
            print "Creating organizational unit: %s" % auditDN
            branch = SimpleBranch()
            branch.setOrganizationalUnitName(self.metric_audit_ou_name)
            branch.setDn(auditDN)
            self.entryManager.persist(branch)

        # If there is no audit organizational unit for this month, create it
        yearMonth = time.strftime("%Y%m", now)
        yearMonthDN = "ou=%s,%s" % (yearMonth, auditDN)
        ouExists = self.entryManager.contains(yearMonthDN, SimpleBranch)
        if not ouExists:
            print "Creating organizational unit: %s" % yearMonthDN
            branch.setOrganizationalUnitName(yearMonth)
            branch.setDn(yearMonthDN)
            self.entryManager.persist(branch)

        # Write the log
        # TODO Need to figure out edipi
        uniqueIdentifier = str(uuid.uuid4())
        createDate = time.strftime("%Y%m%d%H%M%S.%f+0000", now)
        metricEntity = CustomEntry()
        metricEntity.setCustomObjectClasses(["top","oxMetric"])
        dn = "uniqueIdentifier=%s,%s" % (str(uniqueIdentifier), ouDN)
        uniqueIdentifier = CustomAttribute("uniqueIdentifier", uniqueIdentifier)
        metricType = CustomAttribute("oxMetricType", "audit")
        creationDate = CustomAttribute("creationDate", createDate)
        applicationType = CustomAttribute("oxApplicationType", clientid)
        data = """{"sessionId": "%s",
"uid": "%s",
"client_id": "%s",
"redirect_uri": "%s",
"acr": "%s",
"ip": "%s",
"type": "startSession"}""" % (sessionId, uid, client_id, redirect_uri, acr, ip)
        oxData = CustomAttribute("oxData", data)
        customAttributes = [uniqueIdentifier,
                            metricType,
                            creationDate,
                            applicationType,
                            oxData]
        customEntry.setCustomAttributes(customAttributes)
        customEntry.setDn(dn)
        self.entryManager.persist(customEntry)
        print "startSession: Wrote metric entry %s" % dn
        return

    # This method is called for both authenticated and unauthenticated sessions
    #   httpRequest is javax.servlet.http.HttpServletRequest
    #   sessionId is org.gluu.oxauth.model.common.SessionId
    #   configurationAttributes is java.util.Map<String, SimpleCustomProperty>
    def startSession(self, httpRequest, sessionId, configurationAttributes):

        return True

    # Application calls it at end session request to allow notify 3rd part systems
    #   httpRequest is javax.servlet.http.HttpServletRequest
    #   sessionId is org.gluu.oxauth.model.common.SessionId
    #   configurationAttributes is java.util.Map<String, SimpleCustomProperty>
    def endSession(self, httpRequest, sessionId, configurationAttributes):
        if sessionId:
            print "ApplicationSession.endSession for sessionId: %" % sessionId.getId()
        else:
            print "ApplicationSession.endSession: sessionId object not found"
        return True
