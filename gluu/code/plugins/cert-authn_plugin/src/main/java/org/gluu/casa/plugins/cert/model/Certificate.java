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
    
    private long expirationDate = -1L;
    private boolean expired = false;
    
    private String fingerPrint = null;
    
    private Certificate issuerCertificate = null;
    
//  private List<String> organizationUnit = new ArrayList<>();
//  private String organizationUnit;

    public int compareTo(final Certificate cert) {
        return getFingerPrint().compareTo(cert.getFingerPrint());
    }
    
    public String getFormattedName() {
        return formattedName;
    }

    public void setFormattedName(final String formattedName) {
        this.formattedName = formattedName;
    }    
    
    public String getFormattedCommonName() {
        return formattedCommonName;
    }

    public void setFormattedCommonName(final String formattedCommonName) {
        this.formattedCommonName = formattedCommonName;
    }

    public long getExpirationDate() {
        return expirationDate;
    }

    public void setExpirationDate(final long expirationDate) {
        this.expirationDate = expirationDate;
    }

    public boolean isExpired() {
        return expired;
    }

    public void setExpired(final boolean expired) {
        this.expired = expired;
    }

    public String getFingerPrint() {
        return fingerPrint;
    }

    public void setFingerPrint(final String fingerPrint) {
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

    public void setCommonName(final List<String> commonName) {
        this.commonName = commonName;
    }
    
    public List<String> getOrganization() {
        return organization;
    }

    public void setOrganization(final List<String> organization) {
        this.organization = organization;
    }

    public List<String> getOrganizationUnit() {
        return organizationUnit;
    }

    public void setOrganizationUnit(final List<String> organizationUnit) {
        this.organizationUnit = organizationUnit;
    }

    public List<String> getState() {
        return state;
    }

    public void setState(final List<String> state) {
        this.state = state;
    }

    public List<String> getLocation() {
        return location;
    }

    public void setLocation(final List<String> location) {
        this.location = location;
    }
    
    public List<String> getCountry() {
        return country;
    }

    public void setCountry(final List<String> country) {
        this.country = country;
    }

    public Certificate getIssuerCertificate() {
        return issuerCertificate;
    }

    public void setIssuerCertificate(final Certificate issuerCertificate) {
        this.issuerCertificate = issuerCertificate;
    }

}
