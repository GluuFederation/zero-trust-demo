/**
 * 
 */
package io.jans.model.metric.sql;

import java.util.Date;

import io.jans.model.ApplicationType;
import io.jans.orm.annotation.AttributeName;
import io.jans.orm.annotation.DN;
import io.jans.orm.annotation.DataEntry;
import io.jans.orm.annotation.ObjectClass;

/**
 * @author Sergey Manoylo
 * @version June 2, 2023
 */
@DataEntry
@ObjectClass(value = "jansMetric")
public class ZTrustMetricEntry {
	
    @DN
    private String dn;

    @AttributeName(name = "uniqueIdentifier", ignoreDuringUpdate = true)
    private String id;

    @AttributeName(name = "creationDate")
    private Date creationDate;
	
    @AttributeName(name = "jansAppTyp")
    private ApplicationType applicationType;
    
    @AttributeName(name = "jansMetricTyp")
    private String metricType;    

    @AttributeName(name = "jansData")
    private String jansData;
    
    /**
     * 
     * @return
     */
    public String getDn() {
        return dn;
    }

    /**
     * 
     * @param dn
     */
    public void setDn(String dn) {
        this.dn = dn;
    }
    
    /**
     * 
     * @return
     */
    public String getId() {
        return id;
    }

    /**
     * 
     * @param id
     */
    public void setId(String id) {
        this.id = id;
    }    
    
    /**
     * 
     * @param applicationType
     */
    public void setApplicationType(ApplicationType applicationType) {
    	this.applicationType = applicationType;    	
    }

    /**
     * 
     * @return
     */
    public ApplicationType getApplicationType() {
    	return this.applicationType;    	
    }
    
    /**
     * 
     * @return
     */
    public String getMetricType() {
        return metricType;
    }

    /**
     * 
     * @param metricType
     */
    public void setMetricType(String metricType) {
        this.metricType = metricType;
    }    
    
    /**
     * 
     * @return
     */
    public Date getCreationDate() {
        return creationDate;
    }

    /**
     * 
     * @param creationDate
     */
    public void setCreationDate(Date creationDate) {
        this.creationDate = creationDate;
    }
    
    /**
     * 
     * @param jansData
     */
    public void setJansData(String jansData) {
    	this.jansData = jansData;    	
    }

    /**
     * 
     * @return
     */
    public String getJansData() {
    	return this.jansData;    	
    }    
    
}
