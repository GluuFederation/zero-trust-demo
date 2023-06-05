package org.gluu.casa.plugins.cert_plugin.vm;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.gluu.casa.core.pojo.User;
import org.gluu.casa.credential.CredentialRemovalConflict;
import org.gluu.casa.plugins.cert_plugin.CertAuthenticationExtension;
import org.gluu.casa.plugins.cert_plugin.CertAuthenticationPlugin;
import org.gluu.casa.plugins.cert_plugin.model.Certificate;
import org.gluu.casa.plugins.cert_plugin.service.CertService;
import org.gluu.casa.service.ISessionContext;
import org.gluu.casa.ui.UIUtils;
import org.zkoss.bind.BindUtils;
import org.zkoss.bind.annotation.BindingParam;
import org.zkoss.bind.annotation.Command;
import org.zkoss.bind.annotation.Init;
import org.zkoss.util.Pair;
import org.zkoss.util.resource.Labels;
import org.zkoss.zk.ui.WebApps;
import org.zkoss.zk.ui.select.annotation.WireVariable;
import org.zkoss.zul.Messagebox;

import java.io.File;
import java.util.List;

/**
 * This is the ViewModel of page cert-detail.zul. It controls the display of
 * user certs
 */
public class CertAuthenticationSummaryVM {

	private static final Logger logger = LogManager.getLogger(CertAuthenticationSummaryVM.class);

	@WireVariable
	private ISessionContext sessionContext;

	private User user;
	private List<Certificate> certificates;
	private CertService certService;
	
    private String pluginId = null;

	public List<Certificate> getCertificates() {
		return certificates;
	}
	
	@Init
	public void init() {
		certService = CertService.getInstance();
		user = sessionContext.getLoggedUser();
		// sndFactorUtils = Utils.managedBean(SndFactorAuthenticationUtils.class);
		certificates = certService.getUserCerts(user.getId());
		
        CertAuthenticationPlugin plugin = CertAuthenticationPlugin.getInstance();
        pluginId = plugin.getWrapper().getPluginId();
	}

	public Pair<CredentialRemovalConflict, String> removalConflict(String credentialType, int nCredsOfType, User user) {
		Pair<CredentialRemovalConflict, String> pair = new Pair<CredentialRemovalConflict, String>(null, null);
		return pair;
	};

	@Command
	public void delete(@BindingParam("cert") Certificate certificate) {
		
		String resetMessages = removalConflict(CertAuthenticationExtension.ACR, certificates.size(), user).getY();
		
		boolean reset = resetMessages != null;
		Pair<String, String> delMessages = getDeleteMessages(resetMessages);

		Messagebox.show(delMessages.getY(), delMessages.getX(), Messagebox.YES | Messagebox.NO,
				reset ? Messagebox.EXCLAMATION : Messagebox.QUESTION, event -> {
					if (Messagebox.ON_YES.equals(event.getName())) {
						try {
							boolean success = certService.removeFromUser(certificate.getFingerPrint(), user.getId());
							if (success) {
								if (reset) {
									//sndFactorUtils.turn2faOff(user);
								}
								certificates.remove(certificate);

								BindUtils.postNotifyChange(null, null, CertAuthenticationSummaryVM.this,
										"certificates");
							}
							UIUtils.showMessageUI(success);
						} catch (Exception e) {
							UIUtils.showMessageUI(false);
							logger.error(e.getMessage(), e);
						}
					}
				});

	}

	private Pair<String, String> getDeleteMessages(String msg) {

		StringBuilder text = new StringBuilder();
		if (msg != null) {
			text.append(msg).append("\n\n");
		}
		text.append(Labels.getLabel("usercert.del_confirm"));
		if (msg != null) {
			text.append("\n");
		}

		return new Pair<>(null, text.toString());

	}
	
	public boolean isCountryValid(final String countryCode) {

	    boolean res = false;

	    String relFilePath = String.format("pl/%s/img/flags_32/%s_32.png", pluginId, countryCode.toLowerCase());
	    String filePath = WebApps.getCurrent().getRealPath(relFilePath);

	    File file = new File(filePath);
	    res = file.exists();
	    
	    return res;
	}
}
