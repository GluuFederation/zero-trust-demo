package org.gluu.casa.plugins.emailenroll;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.gluu.casa.credential.BasicCredential;
import org.gluu.casa.misc.Utils;
import org.gluu.casa.plugins.emailenroll.model.UserPerson;
import org.gluu.casa.service.IPersistenceService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.databind.ObjectMapper;

public class EmailEnrollService {

	private static final Logger logger = LoggerFactory.getLogger(EmailEnrollService.class);

	public static String ACR = "ztrust-email_2fa_plugin";

	private static EmailEnrollService SINGLE_INSTANCE = null;
	public static Map<String, String> properties;

	private IPersistenceService persistenceService;
	private UserPerson person;

	private EmailEnrollService() {
		persistenceService = Utils.managedBean(IPersistenceService.class);
		reloadConfiguration();
	}

	public static EmailEnrollService getInstance() {
		if (SINGLE_INSTANCE == null) {
			synchronized (EmailEnrollService.class) {
				SINGLE_INSTANCE = new EmailEnrollService();
			}
		}
		return SINGLE_INSTANCE;
	}

	public void reloadConfiguration() {
		ObjectMapper mapper = new ObjectMapper();
		properties = persistenceService.getCustScriptConfigProperties(ACR);
		if (properties == null) {
			logger.warn(
					"Config. properties for custom script '{}' could not be read. Features related to {} will not be accessible",
					ACR, ACR.toUpperCase());
		} else {
			try {
				logger.info("Sample settings found were: {}", mapper.writeValueAsString(properties));
			} catch (Exception e) {
				logger.error(e.getMessage(), e);
			}
		}
	}
	
	public String getScriptPropertyValue(String value) {
		return properties.get(value);
	}

	public List<BasicCredential> getCredentials(String uniqueIdOfTheUser) {
		// Write the code to connect to the 3rd party API and fetch credentials against
		// the user
		
		person = new UserPerson();
		person.setBaseDn(persistenceService.getPeopleDn());
		person.setUid(uniqueIdOfTheUser);
		person = persistenceService.find(person).stream().findFirst().orElse(null);
		List<BasicCredential> list = new ArrayList<BasicCredential>();
		list.add(new BasicCredential("Email: "+person.getMail(), System.currentTimeMillis()));
		
		return list;
	}
	public int getCredentialsTotal(String uniqueIdOfTheUser) {
		// Write the code to connect to the 3rd party API and fetch total number of
		// credentials against the user
		return 1;
	}
}
