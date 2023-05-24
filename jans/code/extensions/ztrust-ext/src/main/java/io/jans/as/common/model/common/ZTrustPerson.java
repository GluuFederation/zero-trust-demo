/**
 * 
 */
package io.jans.as.common.model.common;

import io.jans.orm.annotation.DataEntry;
import io.jans.orm.annotation.ObjectClass;

/**
syntaxType = {
                '1.3.6.1.4.1.1466.115.121.1.7': 'boolean',
                '1.3.6.1.4.1.1466.115.121.1.27': 'integer',
                '1.3.6.1.4.1.1466.115.121.1.24': 'datetime',
              }
          
The LDAPSyntaxes 1.3.6.1.4.1.1466.115.121.1.15 is named Directory String
    1.3.6.1.4.1.1466.115.121.1.15 is a Case-insensitive UTF-8 (Unicode) String

We have seen this also named as caseIgnoreString and Directory (Case Ignore) String     
     
The 1.3.6.1.4.1.1466.115.121.1.24 LDAPSyntaxes is defined as:
    OID of 1.3.6.1.4.1.1466.115.121.1.24
    NAME: GeneralizedTime
    DESC:
    X-NDS_SYNTAX: 24         
     
*/

/**
 * @author Sergey Manoylo
 * @version Sept 8, 2022
 */
@DataEntry
@ObjectClass(value = "ztrustPerson")
public class ZTrustPerson extends User {

    /**
     * 
     */
    private static final long serialVersionUID = 9100931112511064126L;

}
