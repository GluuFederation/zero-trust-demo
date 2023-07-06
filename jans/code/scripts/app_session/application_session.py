
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

import uuid, time, java

class ApplicationSession(ApplicationSessionType):
    def __init__(self, currentTimeMillis):
        self.currentTimeMillis = currentTimeMillis

    def init(self, configurationAttributes):
        print "ApplicationSession.init: begin"
        self.entryManager = CdiUtil.bean(PersistenceEntryManager)
        self.staticConfiguration = CdiUtil.bean(StaticConfiguration)
        self.metricService = CdiUtil.bean(MetricService)
        self.identity = CdiUtil.bean(Identity)

        try:
            self.metric_audit_ou_name = configurationAttributes.get("metric_audit_ou_name").getValue2()
        except:
            print("ApplicationSession.init: metric_audit_ou_name not found")

        print("ApplicationSession.init: success")
        return True

    def destroy(self, configurationAttributes):
        print("ApplicationSession.destroy")
        return True

    def getApiVersion(self):
        return 2

    # Called each time specific session event occurs
    # event is org.gluu.oxauth.service.external.session.SessionEvent
    def onEvent(self, event):
        print("ApplicationSession.onEvent: start")
        print("ApplicationSession.onEvent: event.getType() = {}".format(event.getType()))
#        if not(event.getType() == SessionEventType.AUTHENTICATED):
#            print("ApplicationSession.onEvent: end")
#            return

#        if event.getType() == SessionEventType.AUTHENTICATED:
#            self.onEventAuthenticated(event)
#            return

 #       if event.getType() == SessionEventType.GONE:
#            self.onEventGone(event)
#            return
            
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
            ip = event.getHttpRequest().getRemoteAddr()

        print('ApplicationSession.onEvent: {"sessionId": "%s", "uid": "%s", "client_id": "%s", "redirect_uri": "%s", "acr": "%s", "ip": "%s", "type": "%s"}' %
            (session_id, uid, client_id, redirect_uri, acr, ip, str(event.getType())))

        ########################################################################
        # Don't allow more then one session!
        ########################################################################
        entity = SessionId()
        entity.setDn(self.staticConfiguration.getBaseDn().getSessions())
        entity.setUserDn(userDN)
        entity.setState(SessionIdState.UNAUTHENTICATED)
        results = self.entryManager.findEntries(entity)
        if results == 1:
            facesMessages = CdiUtil.bean(FacesMessages)
            facesMessages.add(FacesMessage.SEVERITY_ERROR, "Please, end active session first!")
            print("User %s denied session--must end active session first" % uid)
            return

        ########################################################################
        # Audit Log enhancements to store additional data in LDAP.
        #
        # The goal is to create a record here that can be exported and
        # reported on at a later time.
        #
        # dn=uniqueIdentifier={guid},ou={year-month},ou=audit,o=metric
        # objectclass: top
        # objectclass: jansMetric
        # uniqueIdentifier: {guid}
        # jansMetricTyp: audit
        # creationDate: {timestamp}
        # jansAppTyp: client_id
        # jansData: {'uid':'foobar',
        #          'edipi':'12321321',
        #          'type': 'startSession',
        #          'redirect_uri': 'https://abc.com/cb'
        #          'acr': 'smartcard',
        #          'session_id': "1234"}
        ########################################################################
        
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
                print("Creating organizational unit: %s" % auditDN)
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
                print("Creating organizational unit: %s" % yearMonthDN)
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
        print("ApplicationSession.onEvent: type(curr_date) = %s" % type(curr_date))

        dn = "uniqueIdentifier=%s,ou=%s,ou=%s,ou=statistic,o=metric" % (uniqueIdentifier, yearMonth, self.metric_audit_ou_name)

        metricEntity = ZTrustMetricEntry()

        metricEntity.setDn(dn)
        metricEntity.setId(uniqueIdentifier)
        metricEntity.setCreationDate(curr_date)
        metricEntity.setApplicationType(ApplicationType.OX_AUTH)
        metricEntity.setMetricType("audit")
 
