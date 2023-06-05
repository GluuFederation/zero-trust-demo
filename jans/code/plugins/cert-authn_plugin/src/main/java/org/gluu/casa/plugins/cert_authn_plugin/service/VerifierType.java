package org.gluu.casa.plugins.cert_authn_plugin.service;

public enum VerifierType {

    GENERIC("use_generic_validator"),
    PATH("use_path_validator"),
    OCSP("use_ocsp_validator"),
    CRL("use_crl_validator");

    private String param;

    VerifierType(String param) {
        this.param = param;
    }

    public String getParam() {
        return param;
    }

}
