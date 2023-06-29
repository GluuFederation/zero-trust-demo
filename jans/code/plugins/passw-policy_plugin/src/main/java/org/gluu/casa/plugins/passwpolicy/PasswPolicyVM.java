package org.gluu.casa.plugins.passwpolicy;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.zkoss.bind.annotation.BindingParam;
import org.zkoss.bind.annotation.Command;
import org.zkoss.bind.annotation.Init;
import org.zkoss.bind.annotation.NotifyChange;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.jans.util.Util;

import java.io.File;
import java.util.Map;

import org.gluu.casa.ui.UIUtils;

/**
 * 
 * 
 * @author Sergey Manoylo
 * @version 2022-11-13
 */
public class PasswPolicyVM {

    private static Logger logger = LoggerFactory.getLogger(PasswPolicyVM.class);

    public static final String DEF_REGEX_PROPS_FPATH = "/etc/jans/conf/ztrust-regex.json";
    public static final String DEF_PASS_REGEX = "pass_regex";
    
    private ObjectMapper mapper = new ObjectMapper();

    private Map<String, String> properties;

    private String currPassRegEx;   // current Password Regular Expression
                                    // 'save', 'reload' - synchronizing with 

    private String genPassRegEx;    // generated Password Regular Expression

    // values, used by RegEx generator 
    private boolean isUpperCase = true;

    private boolean isLowerCase = true;

    private boolean isDigits = true;

    private boolean isSpecSymbols = true;

    private boolean isMinus = true;

    private boolean isUnderline = true;

    private boolean isSymbols = true;

    private boolean isBrackets = true;

    private int passwLength = 15;

    @Init
    @NotifyChange("currPassRegEx")
    public void init() {
        try {
            currPassRegEx = getPropertyValue(DEF_PASS_REGEX);
        } catch (Exception e) {
            logger.error(String.format("Failed to load '%s' configuration file", DEF_REGEX_PROPS_FPATH));
            logger.error(e.getMessage(), e);
        }
    }
    
    public String getPropertyValue(final String key) {
        String resValue = ""; 
        try {
            properties = mapper.readValue(new File(DEF_REGEX_PROPS_FPATH), Map.class);
            if (properties.containsKey(key)) {
                resValue = properties.get(key);
            }
        } catch (Exception e) {
            logger.error(String.format("Failed to get property: key = '%s'", key));
            logger.error(e.getMessage(), e);
        }        
        return resValue;
    }

    public void setPropertyValue(final String key, final String value) {
        try {
            if (properties.containsKey(key)) {
                properties.replace(key, value);
            }
            else {
                properties.put(key, value);
            }
            mapper.writeValue(new File(DEF_REGEX_PROPS_FPATH), properties);
        } catch (Exception e) {
            logger.error(String.format("Failed to save '%s' configuration file", DEF_REGEX_PROPS_FPATH));
            logger.error(e.getMessage(), e);
        }
    }

    public String getRegexPropsFPath() {
        return DEF_REGEX_PROPS_FPATH;
    }

    public String getCurrPassRegEx() {
        return this.currPassRegEx;
    }

    public void setCurrPassRegEx(final String currPassRegEx) {
        this.currPassRegEx = currPassRegEx;
    }

    public String getGenPassRegEx() {
        return this.genPassRegEx;
    }

    public void setGenPassRegEx(final String genPassRegEx) {
        this.genPassRegEx = genPassRegEx;
    }
    
    public boolean getIsUpperCase() {
        return this.isUpperCase;
    }

    public void setIsUpperCase(final boolean isUpperCase) {
        this.isUpperCase = isUpperCase;
    }

    public boolean getIsLowerCase() {
        return this.isLowerCase;
    }

    public void setIsLowerCase(final boolean isLowerCase) {
        this.isLowerCase = isLowerCase;
    }
    
    public boolean getIsDigits() {
        return this.isDigits;
    }    

    public void setIsDigits(final boolean isDigits) {
        this.isDigits = isDigits;
    }

    public boolean getIsSpecSymbols() {
        logger.debug(String.format("getIsSpecSymbols(): isSpecSymbols = %b", isSpecSymbols));
        return this.isSpecSymbols;
    }

    public void setIsSpecSymbols(final boolean isSpecSymbols) {
        this.isSpecSymbols = isSpecSymbols;
        logger.debug(String.format("setIsSpecSymbols(): isSpecSymbols = %b", isSpecSymbols));
    }

    public boolean getIsMinus() {
        logger.debug(String.format("getIsMinus(): isMinus = %b", isMinus));
        return this.isMinus;
    }

