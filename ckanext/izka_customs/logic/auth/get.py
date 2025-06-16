# -*- coding: utf-8 -*-
from ckan.logic.auth import get as auth_get_core

def group_list_for_user(context, data_dict):
    return auth_get_core.organization_list_for_user(context, data_dict)