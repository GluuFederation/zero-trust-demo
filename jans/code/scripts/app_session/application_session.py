
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
from java.util import GregorianCalendar
from java.util import TimeZone

#### Audit Entries Additional Imports ####
from io.jans.as.server.security import Identity
from io.jans.as.server.service import MetricService

from io.jans.orm.model.base import SimpleBranch
from io.jans.model.metric import MetricType

from io.jans.model import ApplicationType

from io.jans.as.server.service.external.session import SessionEventType

from io.jans.as.common.model.session import SessionId
from io.jans.as.common.model.session import SessionIdState

from io.jans.model.metric.audit import AuditMetricEntry
from io.jans.model.metric.audit import AuditMetricData

from io.jans.orm.model.base import CustomAttribute
from io.jans.orm.model.base import CustomEntry

from io.jans.orm.model.base import CustomObjectAttribute
from io.jans.orm.model.base import CustomObjectEntry

import java

import uuid
import time
import json
import ast

class ApplicationSession(ApplicationSessionType):

    session_attributes_map = {
            "dn": "dn",
            "userDn": "userDn",
            "id": "id",
            "outsideSid": "outsideSid",
            "lastUsedAt": "lastUsedAt",
            "authenticationTime": "authenticationTime",
            "expirationDate": "expirationDate",
            "sessionState": "sessionState",
            "permissionGranted": "permissionGranted",
            "deviceSecrets": "deviceSecrets"
        }

    session_cust_attributes_map = {
            "auth_external_attributes": "authExternalAttributes",
            "opbs": "opbs",
            "response_type": "responseType",
            "client_id": "clientId",
            "auth_step": "authStep",
            "acr": "acr",
            "casa_logoUrl": "casaLogoUrl",
            "remote_ip": "remoteIp",
            "scope": "scope",
            "acr_values": "acrValues",
            "casa_faviconUrl": "casaFaviconUrl",
            "redirect_uri": "redirectUri",
            "state": "state",
            "casa_prefix": "casaPrefix",
            "casa_contextPath": "casaContextPath",
            "casa_extraCss": "casaExtraCss"
        }

    def __init__(self, current_time_millis):
        self.currentTimeMillis = current_time_millis

    def init(self, configuration_attributes):
        print "ApplicationSession.init(): begin"

        self.metric_audit_ou_name = None
        self.metric_audit_conf_json_file_path = None

        self.event_types = None
        self.audit_data = None

        self.init_ok = False

        self.entry_manager = CdiUtil.bean(PersistenceEntryManager)
        self.static_configuration = CdiUtil.bean(StaticConfiguration)
        self.metric_service = CdiUtil.bean(MetricService)
        self.identity = CdiUtil.bean(Identity)

        try:
            self.metric_audit_ou_name = configuration_attributes.get("metric_audit_ou_name").getValue2()
            self.metric_audit_conf_json_file_path = configuration_attributes.get("metric_audit_conf_json_file_path").getValue2()
            self.event_types, self.audit_data = self.getMetricAuditParameters(self.metric_audit_conf_json_file_path)
            if self.event_types and self.audit_data:
                self.init_ok = True
        except Exception as ex:
            print("ApplicationSession.init(): error of initializing: ex = {}".format(ex))

        print("ApplicationSession.init(): self.event_types = {}".format(self.event_types))
        print("ApplicationSession.init(): self.audit_data = {}".format(self.audit_data))

        print("ApplicationSession.init(): self.init_ok = {}".format(self.init_ok))
        return True

    def destroy(self, configuration_attributes):
        print("ApplicationSession.destroy()")
        return True

    def getApiVersion(self):
        return 2

    # Called each time specific session event occurs
    # event is org.gluu.oxauth.service.external.session.SessionEvent
    def onEvent(self, event):

        print("ApplicationSession.onEvent(): event = {}".format(event))
        print("ApplicationSession.onEvent(): event.getType() = {}".format(event.getType()))
        print("ApplicationSession.onEvent(): event.getSessionId() = {}".format(event.getSessionId()))

        if not self.init_ok:
            print("ApplicationSession.onEvent(): isn't initialized")
            return

        if not(str(event.getType()).upper() in (event_type.upper() for event_type in self.event_types)):
            print("ApplicationSession.onEvent(): event {} will not be processed".format(event.getType()))
            return;

        remote_ip = event.getSessionId().getSessionAttributes()["remote_ip"]
        print("ApplicationSession.onEvent(): remote_ip = {}".format(remote_ip))

        session = None
        session_attrs = None
        session_id = None
        user_dn = None 
        user = None
        uid = None
        ip = None

        session = event.getSessionId()
        if session:
            session_attrs = session.getSessionAttributes()
            session_id = session.getId()
            user_dn = session.getUserDn()
            user = session.getUser()

        if user:
            uid = user.getUserId()

        if session_attrs:
            client_id = session_attrs.get("client_id")
            redirect_uri = session_attrs.get("redirect_uri")
            acr = session_attrs.get("acr_values")

        http_request = event.getHttpRequest()

        if http_request:
            ip = http_request.getRemoteAddr()

        print('ApplicationSession.onEvent(): {"sessionId": "%s", "uid": "%s", "client_id": "%s", "redirect_uri": "%s", "acr": "%s", "ip": "%s", "type": "%s"}' %
            (session_id, uid, client_id, redirect_uri, acr, ip, str(event.getType())))

        # Don't allow more then one session!
        entity = SessionId()
        entity.setDn(self.static_configuration.getBaseDn().getSessions())
        entity.setUserDn(user_dn)
        entity.setState(SessionIdState.UNAUTHENTICATED)
        results = self.entry_manager.findEntries(entity)
        if results == 1:
            faces_messages = CdiUtil.bean(FacesMessages)
            faces_messages.add(FacesMessage.SEVERITY_ERROR, "Please, end active session first!")
            print("ApplicationSession.onEvent(): User %s denied session--must end active session first" % uid)
            return

        # Audit Log enhancements to store additional data in LDAP.
        #
        # The goal is to create a record here that can be exported and
        # reported on at a later time.
        now = time.localtime(time.time())
        year_month = time.strftime("%Y%m", now)

        if self.entry_manager.hasBranchesSupport(""):
            print("ApplicationSession.onEvent(): self.entry_manager.hasBranchesSupport("") = %s" % str(self.entry_manager.hasBranchesSupport("")))
            # Create a base organization unit, for example
            # ou=audit,o=metric
            metric_dn = self.static_configuration.getBaseDn().getMetric().split(",")[1]
            print("ApplicationSession.onEvent(): metric_dn = %s" % metric_dn)
            audit_dn = "ou=%s,ou=statistic,%s" % (self.metric_audit_ou_name, metric_dn)
            print("ApplicationSession.onEvent(): audit_dn = %s" % audit_dn)

            # If audit organizational unit does not exist, create it
            ou_exists = self.entry_manager.contains(audit_dn, SimpleBranch)
            print("ApplicationSession.onEvent(): ou_exists = %s" % ou_exists)
            if not ou_exists:
                print("ApplicationSession.onEvent(): Creating organizational unit: %s" % audit_dn)
                branch = SimpleBranch()
                branch.setOrganizationalUnitName(self.metric_audit_ou_name)
                branch.setDn(audit_dn)
                print("ApplicationSession.onEvent(): branch = %s" % branch)
                self.entry_manager.persist(branch)

            # If there is no audit organizational unit for this month, create it
            year_month_dn = "ou=%s,%s" % (year_month, audit_dn)
            print("ApplicationSession.onEvent(): year_month_dn = %s" % year_month_dn)
            ou_exists = self.entry_manager.contains(year_month_dn, SimpleBranch)
            print("ApplicationSession.onEvent(): ou_exists = %s" % ou_exists)
            if not ou_exists:
                print("ApplicationSession.onEvent(): Creating organizational unit: %s" % year_month_dn)
                branch = SimpleBranch()
                branch.setOrganizationalUnitName(year_month)
                branch.setDn(year_month_dn)
                print("ApplicationSession.onEvent(): branch = %s" % branch)
                self.entry_manager.persist(branch)

        # Write the log
        # TODO Need to figure out edipi
        unique_identifier = str(uuid.uuid4())
        print("ApplicationSession.onEvent(): unique_identifier = %s" % unique_identifier)
        calendar_curr_date = Calendar.getInstance()
        curr_date = calendar_curr_date.getTime()

        dn = "uniqueIdentifier=%s,ou=%s,ou=%s,ou=statistic,o=metric" % (unique_identifier, year_month, self.metric_audit_ou_name)
        
        metric_entity = CustomObjectEntry();
        metric_entity.setDn(dn);
        metric_entity.setCustomObjectClasses(["jansMetric"])
