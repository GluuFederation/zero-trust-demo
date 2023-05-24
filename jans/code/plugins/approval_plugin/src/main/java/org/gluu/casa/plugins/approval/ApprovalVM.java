package org.gluu.casa.plugins.approval;

import java.util.ArrayList;
import java.util.List;

import org.gluu.casa.misc.Utils;
import org.gluu.casa.plugins.approval.model.ZTrustPerson;
import org.gluu.casa.plugins.approval.service.UserService;

import org.gluu.casa.service.IPersistenceService;
import org.gluu.casa.ui.UIUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.zkoss.bind.BindUtils;
import org.zkoss.bind.annotation.BindingParam;
import org.zkoss.bind.annotation.Command;
import org.zkoss.bind.annotation.Init;
import org.zkoss.bind.annotation.NotifyChange;

/**
 * A ZK
 * <a href="http://books.zkoss.org/zk-mvvm-book/8.0/viewmodel/index.html" target
 * ="_blank">ViewModel</a> that acts as the "controller" of page
 * <code>index.zul</code> in this sample plugin. See <code>viewModel</code>
 * attribute of panel component of <code>index.zul</code>.
 * 
 * @author jgomer
 */
public class ApprovalVM {

    private static final int DEF_IDX_INACTIVE_USERS = 0;
    private static final int DEF_IDX_PENDING_USERS = 1;
    private static final int DEF_IDX_ACTIVE_USERS = 2;

    private Logger logger = LoggerFactory.getLogger(getClass());
    private IPersistenceService persistenceService;

    private List<ZTrustPerson> users;
    private UserService us;
    private List<ZTrustPerson> pickedUsers;
    private String keyword;

    private String[] userTypes = { "Inactive Users", "Pending Users", "Active Users" };

    private List<ZTrustPerson> inactiveUsers;
    private List<ZTrustPerson> pendingUsers;
    private List<ZTrustPerson> activeUsers;

    private int currentSelectedUserTypeIndex;

    /**
     * Initialization method for this ViewModel.
     */
    public void setCurrentSelectedUserTypeIndex(int currentSelectedUserTypeIndex) {
        this.currentSelectedUserTypeIndex = currentSelectedUserTypeIndex;
    }

    public List<ZTrustPerson> getUsers() {
        return users;
    }

    public String[] getUserTypes() {
        return userTypes;
    }

    public String getKeyword() {
        return keyword;
    }

    public void setKeyword(String keyword) {
        this.keyword = keyword;
    }

    public int getCurrentSelectedUserTypeIndex() {
        return currentSelectedUserTypeIndex;
    }

    public String getCurrentSelectedUserType() {
        return userTypes[getCurrentSelectedUserTypeIndex()];
    }

    @Init
    @NotifyChange("users")
    public void init() {
        persistenceService = Utils.managedBean(IPersistenceService.class);
//        persistenceService.initialize();        
        setCurrentSelectedUserTypeIndex(DEF_IDX_ACTIVE_USERS);
        us = new UserService();
        activeUsers = us.getUsers("active", "active");
        users = activeUsers;
        pickedUsers = new ArrayList<ZTrustPerson>();
        logger.info("Approval ViewModel inited");
    }

    @NotifyChange("users")
    @Command
    public void activate(@BindingParam("user") ZTrustPerson user) {
        try {
            user.setUserStatus("active");
            user.setStatus("active");

            boolean res = persistenceService.modify(user);
            if (res) {
                logger.info("User " + user.getFormattedName() + "is activated");
                users.remove(user);

                BindUtils.postNotifyChange(null, null, this, "users");
                UIUtils.showMessageUI(true);
            }
            else {
                logger.info("User " + user.getFormattedName() + "isn't activated");
                UIUtils.showMessageUI(false);                   
            }
        } catch (Exception e) {
            UIUtils.showMessageUI(false);
        }
    }
    
    @NotifyChange("users")
    @Command
    public void deactivate(@BindingParam("user") ZTrustPerson user) {
        try {
            user.setUserStatus("inactive");
            user.setStatus("inactive");

            boolean res = persistenceService.modify(user);
            if (res) {
                logger.info("User " + user.getFormattedName() + "is deactivated");
                users.remove(user);

                BindUtils.postNotifyChange(null, null, this, "users");
                UIUtils.showMessageUI(true);
            }
            else {
                logger.info("User " + user.getFormattedName() + "isn't deactivated");
                UIUtils.showMessageUI(false);                   
            }
        } catch (Exception e) {
            UIUtils.showMessageUI(false);
        }
    }
    
    @NotifyChange("users")
    @Command
    public void delete(@BindingParam("user") ZTrustPerson user) {
        try {
            boolean res = persistenceService.delete(user);
            if (res) {
                logger.info("User " + user.getFormattedName() + "is removed");
                users.remove(user);
                BindUtils.postNotifyChange(null, null, this, "users");
                UIUtils.showMessageUI(true);
            }
            else {
                logger.info("User " + user.getFormattedName() + "isn't removed");
                UIUtils.showMessageUI(false);                
            }
        } catch (Exception e) {
            UIUtils.showMessageUI(false);
        }
    }    

