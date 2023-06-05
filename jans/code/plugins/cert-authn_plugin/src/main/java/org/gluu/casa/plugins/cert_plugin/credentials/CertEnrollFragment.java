package org.gluu.casa.plugins.cert_plugin.credentials;

import org.gluu.casa.extension.PreferredMethodFragment;

public class CertEnrollFragment implements PreferredMethodFragment {

	@Override
	public String getUrl() {
		return "fragment.zul";
	}

}