#        data = """{"sessionId": "%s", "uid": "%s", "client_id": "%s", "redirect_uri": "%s", "acr": "%s", "ip": "%s", "type": "startSession"}""" % (session_id, uid, client_id, redirect_uri, acr, ip)
        data = """{"sessionId": "%s", "uid": "%s", "client_id": "%s", "redirect_uri": "%s", "acr": "%s", "ip": "%s", "type": "%s"}""" % (session_id, uid, client_id, redirect_uri, acr, ip, str(event.getType()))

        metricEntity.setJansData(data)

        print("ApplicationSession.onEvent: metricEntity = %s" % metricEntity)
        self.entryManager.persist(metricEntity)

        print("ApplicationSession.startSession: Wrote metric entry %s" % dn)
        print("ApplicationSession.onEvent: end")            

        return
        
    def onEventAuthenticated(self, event):
        session = event.getSessionId()
        sessionAttrs = session.getSessionAttributes()
        session_id = session.getId()
        user = session.getUser()
        userDN = session.getUserDn()
        uid = user.getUserId()
        # edipi = user.getAttribute("edipi")
        client_id = sessionAttrs.get("client_id")
        redirect_uri = sessionAttrs.get("redirect_uri")
        acr = sessionAttrs.get("acr_values")
        ip = event.getHttpRequest().getRemoteAddr()
        print('ApplicationSession.onEvent: {"sessionId": "%s", "uid": "%s", "client_id": "%s", "redirect_uri": "%s", "acr": "%s", "ip": "%s"}' % (session_id, uid, client_id, redirect_uri, acr, ip))

        ########################################################################
        # Don't allow more then one session!
        ########################################################################
        entity = SessionId()
        entity.setDn(self.staticConfiguration.getBaseDn().getSessions())
        entity.setUserDn(userDN)
        entity.setState(SessionIdState.AUTHENTICATED)
        results = self.entryManager.findEntries(entity)
        if results == 1:
            facesMessages = CdiUtil.bean(FacesMessages)
            facesMessages.add(FacesMessage.SEVERITY_ERROR, "Please, end active session first!")
            print("User %s denied session--must end active session first" % uid)
            return

        ########################################################################
        # Audit Log enhancements to store additional data in LDAP.
        #
        # The goal is to create a record here that can be exported and
        # reported on at a later time.
        #
        # dn=uniqueIdentifier={guid},ou={year-month},ou=audit,o=metric
        # objectclass: top
        # objectclass: jansMetric
        # uniqueIdentifier: {guid}
        # jansMetricTyp: audit
        # creationDate: {timestamp}
        # jansAppTyp: client_id
        # jansData: {'uid':'foobar',
        #          'edipi':'12321321',
        #          'type': 'startSession',
        #          'redirect_uri': 'https://abc.com/cb'
        #          'ip': '10.10.10.10',
        #          'acr': 'smartcard',
        #          'session_id': "1234"}
        ########################################################################
        
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
                print("Creating organizational unit: %s" % auditDN)
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
                print("Creating organizational unit: %s" % yearMonthDN)
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
        print("ApplicationSession.onEvent: type(curr_date) = %s" % type(curr_date))

        dn = "uniqueIdentifier=%s,ou=%s,ou=%s,ou=statistic,o=metric" % (uniqueIdentifier, yearMonth, self.metric_audit_ou_name)

        metricEntity = ZTrustMetricEntry()

        metricEntity.setDn(dn)
        metricEntity.setId(uniqueIdentifier)
        metricEntity.setCreationDate(curr_date)
        metricEntity.setApplicationType(ApplicationType.OX_AUTH)
        metricEntity.setMetricType("audit")
 
