package org.gluu.casa.plugins.approval.service;

import java.util.Date;
import java.util.List;

import org.gluu.casa.plugins.approval.model.ZTrustPerson;
import org.gluu.casa.service.IPersistenceService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import io.jans.as.common.model.common.User;
import io.jans.orm.search.filter.Filter;

public class UserService {

    @SuppressWarnings("unused")
    private static Logger logger = LoggerFactory.getLogger(UserService.class);
    
    private IPersistenceService persistenceService;

    public UserService() {
        persistenceService = org.gluu.casa.misc.Utils.managedBean(IPersistenceService.class);
    }

    public List<ZTrustPerson> getUsers(String jansStatus, String userStatus) {
        Filter jansStatusFilter = Filter.createEqualityFilter("jansStatus", jansStatus);
        Filter userStatusFilter = Filter.createEqualityFilter("userStatus", userStatus);
        Filter filters = Filter.createANDFilter(jansStatusFilter, userStatusFilter);

        return persistenceService.find(ZTrustPerson.class, persistenceService.getPeopleDn(), filters);
    };

    public boolean updateUser(User user) {
        user.setUpdatedAt(new Date());
        return persistenceService.modify(user);
    }
}
