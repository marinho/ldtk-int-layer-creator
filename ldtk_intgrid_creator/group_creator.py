from .dict_templates import GROUP_TEMPLATE
from .utilities import copy_update_dict


class GroupCreator(object):
    _group_template = GROUP_TEMPLATE
    _get_next_uid = lambda: None

    def __init__(self, get_next_uid_function):
        self._get_next_uid = get_next_uid_function

    def create(self, rules):
        remaining_rules = [] + rules
        top_groups = []
        bottom_groups = []

        thin_rules_group = self._thin_rules_group(remaining_rules)
        if thin_rules_group:
            top_groups.append(thin_rules_group)
            remaining_rules = self._get_remaining_rules(remaining_rules, thin_rules_group['rules'])

        intcorner_rules_group = self._intcorner_rules_group(remaining_rules)
        if intcorner_rules_group:
            bottom_groups.append(intcorner_rules_group)
            remaining_rules = self._get_remaining_rules(remaining_rules, intcorner_rules_group['rules'])

        inside_rules_group = self._inside_rules_group(remaining_rules)
        if inside_rules_group:
            bottom_groups.append(inside_rules_group)
            remaining_rules = self._get_remaining_rules(remaining_rules, inside_rules_group['rules'])

        if len(remaining_rules) > 0:
            remaining_rules_group = self._remaining_rules_group(remaining_rules)
            top_groups.append(remaining_rules_group)

        return top_groups + bottom_groups

    def _thin_rules_group(self, remaining_rules):
        thin_rules = [r for r in remaining_rules if
            (r['pattern'][1] == -1 and r['pattern'][7] == -1) or
            (r['pattern'][3] == -1 and r['pattern'][5] == -1)]
        if len(thin_rules) == 0:
            return None

        group = copy_update_dict(self._group_template, {
            'name': 'Thin Tiles',
            'uid': self._get_next_uid(),
            'rules': thin_rules,
        })
        return group

    def _intcorner_rules_group(self, remaining_rules):
        patterns = ([-1,0,0,0,1,0,0,0,0], [0,0,-1,0,1,0,0,0,0], [0,0,0,0,1,0,-1,0,0], [0,0,0,0,1,0,0,0,-1])
        intcorner_rules = [r for r in remaining_rules if r['pattern'] in patterns]
        if len(intcorner_rules) == 0:
            return None

        group = copy_update_dict(self._group_template, {
            'name': 'Internal Corner Tiles',
            'uid': self._get_next_uid(),
            'rules': intcorner_rules,
        })
        return group

    def _inside_rules_group(self, remaining_rules):
        inside_rules = [r for r in remaining_rules if r['pattern'] == [0,0,0,0,1,0,0,0,0]]
        if len(inside_rules) == 0:
            return None

        group = copy_update_dict(self._group_template, {
            'name': 'Fill Tiles',
            'uid': self._get_next_uid(),
            'rules': inside_rules,
        })
        return group

    def _remaining_rules_group(self, remaining_rules):
        group = copy_update_dict(self._group_template, {
            'name': 'Remaining Tiles',
            'uid': self._get_next_uid(),
            'rules': remaining_rules,
        })
        return group

    def _get_remaining_rules(self, remaining_rules, new_rules):
        new_rules_ids = [r['uid'] for r in new_rules]
        remaining_rules = [r for r in remaining_rules if r['uid'] not in new_rules_ids]
        return remaining_rules