#        data = """{"sessionId": "%s", "uid": "%s", "client_id": "%s", "redirect_uri": "%s", "acr": "%s", "ip": "%s", "type": "startSession"}""" % (session_id, uid, client_id, redirect_uri, acr, ip)
        data = """{"sessionId": "%s", "uid": "%s", "client_id": "%s", "redirect_uri": "%s", "acr": "%s", "ip": "%s", "type": "%s"}""" % (session_id, uid, client_id, redirect_uri, acr, ip, str(event.getType()))

        metricEntity.setJansData(data)

        print("ApplicationSession.onEvent: metricEntity = %s" % metricEntity)
        self.entryManager.persist(metricEntity)
        print("ApplicationSession.startSession: Wrote metric entry %s" % dn)
        print("ApplicationSession.onEvent: end")
        return    

    def onEventGone(self, event):
        session = None
        sessionAttrs = None
        session_id = None
        userDN = None 
        user = None
        uid = None
        
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

        print('ApplicationSession.onEvent: {"sessionId": "%s", "uid": "%s", "client_id": "%s", "redirect_uri": "%s", "acr": "%s"}' % (session_id, uid, client_id, redirect_uri, acr))

        ########################################################################
        # Don't allow more then one session!
        ########################################################################
        entity = SessionId()
        entity.setDn(self.staticConfiguration.getBaseDn().getSessions())
        entity.setUserDn(userDN)
        entity.setState(SessionIdState.UNAUTHENTICATED)
        results = self.entryManager.findEntries(entity)
        if results == 1:
            facesMessages = CdiUtil.bean(FacesMessages)
            facesMessages.add(FacesMessage.SEVERITY_ERROR, "Please, end active session first!")
            print("User %s denied session--must end active session first" % uid)
            return

        ########################################################################
        # Audit Log enhancements to store additional data in LDAP.
        #
        # The goal is to create a record here that can be exported and
        # reported on at a later time.
        #
        # dn=uniqueIdentifier={guid},ou={year-month},ou=audit,o=metric
        # objectclass: top
        # objectclass: jansMetric
        # uniqueIdentifier: {guid}
        # jansMetricTyp: audit
        # creationDate: {timestamp}
        # jansAppTyp: client_id
        # jansData: {'uid':'foobar',
        #          'edipi':'12321321',
        #          'type': 'startSession',
        #          'redirect_uri': 'https://abc.com/cb'
        #          'acr': 'smartcard',
        #          'session_id': "1234"}
        ########################################################################
        
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
                print("Creating organizational unit: %s" % auditDN)
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
                print("Creating organizational unit: %s" % yearMonthDN)
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
        print("ApplicationSession.onEvent: type(curr_date) = %s" % type(curr_date))

        dn = "uniqueIdentifier=%s,ou=%s,ou=%s,ou=statistic,o=metric" % (uniqueIdentifier, yearMonth, self.metric_audit_ou_name)

        metricEntity = ZTrustMetricEntry()

        metricEntity.setDn(dn)
        metricEntity.setId(uniqueIdentifier)
        metricEntity.setCreationDate(curr_date)
        metricEntity.setApplicationType(ApplicationType.OX_AUTH)
        metricEntity.setMetricType("audit")
 
#        data = """{"sessionId": "%s", "uid": "%s", "client_id": "%s", "redirect_uri": "%s", "acr": "%s", "ip": "%s", "type": "startSession"}""" % (session_id, uid, client_id, redirect_uri, acr, ip)
        data = """{"sessionId": "%s", "uid": "%s", "client_id": "%s", "redirect_uri": "%s", "acr": "%s", "type": "%s"}""" % (session_id, uid, client_id, redirect_uri, acr, str(event.getType()))

        metricEntity.setJansData(data)

        print("ApplicationSession.onEvent: metricEntity = %s" % metricEntity)
        self.entryManager.persist(metricEntity)

        print("ApplicationSession.startSession: Wrote metric entry %s" % dn)
        print("ApplicationSession.onEvent: end")
        return    

    # This method is called for both authenticated and unauthenticated sessions
    #   httpRequest is javax.servlet.http.HttpServletRequest
    #   sessionId is org.gluu.oxauth.model.common.SessionId
    #   configurationAttributes is java.util.Map<String, SimpleCustomProperty>
    def startSession(self, httpRequest, sessionId, configurationAttributes):
        print("ApplicationSession.startSession for sessionId: {}".format(sessionId.getId()))
        return True

    # Application calls it at end session request to allow notify 3rd part systems
    #   httpRequest is javax.servlet.http.HttpServletRequest
    #   sessionId is org.gluu.oxauth.model.common.SessionId
    #   configurationAttributes is java.util.Map<String, SimpleCustomProperty>
    def endSession(self, httpRequest, sessionId, configurationAttributes):
        if sessionId:
            print("ApplicationSession.endSession for sessionId: {}".format(sessionId.getId()))
        else:
            print("ApplicationSession.endSession: sessionId object not found")
        return True
