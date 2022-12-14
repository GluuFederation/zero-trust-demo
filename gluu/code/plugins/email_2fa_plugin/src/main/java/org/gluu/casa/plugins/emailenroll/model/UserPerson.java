package org.gluu.casa.plugins.emailenroll.model;

import org.gluu.casa.core.model.BasePerson;
import org.gluu.persist.annotation.AttributeName;
import org.gluu.persist.annotation.DataEntry;
import org.gluu.persist.annotation.ObjectClass;

@DataEntry
@ObjectClass("gluuPerson")
public class UserPerson extends BasePerson{

    /**
     * 
     */
    private static final long serialVersionUID = 5588408515604090049L;

    @AttributeName(name = "oxEmailAlternate")
    private String oxEmailAlternate;

    @AttributeName(name = "mail")
    private String mail;

    public String getOxEmailAlternate() {
        return oxEmailAlternate;
    }

    public void setOxEmailAlternate(String oxEmailAlternate) {
        this.oxEmailAlternate = oxEmailAlternate;
    }

    public String getMail() {
        return mail;
    }

    public void setMail(String mail) {
        this.mail = mail;
    }

}
