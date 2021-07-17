import json
from functools import reduce
from dict_templates import RULE_TEMPLATE, GROUP_TEMPLATE, DEFAULT_OPTIONS, SIMPLIFIED_OPTIONS
from simplifier import Simplifier
from utilities import copy_update_dict

class LevelCreator(object):
    _json_obj = None
    _file_name = str()
    _level_id = str()
    _source_layer_id = str()
    _output_layer_id = str()
    _next_uid = int()
    _tile_size = 16 # px
    _empty_tile_ids = None # list
    _options = None

    _rule_template = RULE_TEMPLATE
    _group_template = GROUP_TEMPLATE
    _default_options = DEFAULT_OPTIONS

    def __init__(self, file_name, level_id, source_layer_id, output_layer_id, empty_tile_ids, options=None):
        self._file_name = file_name
        self._level_id = level_id
        self._source_layer_id = source_layer_id
        self._output_layer_id = output_layer_id
        self._empty_tile_ids = empty_tile_ids if empty_tile_ids else []
        self._options = self._prepare_options(options)

        self._json_obj = self._get_json(file_name)
        self._next_uid = self._json_obj['nextUid']

    def update_file_with_int_level(self, output_file_path=None):
        file_json_updated = self._replace_int_level_in_json()
        json_as_string = json.dumps(file_json_updated, indent=2, sort_keys=True)
        output_file_name = output_file_path if output_file_path is not None else self._file_name
        with open(output_file_name, 'w') as fp:
            fp.write(json_as_string)

    def get_int_level_updated(self):
        output_layer = self._get_def_layer(self._output_layer_id)
        rules = self._create_rules()
        groups = self._create_groups(rules)
        output_layer_copy = copy_update_dict(output_layer, {
            'autoRuleGroups': groups,
        })
        # TODO: "__tilesetDefUid": 1,
        # TODO: "__tilesetRelPath": "../Platformer Ground.png",
        return output_layer_copy

    def _replace_int_level_in_json(self):
        int_level_updated = self.get_int_level_updated()
        updated_layers = [(int_level_updated if l['identifier'] == self._output_layer_id else l)
            for l in self._json_obj['defs']['layers']]
        updated_defs = copy_update_dict(self._json_obj['defs'], {
            'layers': updated_layers,
        })
        file_json_updated = copy_update_dict(self._json_obj, {
            'nextUid': self._next_uid,
            'defs': updated_defs,
        })
        return file_json_updated

    def _remove_duplicate_rules(self, rules):
        cleaned = []
        for rule in rules:
            found = [r for r in cleaned if r['pattern'] == rule['pattern']]
            if not found:
                cleaned.append(rule)
            else:
                found_rule = found[0]
                new_tile_ids = list(set(found_rule['tileIds'] + rule['tileIds']))
                found_rule['tileIds'] = new_tile_ids
        return cleaned

    def _create_groups(self, rules):
        remaining_rules = [] + rules
        groups = []

        thin_rules = [r for r in remaining_rules if
            (r['pattern'][1] == -1 and r['pattern'][7] == -1) or
            (r['pattern'][3] == -1 and r['pattern'][5] == -1)]
        if len(thin_rules) > 0:
            groups.append(copy_update_dict(self._group_template, {
                'name': 'Thin Tiles',
                'uid': self._get_group_uid(),
                'rules': thin_rules,
            }))
        thin_rules_ids = [r['uid'] for r in thin_rules]
        remaining_rules = [r for r in remaining_rules if r['uid'] not in thin_rules_ids]

        intcorner_rules = [r for r in remaining_rules if
            r['pattern'] in ([-1,0,0,0,1,0,0,0,0], [0,0,-1,0,1,0,0,0,0], [0,0,0,0,1,0,-1,0,0], [0,0,0,0,1,0,0,0,-1])]
        intcorner_rules_ids = [r['uid'] for r in intcorner_rules]
        remaining_rules = [r for r in remaining_rules if r['uid'] not in intcorner_rules_ids]

        inside_rules = [r for r in remaining_rules if r['pattern'] == [0,0,0,0,1,0,0,0,0]]
        inside_rules_ids = [r['uid'] for r in inside_rules]
        remaining_rules = [r for r in remaining_rules if r['uid'] not in inside_rules_ids]

        if len(remaining_rules) > 0:
            groups.append(copy_update_dict(self._group_template, {
                'name': 'Remaining Tiles',
                'uid': self._get_group_uid(),
                'rules': remaining_rules,
            }))

        if len(intcorner_rules) > 0:
            groups.append(copy_update_dict(self._group_template, {
                'name': 'Internal Corner Tiles',
                'uid': self._get_group_uid(),
                'rules': intcorner_rules,
            }))

        if len(inside_rules) > 0:
            groups.append(copy_update_dict(self._group_template, {
                'name': 'Fill Tiles',
                'uid': self._get_group_uid(),
                'rules': inside_rules,
            }))

        return groups

    def _create_rules(self):
        source_layer = self._get_level_layer(self._source_layer_id)
        rules = []
        for grid_tile in source_layer['gridTiles']:
            if grid_tile['t'] in self._empty_tile_ids:
                continue

            pattern = self._get_pattern_for_file(source_layer['gridTiles'], grid_tile['px'])
            rule = copy_update_dict(self._rule_template, {
                'uid': self._get_rule_uid(),
                'tileIds': [grid_tile['t']],
                'pattern': pattern,
            })
            rules.append(rule)
        rules = self._remove_duplicate_rules(rules)
        rules.sort(key=lambda r: self._sort_pattern(r))

        simplifier = Simplifier(
            corners=self._options['simplified_corners'],
            tjoins=self._options['simplified_tjoins'],
            point=self._options['simplified_point'],
            stubs=self._options['simplified_stubs'],
            pjoins=self._options['simplified_pjoins'],
        )
        rules = simplifier.simplify(rules)

        return rules

    def _sort_pattern(self, rule):
        total_sum = sum(rule['pattern'])
        return total_sum

    def _get_pattern_for_file(self, grid_tiles, position):
        pattern = [
            self._tile_is_filled(grid_tiles, [position[0] - self._tile_size, position[1] - self._tile_size]),
            self._tile_is_filled(grid_tiles, [position[0], position[1] - self._tile_size]),
            self._tile_is_filled(grid_tiles, [position[0] + self._tile_size, position[1] - self._tile_size]),

            self._tile_is_filled(grid_tiles, [position[0] - self._tile_size, position[1]]),
            1,
            self._tile_is_filled(grid_tiles, [position[0] + self._tile_size, position[1]]),

            self._tile_is_filled(grid_tiles, [position[0] - self._tile_size, position[1] + self._tile_size]),
            self._tile_is_filled(grid_tiles, [position[0], position[1] + self._tile_size]),
            self._tile_is_filled(grid_tiles, [position[0] + self._tile_size, position[1] + self._tile_size]),
        ]
        return pattern
    
    def _tile_is_filled(self, grid_tiles, position):
        filtered_tile_ids = [t['t'] for t in grid_tiles if t['px'][0] == position[0] and t['px'][1] == position[1]]
        if len(filtered_tile_ids) == 0 or self._list_intersects(filtered_tile_ids, self._empty_tile_ids):
            return -1
        else:
            return 0
    
    def _list_intersects(self, list1, list2):
        found = [i1 for i1 in list1 if i1 in list2]
        return len(found) > 0

    def _get_group_uid(self):
        output_layer = self._get_def_layer(self._output_layer_id)
        if len(output_layer['autoRuleGroups']) > 0:
            return output_layer['autoRuleGroups'][0]['uid']
        group_uid = self._next_uid
        self._next_uid += 1
        return group_uid

    def _get_rule_uid(self):
        output_layer = self._get_def_layer(self._output_layer_id)
        groups = output_layer['autoRuleGroups']
        existing_rule_ids = []
        rule_uid = self._next_uid

        if len(groups) > 0 and len(groups[0]['rules']) > 0:
            existing_rule_ids = [r['uid'] for r in groups[0]['rules']]

        if len(existing_rule_ids):
            while (rule_uid - 1) in existing_rule_ids:
                rule_uid -= 1

        if rule_uid == self._next_uid:
            self._next_uid += 1

        return rule_uid

    def _get_json(self, file_name):
        with open(file_name) as fp:
            json_str = fp.read()
        json_obj = json.loads(json_str)
        return json_obj

    def _get_level(self, json_obj, level_id):
        levels = json_obj['levels']
        filtered = [l for l in levels if l['identifier'] == level_id]
        # TODO: error if len(filtered) != 1
        return filtered[0]

    def _get_level_layer(self, layer_id):
        level_obj = self._get_level(self._json_obj, self._level_id)
        levels = level_obj['layerInstances']
        filtered = [l for l in levels if l['__identifier'] == layer_id]
        # TODO: error if len(filtered) != 1
        return filtered[0]

    def _get_def_layer(self, layer_id):
        layers = self._json_obj['defs']['layers']
        filtered = [l for l in layers if l['identifier'] == layer_id]
        # TODO: error if len(filtered) != 1
        return filtered[0]

    def _prepare_options(self, options):
        prepared_options = copy_update_dict(self._default_options, options or {})
        if prepared_options['simplified']:
            prepared_options = copy_update_dict(prepared_options, SIMPLIFIED_OPTIONS)
        return prepared_options


if __name__ == '__main__':
    creator = LevelCreator('source-auto.ldtk', 'Level_0', 'Tiles', 'IntGrid2', [137], dict(
        simplified=True,
    ))
    creator.update_file_with_int_level()
