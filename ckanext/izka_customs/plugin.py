import ckan.plugins as p
from ckanext.izka_customs.logic.action import get as action_get
from ckanext.izka_customs.logic.auth import get as auth_get

class IzkaCustomsPlugin(p.SingletonPlugin):
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)

    def get_actions(self):
        return {
            'group_list_for_user': action_get.group_list_for_user,
        }

    def get_auth_functions(self):
        return {
            'group_list_for_user': auth_get.group_list_for_user,
        }