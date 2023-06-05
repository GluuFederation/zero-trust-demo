package org.gluu.casa.plugins.cert_authn_plugin;

import org.pf4j.Plugin;
import org.pf4j.PluginWrapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CertAuthenticationPlugin extends Plugin {
    
    private final static Logger logger = LoggerFactory.getLogger(CertAuthenticationPlugin.class);    
    
    private static CertAuthenticationPlugin instance = null;

    /**
     * 
     * @param wrapper
     */
    public CertAuthenticationPlugin(PluginWrapper wrapper) {
        super(wrapper);
        logger.info("CertAuthenticationPlugin.CertAuthenticationPlugin()");
        synchronized(CertAuthenticationPlugin.class) {
            instance = this;
        }
    }
    
    /**
     * 
     * @return
     */
    public synchronized static CertAuthenticationPlugin getInstance() {
        return instance;
    }

}
