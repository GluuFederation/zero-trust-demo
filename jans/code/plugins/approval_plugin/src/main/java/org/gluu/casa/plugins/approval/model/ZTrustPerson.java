package org.gluu.casa.plugins.approval.model;

import io.jans.orm.annotation.AttributeName;
import io.jans.orm.annotation.DataEntry;
import io.jans.orm.annotation.ObjectClass;

/**
 * @author Sergey Manoylo
 * @version Sept 8, 2022
 */
@DataEntry
@ObjectClass(value = "ztrustPerson")
public class ZTrustPerson extends GluuPerson {
	
	/**
     * 
     */
    private static final long serialVersionUID = 5795708262790917897L;
	
	@AttributeName(name = "userStatus")
	private String userStatus;
	
	public String getUserStatus() {
		return userStatus;
	}

	public void setUserStatus(String userStatus) {
		this.userStatus = userStatus;
	}
	
	public boolean isUserActive() {
	    return userStatus.equalsIgnoreCase("active");
	}

    public boolean getUserActive() {
        return userStatus.equalsIgnoreCase("active");
    }
}
