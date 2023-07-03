/**
 * 
 */
package io.jans.orm.model.base;

import java.util.Date;
import java.util.List;
import java.sql.Timestamp;

/**
 * @author Sergey Manoylo
 * @version June 30, 2023
 */
public class ZTrustCustomAttribute extends CustomAttribute {

	/**
	 * 
	 */
	private static final long serialVersionUID = -914479026360407887L;
	
	/**
	 * 
	 */
    public ZTrustCustomAttribute() {
    	super();
    }

    /**
     * 
     * @param name
     */
    public ZTrustCustomAttribute(String name) {
    	super(name);
    }

    /**
     * 
     * @param name
     * @param value
     */
    public ZTrustCustomAttribute(String name, String value) {
    	super(name, value);
    }

    /**
     * 
     * @param name
     * @param values
     */
    public ZTrustCustomAttribute(String name, List<String> values) {
    	super(name, values);    	
    }	

	/**
	 * 
	 * @param attributeName
	 * @param attributeValue
	 */
    public ZTrustCustomAttribute(String attributeName, Date attributeValue) {
    	setName(attributeName);    	
        setValue(new Timestamp(attributeValue.getTime()).toString());
    }
    
	/**
	 * 
	 * @param attributeName
	 * @param attributeValue
	 */
    public ZTrustCustomAttribute(String attributeName, Date attributeValue, Boolean multiValued) {
    	setName(attributeName);
        setValue(new Timestamp(attributeValue.getTime()).toString());
        if (multiValued != null) {
            setMultiValued(multiValued);
        }        
    }

    /**
     * 
     * @param attributeName
     * @param attributeValue
     * @param multiValued
     */
    public void setAttribute(String attributeName, Date attributeValue) {
    	setName(attributeName);
    	setValue(new Timestamp(attributeValue.getTime()).toString());    	
    }
    
    /**
     * 
     * @param attributeName
     * @param attributeValue
     * @param multiValued
     */
    public void setAttribute(String attributeName, Date attributeValue, Boolean multiValued) {
    	setName(attributeName);
    	setValue(new Timestamp(attributeValue.getTime()).toString());
        if (multiValued != null) {
            setMultiValued(multiValued);
        }        
    }

    /**
     * 
     * @param attributeValue
     * @return
     */
    public String getDateString(Date attributeValue) {
    	return attributeValue.toString();
    }

    /**
     * 
     * @param attributeValue
     * @return
     */
    public String getDateString1(Date attributeValue) {
    	Timestamp timestamp = new Timestamp(attributeValue.getTime());
    	return timestamp.toString();
    }
        
}