#        metric_entity.setId(unique_identifier)

        custom_attribute = CustomObjectAttribute("uniqueIdentifier", unique_identifier)
        metric_entity.getCustomObjectAttributes().add(custom_attribute)        

        now = GregorianCalendar(TimeZone.getTimeZone("UTC")).getTime()
        
#        now_date_string = now
        now_date_string = self.entry_manager.encodeTime(dn, now)

        print("ApplicationSession.onEvent(): now_date_string = %s" % now_date_string)
        print("ApplicationSession.onEvent(): now = %s" % str(now))

#from io.jans.orm.model.base import CustomObjectAttribute
#from io.jans.orm.model.base import CustomObjectEntry

        custom_attribute = CustomObjectAttribute("creationDate", now)
        metric_entity.getCustomObjectAttributes().add(custom_attribute)

#       CustomEntry customEntry = new CustomEntry();
#       customEntry.setDn(user.getDn());
#       customEntry.setCustomObjectClasses(new String[] { "jansPerson" });

#       Date now = new GregorianCalendar(TimeZone.getTimeZone("UTC")).getTime();
#       String nowDateString = couchbaseEntryManager.encodeTime(customEntry.getDn(), now);
#       CustomAttribute customAttribute = new CustomAttribute("jansLastLogonTime", nowDateString);
#       customEntry.getCustomAttributes().add(customAttribute);
        
