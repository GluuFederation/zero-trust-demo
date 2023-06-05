package org.gluu.casa.plugins.email_2fa_plugin.service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.gluu.casa.credential.BasicCredential;
import org.gluu.casa.misc.Utils;
import org.gluu.casa.plugins.email_2fa_plugin.model.EmailPerson;
import org.gluu.casa.service.IPersistenceService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.databind.ObjectMapper;

public class Email2faService {

	private static final Logger logger = LoggerFactory.getLogger(Email2faService.class);

	public static String ACR = "ztrust-email_2fa_plugin";

	private static Email2faService SINGLE_INSTANCE = null;
	public static Map<String, String> properties;

	private IPersistenceService persistenceService;
	private EmailPerson person;

	private Email2faService() {
		persistenceService = Utils.managedBean(IPersistenceService.class);
		reloadConfiguration();
	}

	public static Email2faService getInstance() {
		if (SINGLE_INSTANCE == null) {
			synchronized (Email2faService.class) {
				SINGLE_INSTANCE = new Email2faService();
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
		
		person = new EmailPerson();
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
