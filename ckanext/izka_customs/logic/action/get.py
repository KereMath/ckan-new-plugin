# -*- coding: utf-8 -*-
from ckan.logic import NotFound
from ckan.logic.action.get import _check_access
import ckan.authz as authz
from ckan.logic import side_effect_free
from ckan.lib.dictization import model_dictize
from ckan.lib.plugins import toolkit
asbool = toolkit.asbool

@side_effect_free
def group_list_for_user(context, data_dict):
    '''Return the groups that the user has a given permission for.
    MODIFIED to include user capacity in the response.
    '''
    model = context['model']

    if data_dict.get('id'):
        user_obj = model.User.get(data_dict['id'])
        if not user_obj:
            raise NotFound
        user = user_obj.name
    else:
        user = context['user']

    _check_access('group_list_for_user', context, data_dict)
    sysadmin = authz.is_sysadmin(user)

    groups_q = model.Session.query(model.Group) \
        .filter(model.Group.is_organization == False) \
        .filter(model.Group.state == 'active')

    if sysadmin:
        groups_and_capacities = [(group, 'admin') for group in groups_q.all()]
    else:
        permission = data_dict.get('permission', 'read')
        roles = authz.get_roles_with_permission(permission)

        if not roles:
            return []

        user_id = authz.get_user_id_for_username(user, allow_none=True)
        if not user_id:
            return []

        # --- DÜZELTİLMİŞ SORGU ---
        q = model.Session.query(model.Member, model.Group) \
            .filter(model.Member.group_id == model.Group.id) \
            .filter(model.Member.table_name == 'user') \
            .filter(model.Member.capacity.in_(roles)) \
            .filter(model.Member.table_id == user_id) \
            .filter(model.Member.state == 'active') \
            .filter(model.Group.is_organization == False)
        # --- DÜZELTİLMİŞ SORGUNUN SONU ---

        group_ids_to_capacities = {member.group_id: member.capacity for member, group in q.all()}
        group_ids = group_ids_to_capacities.keys()

        if not group_ids:
            return []

        groups_q = groups_q.filter(model.Group.id.in_(group_ids))
        groups_and_capacities = [
            (group, group_ids_to_capacities.get(group.id, 'member'))
            for group in groups_q.all()
        ]

    context['with_capacity'] = True
    groups_list = model_dictize.group_list_dictize(
        groups_and_capacities,
        context,
        with_package_counts=asbool(data_dict.get('include_dataset_count', False))
    )

    return groups_list