    public void setIsMinus(final boolean isMinus) {
        this.isMinus = isMinus;
        logger.debug(String.format("setIsMinus(): isMinus = %b", isMinus));
    }

    public boolean getIsUnderline() {
        logger.debug(String.format("getIsUnderline(): isUnderline = %b", isUnderline));
        return this.isUnderline;
    }

    public void setIsUnderline(final boolean isUnderline) {
        logger.debug(String.format("setIsUnderline(): isUnderline = %b", isUnderline));
        this.isUnderline = isUnderline;
    }

    public boolean getIsSymbols() {
        logger.debug(String.format("getIsSymbols(): isSymbols = %b", isSymbols));
        return this.isSymbols;
    }

    public void setIsSymbols(final boolean isSymbols) {
        this.isSymbols = isSymbols;
        logger.debug(String.format("setIsSymbols(): isSymbols = %b", isSymbols));
    }

    public boolean getIsBrackets() {
        logger.debug(String.format("getIsBrackets(): isBrackets = %b", isBrackets));
        return this.isBrackets;
    }

    public void setIsBrackets(final boolean isBrackets) {
        logger.debug(String.format("setIsBrackets(): isBrackets = %b", isBrackets));
        this.isBrackets = isBrackets;
    }

    public int getPasswLength() {
        logger.debug(String.format("getPasswLength(): passwLength = %b", passwLength));
        return this.passwLength;
    }

    public void setPasswLength(final int passwLength) {
        logger.debug(String.format("setPasswLength(): passwLength = %b", passwLength));
        this.passwLength = passwLength;
    }

    @Command
    public void save(@BindingParam("passRegEx") String passRegEx) {
        if (Util.empty(passRegEx)) {
            setPropertyValue(DEF_PASS_REGEX, currPassRegEx);
        }
        else {
            setPropertyValue(DEF_PASS_REGEX, passRegEx);
        }
    }

    @Command
    @NotifyChange("currPassRegEx")
    public void reload() {
        try {
            currPassRegEx = getPropertyValue(DEF_PASS_REGEX);
        } catch (Exception e) {
            logger.error(String.format("Failed to save '%s' configuration file", DEF_REGEX_PROPS_FPATH));
            logger.error(e.getMessage(), e);
        }
    }

    @Command
    @NotifyChange("genPassRegEx")
    public void generate() {
        PasswPolicyLengthConstraint constraint = new PasswPolicyLengthConstraint();
        if (!constraint.validate(passwLength)) {
            this.genPassRegEx = "";
        }
        else {

            String genRegEx = "";

            if (isUpperCase || isLowerCase || isDigits || isMinus || isUnderline || isSymbols || isBrackets) {
                genRegEx += "^";
            }
            if (isUpperCase) {
                genRegEx += "(?=.*[A-Z])";
            }
            if (isLowerCase) {
                genRegEx += "(?=.*[a-z])";
            }
            if (isDigits) {
                genRegEx += "(?=.*\\d)";
            }

            String symbols = "";

            if (isSpecSymbols) {
                if (isMinus) {
                    symbols += "\\-";
                }
                if (isUnderline) {
                    symbols += "\\_";
                }
                if (isBrackets) {
                    symbols += "\\(\\)\\{\\}\\[\\]\\<\\>";
                }
                if (isSymbols) {
                    symbols += "~\\`!@#$%^&*+=|\\/:;\\\\\"\\',.?";
                }

                if (!symbols.isEmpty()) {
                    genRegEx += "(?=.*[";
                    genRegEx += symbols;
                    genRegEx += "])";
                }
            }

            if (isUpperCase || isLowerCase || isDigits || isMinus || isUnderline || isSymbols || isBrackets) {
                genRegEx += "[";
                if (isUpperCase) {
                    genRegEx += "A-Z";
                }
                if (isLowerCase) {
                    genRegEx += "a-z";
                }
                if (isDigits) {
                    genRegEx += "\\d";
                }
                genRegEx += symbols;
                genRegEx += "]";
            }

            if (isUpperCase || isLowerCase || isDigits || isMinus || isUnderline || isSymbols || isBrackets) {
                genRegEx += String.format("{%d,}$", passwLength);
            }

            this.genPassRegEx = genRegEx;
            UIUtils.showMessageUI(true);
        }
    }

    @Command
    @NotifyChange("currPassRegEx")
    public void copy() {
        if (!Util.empty(this.genPassRegEx)) {
            this.currPassRegEx = this.genPassRegEx;
        }
    }
}
