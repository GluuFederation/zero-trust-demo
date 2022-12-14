package org.gluu.casa.plugins.cert.credentials;

import java.util.Collections;
import java.util.List;
import java.util.Optional;

import org.gluu.casa.credential.BasicCredential;
import org.gluu.casa.extension.AuthnMethod;
import org.gluu.casa.plugin.misc.Utils;
import org.gluu.casa.plugins.cert.service.CertService;

import org.gluu.casa.service.ISessionContext;
import org.pf4j.Extension;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Extension
public class CertEnrollAuthnMethod implements AuthnMethod{
	private Logger logger = LoggerFactory.getLogger(getClass());
	private ISessionContext sessionContext;
	public CertEnrollAuthnMethod() {
		sessionContext = Utils.managedBean(ISessionContext.class);
	}
	
	@Override
	public String getPanelBottomTextKey() {
		return "";
	}

	@Override
	public boolean mayBe2faActivationRequisite() {
		return Boolean.parseBoolean(Optional
				.ofNullable(CertService.getInstance().getScriptPropertyValue("2fa_requisite")).orElse("false"));
		
	}

	@Override
	public String getAcr() {
		return CertService.ACR;
	}

	@Override
	public List<BasicCredential> getEnrolledCreds(String arg0) {
		try {
			return CertService.getInstance().getCredentials(sessionContext.getLoggedUser().getUserName());
		} catch (Exception e) {
			logger.error(e.getMessage(), e);
			return Collections.emptyList();
		}
	}

	@Override
	public String getPageUrl() {
		return "cert-details.zul";
	}

	@Override
	public String getPanelButtonKey() {
		return "panel.button";
	}

	@Override
	public String getPanelTextKey() {
		return "panel.test";
	}

	@Override
	public String getPanelTitleKey() {
		return "usrcert.cert_title";
	}

	@Override
	public int getTotalUserCreds(String arg0) {
		return CertService.getInstance().getDevicesTotal(sessionContext.getLoggedUser().getUserName());
	}

	@Override
	public String getUINameKey() {
		return "usrcert.cert_title";
	}

	@Override
	public void reloadConfiguration() {
	    CertService.getInstance().reloadConfiguration();
	}

}
