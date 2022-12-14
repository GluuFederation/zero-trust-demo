package org.gluu.casa.plugins.approval.service;

import java.util.Date;
import java.util.List;

import org.gluu.casa.plugins.approval.model.ZTrustPerson;
import org.gluu.casa.service.IPersistenceService;
import org.gluu.oxauth.model.common.User;
import org.gluu.search.filter.Filter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class UserService {

    private IPersistenceService persistenceService;
    @SuppressWarnings("unused")
    private Logger logger = LoggerFactory.getLogger(UserService.class);

    public UserService() {
        persistenceService = org.gluu.casa.misc.Utils.managedBean(IPersistenceService.class);
    }

    public List<ZTrustPerson> getUsers(String gluuStatus, String userStatus) {

        Filter gluuStatusFilter = Filter.createEqualityFilter("gluuStatus", gluuStatus);
        Filter userStatusFilter = Filter.createEqualityFilter("userStatus", userStatus);
        Filter filters = Filter.createANDFilter(gluuStatusFilter, userStatusFilter);

        return persistenceService.find(ZTrustPerson.class, persistenceService.getPeopleDn(), filters);

    };

    public boolean updateUser(User user) {
        user.setUpdatedAt(new Date());
        return persistenceService.modify(user);
    }
}
