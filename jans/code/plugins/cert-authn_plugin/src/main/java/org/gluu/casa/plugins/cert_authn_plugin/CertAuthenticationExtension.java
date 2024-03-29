package org.gluu.casa.plugins.cert_authn_plugin;

import org.gluu.casa.credential.BasicCredential;
import org.gluu.casa.extension.AuthnMethod;
import org.gluu.casa.plugins.cert_authn_plugin.service.CertService;
import org.pf4j.Extension;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Extension
public class CertAuthenticationExtension implements AuthnMethod {

    private final static Logger logger = LoggerFactory.getLogger(CertAuthenticationExtension.class);

    public final static String ACR = "ztrust-cert";

    private CertService certService;

    public CertAuthenticationExtension() {
        certService = CertService.getInstance();
    }

    public String getUINameKey() {
        return "usrcert.cert_label";
    }

    public String getAcr() {
        return ACR;
    }

    public String getPanelTitleKey() {
        return "usrcert.cert_title";
    }

    public String getPanelTextKey() {
        return "usrcert.cert_text";
    }

    public String getPanelButtonKey() {
        return "usrcert.cert_manage";
    }

    public String getPageUrl() {
        return "cert-detail.zul";
    }

    public List<BasicCredential> getEnrolledCreds(String id) {
        logger.info("CertAuthenticationExtension.getEnrolledCreds(): id = " + id);
        try {
            return certService.getUserCerts(id).stream()
                    .map(cert -> new BasicCredential(cert.getFormattedName(), -1)).collect(Collectors.toList());
        } catch (Exception e) {
            logger.error(e.getMessage(), e);
            return Collections.emptyList();
        }
    }

    public void reloadConfiguration() {
        certService.reloadConfiguration();
    }

    public int getTotalUserCreds(String id) {
        return certService.getDevicesTotal(id);
    }

}
