package org.gluu.casa.plugins.emailenroll;

import org.gluu.casa.core.pojo.User;
import org.gluu.casa.misc.Utils;
import org.gluu.casa.plugins.emailenroll.model.UserPerson;
import org.gluu.casa.service.IPersistenceService;
import org.gluu.casa.service.ISessionContext;
import org.gluu.casa.ui.UIUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.zkoss.bind.BindUtils;
import org.zkoss.bind.annotation.Command;
import org.zkoss.bind.annotation.Init;
import org.zkoss.bind.annotation.NotifyChange;

import org.zkoss.zk.ui.select.annotation.WireVariable;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class EmailEnrollVM {

    private static final Logger logger = LoggerFactory.getLogger(EmailEnrollVM.class);

    private static final String DEF_EMAIL_REGEX = "(?!^[.+&'_-]*@.*$)(^[_\\w\\d+&'-]+(\\.[_\\w\\d+&'-]*)*@[\\w\\d-]+(\\.[\\w\\d-]+)*\\.(([\\d]{1,3})|([\\w]{2,}))$)";  

    private String message;
    private String email;
    private IPersistenceService persistenceService;
    @WireVariable
    private ISessionContext sessionContext;
    private UserPerson person;
    private User user;
    private Pattern pattern;
    
    /**
     * Getter of private class field <code>email</code>.
     * @return A string with the value of the organization name found in your Gluu installation. Find this value in
     * Gluu Server oxTrust GUI at "Configuration" &gt; "Organization configuration"
     */
    public String getEmail() {
        return email;
    }

    /**
     * Getter of private class field <code>message</code>.
     * @return A string value
     */
    public String getMessage() {
        return message;
    }

    /**
     * Setter of private class field <code>message</code>.
     * @param message A string with the contents typed in text box of page index.zul
     */
    public void setMessage(String message) {
        this.message = message;
       
    }

    /**
     * Initialization method for this ViewModel.
     */
    @NotifyChange("email")
    @Init
    public void init() {
        persistenceService = Utils.managedBean(IPersistenceService.class);
//        persistenceService.initialize();
        user = sessionContext.getLoggedUser();
        person = new UserPerson();
        person.setBaseDn(persistenceService.getPeopleDn());
        person.setUid(user.getUserName());
        person = persistenceService.find(person).stream().findFirst().orElse(null);
        email = person.getMail();
        logger.info("Email Enroll ViewModel inited {}",email);
    }
    
    public Pattern getEmailRegex() {
        //(?!^[.+&'_-]*@.*$)(^[_\w\d+&'-]+(\.[_\w\d+&'-]*)*@[\w\d-]+(\.[\w\d-]+)*\.(([\d]{1,3})|([\w]{2,}))$)
        pattern = Pattern.compile(DEF_EMAIL_REGEX);
        return pattern;
    }

    /**
     * The method called when the button on page <code>index.zul</code> is pressed. It sets the value for
     * <code>email</code>.
     */
    
    @NotifyChange("email")
    @Command
    public void setMail() {
        try {
            Matcher matcher = getEmailRegex().matcher(message);
            if (matcher.matches()) {
                person.setMail(message);
                persistenceService.modify(person);
                email = message;
                BindUtils.postNotifyChange(null, null,this,"email");
                UIUtils.showMessageUI(true);
            } else {
                UIUtils.showMessageUI(false,"Invalid Email!");
                logger.error("Invalid Email: " + email);
            }

        } catch(Exception e) {
            UIUtils.showMessageUI(false);
            logger.error(e.getMessage());            
        }
    }
   
    
}
