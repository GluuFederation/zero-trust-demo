package org.gluu.casa.plugins.credentials.extensions;

import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import org.gluu.casa.credential.BasicCredential;
import org.gluu.casa.extension.AuthnMethod;
import org.gluu.casa.misc.Utils;
import org.gluu.casa.plugins.emailenroll.EmailEnrollService;

import org.gluu.casa.service.ISessionContext;
import org.pf4j.Extension;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Extension
public class EmailEnrollAuthnMethod implements AuthnMethod{

	private Logger logger = LoggerFactory.getLogger(EmailEnrollAuthnMethod.class);
	private ISessionContext sessionContext;

	public EmailEnrollAuthnMethod() {
		sessionContext = Utils.managedBean(ISessionContext.class);
	}
	
	@Override
	public String getPanelBottomTextKey() {
		return "";
	}

	@Override
	public boolean mayBe2faActivationRequisite() {
		return Boolean.parseBoolean(Optional
				.ofNullable(EmailEnrollService.getInstance().getScriptPropertyValue("2fa_requisite")).orElse("false"));
	}

	@Override
	public List<BasicCredential> getEnrolledCreds(String arg0) {
		try {
			return EmailEnrollService.getInstance().getCredentials(sessionContext.getLoggedUser().getUserName()).stream()
					.map(dev -> new BasicCredential(dev.getNickName(), 0)).collect(Collectors.toList());
		} catch (Exception e) {
			logger.error(e.getMessage(), e);
			return Collections.emptyList();
		}
	}
	
    @Override
    public String getAcr() {
        return EmailEnrollService.ACR;
    }

	@Override
	public String getPageUrl() {
		return "user/cred_details.zul";
	}

	@Override
	public String getPanelButtonKey() {
		return "email_panel.button";
	}

	@Override
	public String getPanelTextKey() {
		return "email_panel.text";
	}

	@Override
	public String getPanelTitleKey() {
		return "email.title";
	}
	
    @Override
    public String getUINameKey() {
        return "email.title";
    }

	@Override
	public int getTotalUserCreds(String arg0) {
		String userName = sessionContext.getLoggedUser().getUserName();
		return EmailEnrollService.getInstance().getCredentialsTotal(userName);
	}

	@Override
	public void reloadConfiguration() {
		EmailEnrollService.getInstance().reloadConfiguration();
	}

}
