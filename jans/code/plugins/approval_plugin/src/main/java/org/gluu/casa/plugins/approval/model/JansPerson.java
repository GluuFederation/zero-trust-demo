/**
 * 
 */
package org.gluu.casa.plugins.approval.model;

import java.util.HashSet;
import java.util.Optional;

import io.jans.orm.annotation.AttributeName;
import io.jans.orm.annotation.DataEntry;
import io.jans.orm.annotation.ObjectClass;
import io.jans.orm.model.base.SimpleUser;

/**
 * @author Sergey Manoylo
 * @version Sept 8, 2022
 */
@DataEntry
@ObjectClass(value = "jansPerson")
public class JansPerson extends SimpleUser {

    /**
     * 
     */
    private static final long serialVersionUID = -5672094570004725636L;

    @AttributeName(name = "givenName", ignoreDuringUpdate = true)
    private String givenName;

    @AttributeName(name = "sn", ignoreDuringUpdate = true)
    private String sn;

    @AttributeName(name = "jansStatus")
    private String status;

    @AttributeName(name = "mail", ignoreDuringUpdate = true)
    private String mail;

    public String getMail() {
        return mail;
    }

    public void setMail(String mail) {
        this.mail = mail;
    }

    public String getFormattedName() {
        String name = Optional.ofNullable(givenName).orElse("");
        String surname = Optional.ofNullable(sn).orElse("");
        return String.format("%s %s", name, surname);
    }
    
    public HashSet<String> getKeywords(){
        HashSet<String> keywords = new HashSet<>();
        String name = Optional.ofNullable(givenName).orElse("");
        String surname = Optional.ofNullable(sn).orElse("");
        String email = mail;
        keywords.add(name.toLowerCase());
        keywords.add(surname.toLowerCase());
        keywords.add(email.toLowerCase());
       
        return keywords;
    }

    public String getGivenName() {
        return givenName;
    }

    public void setGivenName(String givenName) {
        this.givenName = givenName;
    }

    public String getSn() {
        return sn;
    }

    public void setSn(String sn) {
        this.sn = sn;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

}
