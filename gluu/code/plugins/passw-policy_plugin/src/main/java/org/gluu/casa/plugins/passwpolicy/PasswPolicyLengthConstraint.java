/**
 * 
 */
package org.gluu.casa.plugins.passwpolicy;

import org.zkoss.zul.Constraint;
import org.gluu.casa.ui.UIUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.zkoss.zk.ui.Component;
import org.zkoss.zk.ui.WrongValueException;

/**
 * class PasswPolicyLengthConstraint
 *
 * @author Sergey Manoylo
 * @version 2022-11-20
 */
public class PasswPolicyLengthConstraint implements Constraint {
    
    private Logger logger = LoggerFactory.getLogger(PasswPolicyLengthConstraint.class);

    /**
     * 
     */
    public void validate(Component comp, Object value) {
        if (value == null) {
            logger.error("PasswPolicyLengthConstraint: Value == null !");
            UIUtils.showMessageUI(false,"Value == null !");
            throw new WrongValueException(comp, "Value == null !");
        }
        validate((Integer)value);
    }

    /**
     * 
     * @param value
     * @return
     */
    public boolean validate(Integer value) {
        if (((Integer)value).intValue() < 5 || ((Integer)value).intValue() > 50) {
            logger.error("PasswPolicyLengthConstraint: Password length should be >= 5 and <= 50 !");
            UIUtils.showMessageUI(false,"Password length should be >= 5 and <= 50 !");
            return false; 
        }
        else {
            return true;
        }
    }
}