    @NotifyChange("users")
    @Command
    public void deleteSelected() {
        try {
            for (ZTrustPerson user : pickedUsers) {
                persistenceService.delete(user);
                logger.info("User " + user.getFormattedName() + " is deleted");
                users.remove(user);
            }
            BindUtils.postNotifyChange(null, null, this, "users");
            UIUtils.showMessageUI(true);
        } catch (Exception e) {
            UIUtils.showMessageUI(false);
        }
    }

    @NotifyChange("users")
    @Command
    public void activateSelected() {
        try {
            for (ZTrustPerson user : pickedUsers) {
                user.setStatus("active");
                user.setUserStatus("active");
                persistenceService.modify(user);
                logger.info("User " + user.getFormattedName() + " is activated");
                users.remove(user);
            }
            BindUtils.postNotifyChange(null, null, this, "users");
            UIUtils.showMessageUI(true);

        } catch (Exception e) {
            UIUtils.showMessageUI(false);
        }
    }

    @NotifyChange("users")
    @Command
    public void deactivateSelected() {
        try {
            for (ZTrustPerson user : pickedUsers) {
                user.setStatus("inactive");
                user.setUserStatus("inactive");
                persistenceService.modify(user);
                logger.info("User " + user.getFormattedName() + " is deactivated");
                users.remove(user);
            }
            BindUtils.postNotifyChange(null, null, this, "users");
            UIUtils.showMessageUI(true);

        } catch (Exception e) {
            UIUtils.showMessageUI(false);
        }
    }

    @Command
    public void pick(@BindingParam("checked") boolean isPicked, @BindingParam("picked") ZTrustPerson user) {
        if (isPicked) {
            logger.info("Adding User:" + user.getGivenName().toString() + " to picked list");
            pickedUsers.add(user);
        } else {
            logger.info("Removing User:" + user.getGivenName().toString() + " from the picked list");
            pickedUsers.remove(user);
        }
    }

    @Command
    public void onSelectAll(@BindingParam("checked") boolean isChecked) {
        if (isChecked) {
            final int currSelIdx = getCurrentSelectedUserTypeIndex();

            if (currSelIdx == DEF_IDX_INACTIVE_USERS) {
                pickedUsers.clear();
                pickedUsers = inactiveUsers;
            } else if (currSelIdx == DEF_IDX_PENDING_USERS) {
                pickedUsers.clear();
                pickedUsers = pendingUsers;
            } else if (currSelIdx == DEF_IDX_ACTIVE_USERS) {
                pickedUsers.clear();
                pickedUsers = activeUsers;
            }

        } else {
            pickedUsers.clear();
        }
    }

    @NotifyChange({ "users", "currentSelectedUserType" })
    @Command
    public void selectUserType(@BindingParam("userType") int userTypeIndex) {
        setCurrentSelectedUserTypeIndex(userTypeIndex);
        logger.info("Selected usertype:" + userTypes[userTypeIndex]);
        pickedUsers.clear();

        if (userTypeIndex == DEF_IDX_INACTIVE_USERS) {
            inactiveUsers = us.getUsers("inactive", "inactive");
            users = inactiveUsers;
            BindUtils.postNotifyChange(null, null, this, "users");
        } else if (userTypeIndex == DEF_IDX_PENDING_USERS) {
            pendingUsers = us.getUsers("inactive", "pending");
            users = pendingUsers;
            BindUtils.postNotifyChange(null, null, this, "users");
        } else if (userTypeIndex == DEF_IDX_ACTIVE_USERS) {
            activeUsers = us.getUsers("active", "active");
            users = activeUsers;
            BindUtils.postNotifyChange(null, null, this, "users");
        }
    }

    @NotifyChange("users")
    @Command
    public void search() {
        try {
            List<ZTrustPerson> searchResult = new ArrayList<>();
            final int currSelIdx = getCurrentSelectedUserTypeIndex();
            if (currSelIdx == DEF_IDX_INACTIVE_USERS) {
                searchResult.clear();
                for (ZTrustPerson user : inactiveUsers) {
                    logger.info("Inactive User: " + user.getFormattedName());
                    if (user.getKeywords().contains(keyword.toLowerCase())) {
                        searchResult.add(user);
                    }
                }
            } else if (currSelIdx == DEF_IDX_PENDING_USERS) {
                searchResult.clear();
                for (ZTrustPerson user : pendingUsers) {
                    logger.info("Pending User: " + user.getFormattedName());
                    if (user.getKeywords().contains(keyword.toLowerCase())) {
                        searchResult.add(user);
                    }
                }
            } else if (currSelIdx == DEF_IDX_ACTIVE_USERS) {
                searchResult.clear();
                for (ZTrustPerson user : activeUsers) {
                    logger.info("Active User: " + user.getFormattedName());
                    if (user.getKeywords().contains(keyword.toLowerCase())) {
                        searchResult.add(user);
                    }
                }
            }

            if (searchResult.size() > 0) {
                users = searchResult;
                BindUtils.postNotifyChange(null, null, this, "users");
            } else {
                users.clear();
                UIUtils.showMessageUI(false, "No users found!");
                BindUtils.postNotifyChange(null, null, this, "users");
            }

        } catch (Exception e) {
            UIUtils.showMessageUI(false, "Unrecognized Search Query!");
        }
    }
}
