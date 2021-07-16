import json

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

    _rule_template = {
        "uid": 'XXX', # XXX
        "active": True,
        "size": 3,
        "tileIds": [71], # XXX
        "chance": 1,
        "breakOnMatch": True,
        "pattern": [], # [0,-1,0,-1,1,-1,0,-1,0],
        "flipX": False, # XXX
        "flipY": False, # XXX
        "xModulo": 1,
        "yModulo": 1,
        "checker": "None",
        "tileMode": "Single",
        "pivotX": 0,
        "pivotY": 0,
        "outOfBoundsValue": None,
        "perlinActive": False,
        "perlinSeed": 6841713, # XXX
        "perlinScale": 0.2,
        "perlinOctaves": 2
    }
    _group_template = {
        "uid": 'XXX', # XXX
        "name": "New group", # XXX
        "active": True, 
        "collapsed": False, 
        "isOptional": False, 
        "rules": [] # XXX
    }
    _default_options = {
        'friendly_corners': False,
        'friendly_tjoins': False,
        'friendly_point': False,
    }

    def __init__(self, file_name, level_id, source_layer_id, output_layer_id, empty_tile_ids, options=None):
        self._file_name = file_name
        self._level_id = level_id
        self._source_layer_id = source_layer_id
        self._output_layer_id = output_layer_id
        self._empty_tile_ids = empty_tile_ids if empty_tile_ids else []
        self._options = self._copy_update_dict(self._default_options, options or {})

        self._json_obj = self._get_json(file_name)
        self._next_uid = self._json_obj['nextUid']

    def update_file_with_int_level(self, output_file_path=None):
        file_json_updated = self._replace_int_level_in_json()
        json_as_string = json.dumps(file_json_updated, indent=2, sort_keys=True)
        output_file_name = output_file_path if output_file_path is not None else self._file_name
        with open(output_file_name, 'w') as fp:
            fp.write(json_as_string)

    def _replace_int_level_in_json(self):
        int_level_updated = self.get_int_level_updated()
        updated_layers = [(int_level_updated if l['identifier'] == self._output_layer_id else l)
            for l in self._json_obj['defs']['layers']]
        updated_defs = self._copy_update_dict(self._json_obj['defs'], {
            'layers': updated_layers,
        })
        file_json_updated = self._copy_update_dict(self._json_obj, {
            'nextUid': self._next_uid,
            'defs': updated_defs,
        })
        return file_json_updated

    def get_int_level_updated(self):
        output_layer = self._get_def_layer(self._output_layer_id)
        rules = self._create_rules()
        groups = self._create_groups(rules)
        output_layer_copy = self._copy_update_dict(output_layer, {
            'autoRuleGroups': groups,
        })
        # TODO: "__tilesetDefUid": 1,
        # TODO: "__tilesetRelPath": "../Platformer Ground.png",
        return output_layer_copy

    def _remove_duplicate_rules(self, rules):
        cleaned = []
        for rule in rules:
            pattern_as_string = str(rule['pattern'])
            contains = bool([r for r in cleaned if str(r['pattern']) == pattern_as_string])
            if not contains:
                cleaned.append(rule)
        return cleaned

    def _create_groups(self, rules):
        remaining_rules = [] + rules
        groups = []

        thin_rules = [r for r in remaining_rules if
            (r['pattern'][1] == -1 and r['pattern'][7] == -1) or
            (r['pattern'][3] == -1 and r['pattern'][5] == -1)]
        if len(thin_rules) > 0:
            groups.append(self._copy_update_dict(self._group_template, {
                'name': 'Thin tiles',
                'uid': self._get_group_uid(),
                'rules': thin_rules,
            }))
        thin_rules_ids = [r['uid'] for r in thin_rules]
        remaining_rules = [r for r in remaining_rules if r['uid'] not in thin_rules_ids]
        # print(1111, thin_rules_ids) # XXX
        # print(1112, [r['uid'] for r in remaining_rules]) # XXX

        if len(remaining_rules) > 0:
            groups.append(self._copy_update_dict(self._group_template, {
                'name': 'Remaining tiles',
                'uid': self._get_group_uid(),
                'rules': remaining_rules,
            }))
        print(1111, len(thin_rules), len(remaining_rules)) # XXX

        return groups

    def _create_rules(self):
        source_layer = self._get_level_layer(self._source_layer_id)
        rules = []
        for grid_tile in source_layer['gridTiles']:
            if grid_tile['t'] in self._empty_tile_ids:
                continue

            pattern = self._get_pattern_for_file(source_layer['gridTiles'], grid_tile['px'])
            rule = self._copy_update_dict(self._rule_template, {
                'uid': self._get_rule_uid(),
                'tileIds': [grid_tile['t']],
                'pattern': pattern,
            })
            rules.append(rule)
        rules = self._remove_duplicate_rules(rules)
        rules.sort(key=lambda r: self._sort_pattern(r))
        if self._options['friendly_corners']:
            rules = [self._copy_update_dict(r, {'pattern': self._pattern_with_friendly_corners(r['pattern'])}) for r in rules]
        if self._options['friendly_tjoins']:
            rules = [self._copy_update_dict(r, {'pattern': self._pattern_with_friendly_tjoins(r['pattern'])}) for r in rules]
        if self._options['friendly_point']:
            rules = [self._copy_update_dict(r, {'pattern': self._pattern_with_friendly_point(r['pattern'])}) for r in rules]
        return rules

    def _pattern_with_friendly_corners(self, pattern):
        if pattern == [-1,-1,-1,-1,1,0,-1,0,-1]:
            return [-1,-1,0,-1,1,0,0,0,-1]
        elif pattern == [-1,-1,-1,0,1,-1,-1,0,-1]:
            return [0,-1,-1,0,1,-1,-1,0,0]
        elif pattern == [-1,0,-1,-1,1,0,-1,-1,-1]:
            return [0,0,-1,-1,1,0,-1,-1,0]
        elif pattern == [-1,0,-1,0,1,-1,-1,-1,-1]:
            return [-1,0,0,0,1,-1,0,-1,-1]
        return pattern

    def _pattern_with_friendly_tjoins(self, pattern):
        if pattern == [-1,-1,-1,0,1,0,-1,0,-1]:
            return [0,-1,0,0,1,0,-1,0,-1]
        elif pattern == [-1,0,-1,0,1,0,-1,-1,-1]:
            return [-1,0,-1,0,1,0,0,-1,0]
        elif pattern == [-1,0,-1,-1,1,0,-1,0,-1]:
            return [0,0,-1,-1,1,0,0,0,-1]
        elif pattern == [-1,0,-1,0,1,-1,-1,0,-1]:
            return [-1,0,0,0,1,-1,-1,0,0]
        return pattern

    def _pattern_with_friendly_point(self, pattern):
        if pattern == [-1,-1,-1,-1,1,-1,-1,-1,-1]:
            return [0,-1,0,-1,1,-1,0,-1,0]
        return pattern

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

    def _copy_update_dict(self, d1, d2):
        the_copy = d1.copy()
        the_copy.update(d2)
        return the_copy

if __name__ == '__main__':
    creator = LevelCreator('source-auto.ldtk', 'Level_0', 'Tiles', 'IntGrid2', [137], dict(
        friendly_corners=True,
        friendly_tjoins=True,
        friendly_point=True,
    ))
    # creator.get_int_level_updated()
    creator.update_file_with_int_level()