# from java.util import Date
# from java.util import Calendar
# from java.util import GregorianCalendar
# from java.util import TimeZone

#        metric_entity = AuditMetricEntry()

#        metric_entity.setDn(dn)
#        metric_entity.setId(unique_identifier)
#        metric_entity.setCreationDate(curr_date)
#        metric_entity.setApplicationType(ApplicationType.OX_AUTH)
#        metric_entity.setMetricType(MetricType.AUDIT)

#       audit_metric_data = self.getAuditMetricData(event, self.audit_data)

#        metric_entity.setMetricData(audit_metric_data)

        print("ApplicationSession.onEvent(): metric_entity = %s" % metric_entity)
        self.entry_manager.persist(metric_entity)
        print("ApplicationSession.onEvent(): Wrote metric entry %s" % dn)
        print("ApplicationSession.onEvent(): end")

        return

    # This method is called for both authenticated and unauthenticated sessions
    #   http_request is javax.servlet.http.HttpServletRequest
    #   session_id is org.gluu.oxauth.model.common.SessionId
    #   configuration_attributes is java.util.Map<String, SimpleCustomProperty>
    def startSession(self, http_request, session_id, configuration_attributes):
        print("ApplicationSession.startSession()")
        if not self.init_ok:
            print("ApplicationSession.startSession(): isn't initialized")
            return True

        ip = None
        if http_request:
            ip = http_request.getRemoteAddr()

        remote_ip = session_id.getSessionAttributes()["remote_ip"]
        print("ApplicationSession.startSession(): remote_ip = {}".format(remote_ip))

        print("ApplicationSession.startSession(): http_request = {}".format(http_request))
        print("ApplicationSession.startSession(): session_id = {}".format(session_id))
        print("ApplicationSession.startSession(): ip = {}".format(ip))
        print("ApplicationSession.startSession(): configuration_attributes = {}".format(configuration_attributes))

        print("ApplicationSession.startSession(): for session_id: {}".format(session_id.getId()))

        return True

    # Application calls it at end session request to allow notify 3rd part systems
    #   http_request is javax.servlet.http.HttpServletRequest
    #   session_id is org.gluu.oxauth.model.common.SessionId
    #   configuration_attributes is java.util.Map<String, SimpleCustomProperty>
    def endSession(self, http_request, session_id, configuration_attributes):
        print("ApplicationSession.endSession()")
        if not self.init_ok:
            print("ApplicationSession.endSession: isn't initialized")
            return True

        ip = None
        if http_request:
            ip = http_request.getRemoteAddr()

        remote_ip = session_id.getSessionAttributes()["remote_ip"]
        print("ApplicationSession.endSession(): remote_ip = {}".format(remote_ip))

        print("ApplicationSession.endSession(): http_request = {}".format(http_request))
        print("ApplicationSession.endSession(): session_id = {}".format(session_id))
        print("ApplicationSession.endSession(): ip = {}".format(ip))
        print("ApplicationSession.endSession(): configuration_attributes = {}".format(configuration_attributes))
        
        print("ApplicationSession.endSession(): for session_id: {}".format(session_id.getId()))        
            
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
        print("ApplicationSession.getMetricAuditParameters(): event_types = {}".format(event_types))
        print("ApplicationSession.getMetricAuditParameters(): audit_data = {}".format(audit_data))
        return event_types, audit_data

    def getAuditMetricData(self, event, audit_data):
        session = event.getSessionId()
        audit_metric_data = AuditMetricData()

        print("ApplicationSession.getAuditMetricData(): session = {0}".format(session))

        if "type".upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            audit_metric_data.setType(str(event.getType()))

        #empty first call
        attr_value = getattr(session, "userDn")

        for attr_key, attr_name in self.session_attributes_map.items():
            print("ApplicationSession.getAuditMetricData(): attr_key = {0}, attr_name = {1}".format(attr_key, attr_name))
            if attr_key.upper() in (audit_data_el.upper() for audit_data_el in audit_data):
                try:
                    attr_value = getattr(session, attr_key)
                    print("ApplicationSession.getAuditMetricData(): attr_key = {0}, attr_value = {1}".format(attr_key, attr_value))
                    setattr(audit_metric_data, attr_name, attr_value)
                except Exception as ex:
                    print("ApplicationSession.getAuditMetricData(): Error: ex = {0}".format(ex))

        attr_key = "state"
        attr_name = "authState"

        if attr_key.upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            try:
                attr_value = getattr(session, attr_key)
                print("ApplicationSession.getAuditMetricData(): attr_key = {0}, attr_value = {1}".format(attr_key, attr_value))
                setattr(audit_metric_data, attr_name, str(attr_value))
            except Exception as ex:
                print("ApplicationSession.getAuditMetricData(): Error Reading of config file: ex = {0}".format(ex))

        attr_key = "permissionGrantedMap"
        attr_name = "permissionGrantedMap"

        if attr_key.upper() in (audit_data_el.upper() for audit_data_el in audit_data):
            try:
                attr_value = getattr(session, attr_key)
                print("ApplicationSession.getAuditMetricData(): attr_key = {0}, attr_value = {1}".format(attr_key, attr_value))
                setattr(audit_metric_data, attr_name, attr_value.getPermissionGranted())
            except Exception as ex:
                print("ApplicationSession.getAuditMetricData(): Error: ex = {0}".format(ex))

        session_cust_attributes = {}

        if session:
            session_cust_attributes = session.getSessionAttributes()

        for cust_attr_key, cust_attr_name in self.session_cust_attributes_map.items():
            print("ApplicationSession.getAuditMetricData(): cust_attr_key = {0}, cust_attr_name = {0}".format(cust_attr_key, cust_attr_name))
            if ("sessionAttributes".upper() in (audit_data_el.upper() for audit_data_el in audit_data) or
                    not ("sessionAttributes".upper() in (audit_data_el.upper() for audit_data_el in audit_data)) and
                    cust_attr_key.upper() in (audit_data_el.upper() for audit_data_el in audit_data)):            
                try:
                    cust_attr_value = session_cust_attributes[cust_attr_key]
                    print("ApplicationSession.getAuditMetricData(): cust_attr_name = {0}, cust_attr_value = {1}".format(cust_attr_name, cust_attr_value))
                    setattr(audit_metric_data, cust_attr_name, cust_attr_value)
                except Exception as ex:
                    print("ApplicationSession.getAuditMetricData(): Error: ex = {0}".format(ex))

        return audit_metric_data
