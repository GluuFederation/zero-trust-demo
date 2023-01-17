package org.gluu.casa.plugins.cert.model;

import java.util.ArrayList;
import java.util.List;

public class Certificate implements Comparable<Certificate> {

//    private String formattedName;
//    private String commonName;
//    private String organization;
//    private String location;

    private List<String> commonName = new ArrayList<>();
    private List<String> organization = new ArrayList<>();
    private List<String> organizationUnit = new ArrayList<>();
    
    private List<String> location = new ArrayList<>();
    private List<String> state = new ArrayList<>();    
    private List<String> country = new ArrayList<>();    
    
//    private String commonName;
//    private String organization;
//    private String location;
    
    private String formattedName;
    
    private String formattedCommonName;
    
    private long expirationDate;
    private boolean expired;
    private String fingerPrint;
    
//  private List<String> organizationUnit = new ArrayList<>();
//  private String organizationUnit;

    public int compareTo(Certificate cert) {
        return getFingerPrint().compareTo(cert.getFingerPrint());
    }
    
    public String getFormattedName() {
        return formattedName;
    }

    public void setFormattedName(String formattedName) {
        this.formattedName = formattedName;
    }    
    
    public String getFormattedCommonName() {
        return formattedCommonName;
    }

    public void setFormattedCommonName(String formattedCommonName) {
        this.formattedCommonName = formattedCommonName;
    }

    public long getExpirationDate() {
        return expirationDate;
    }

    public void setExpirationDate(long expirationDate) {
        this.expirationDate = expirationDate;
    }

    public boolean isExpired() {
        return expired;
    }

    public void setExpired(boolean expired) {
        this.expired = expired;
    }

    public String getFingerPrint() {
        return fingerPrint;
    }

    public void setFingerPrint(String fingerPrint) {
        this.fingerPrint = fingerPrint;
    }


    /*    
    public String getCommonName() {
        return commonName;
    }

    public void setCommonName(String commonName) {
        this.commonName = commonName;
    }
*/    
/*    
    public String getOrganization() {
        return organization;
    }
    
    public void setOrganization(String organization) {
        this.organization = organization;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }
*/

    public List<String> getCommonName() {
        return commonName;
    }

    public void setCommonName(List<String> commonName) {
        this.commonName = commonName;
    }
    
    public List<String> getOrganization() {
        return organization;
    }

    public void setOrganization(List<String> organization) {
        this.organization = organization;
    }

    public List<String> getOrganizationUnit() {
        return organizationUnit;
    }

    public void setOrganizationUnit(List<String> organizationUnit) {
        this.organizationUnit = organizationUnit;
    }

    public List<String> getState() {
        return state;
    }

    public void setState(List<String> state) {
        this.state = state;
    }

    public List<String> getLocation() {
        return location;
    }

    public void setLocation(List<String> location) {
        this.location = location;
    }
    
    public List<String> getCountry() {
        return country;
    }

    public void setCountry(List<String> country) {
        this.country = country;
    }
}
