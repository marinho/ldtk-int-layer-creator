import json
from functools import reduce
from .dict_templates import LAYER_TEMPLATE, GROUP_TEMPLATE, RULE_TEMPLATE, DEFAULT_OPTIONS, SIMPLIFIED_OPTIONS
from .simplifier import Simplifier
from .utilities import copy_update_dict
from .group_creator import GroupCreator
from .rule_creator import RuleCreator

class LevelCreator(object):
    _json_obj = None
    _file_name = str()
    _source_level_id = str()
    _source_layer_id = str()
    _output_layer_id = str()
    _next_uid = int() # TODO: optimize to decrease this value ignoring items that are being replaced
    _tile_size = int() # px
    _empty_tile_ids = None # list
    _options = None

    _layer_template = LAYER_TEMPLATE
    # _rule_template = RULE_TEMPLATE
    _default_options = DEFAULT_OPTIONS

    _simplifier = None # Simplifier()
    _group_creator = None # GroupCreator
    _rule_creator = None # RuleCreator

    def __init__(self, file_name, source_level_id, source_layer_id, output_layer_id, empty_tile_ids, tile_size=16, options=None):
        self._file_name = file_name
        self._source_level_id = source_level_id
        self._source_layer_id = source_layer_id
        self._output_layer_id = output_layer_id
        self._empty_tile_ids = empty_tile_ids if empty_tile_ids else []
        self._tile_size = tile_size
        self._options = self._prepare_options(options)

        self._json_obj = self._get_json(file_name)
        self._next_uid = self._json_obj['nextUid']
        self._create_simplifier()
        self._group_creator = GroupCreator(lambda: self._get_next_uid())
        self._rule_creator = RuleCreator(lambda: self._get_next_uid(), self._simplifier, empty_tile_ids, tile_size)

    def update_file_with_int_level(self, output_file_path=None):
        file_json_updated = self._replace_output_layer_in_json()
        json_as_string = json.dumps(file_json_updated, indent=2, sort_keys=True)
        output_file_name = output_file_path if output_file_path is not None else self._file_name
        with open(output_file_name, 'w') as fp:
            fp.write(json_as_string)

    def get_output_layer_updated(self):
        rules = self._create_rules()
        groups = self._group_creator.create(rules)
        output_layer = self._get_def_layer(self._output_layer_id)
        output_layer['autoRuleGroups'] = groups
        # TODO: "__tilesetDefUid": 1,
        # TODO: "__tilesetRelPath": "../Platformer Ground.png",
        return output_layer

    def _replace_output_layer_in_json(self):
        output_layer = self.get_output_layer_updated()
        updated_defs = copy_update_dict(self._json_obj['defs'], {})

        layer_exists = [layer for layer in updated_defs['layers'] if layer['identifier'] == self._output_layer_id]

        if layer_exists:
            updated_defs['layers'] = [(output_layer if layer['identifier'] == self._output_layer_id else layer)
                for layer in updated_defs['layers']]
        else:
            updated_defs['layers'] = [output_layer] + updated_defs['layers']

        file_json_updated = copy_update_dict(self._json_obj, {
            'nextUid': self._next_uid,
            'defs': updated_defs,
        })

        return file_json_updated

    # def _remove_duplicate_rules(self, rules):
    #     cleaned = []
    #     for rule in rules:
    #         found = [r for r in cleaned if r['pattern'] == rule['pattern']]
    #         if not found:
    #             cleaned.append(rule)
    #         else:
    #             found_rule = found[0]
    #             new_tile_ids = list(set(found_rule['tileIds'] + rule['tileIds']))
    #             found_rule['tileIds'] = new_tile_ids
    #     return cleaned

    def _create_rules(self):
        source_layer = self._get_level_layer(self._source_layer_id)
        rules = self._rule_creator.create(source_layer)
        return rules

    # def _create_rules(self):
    #     source_layer = self._get_level_layer(self._source_layer_id)
    #     rules = []
    #     for grid_tile in source_layer['gridTiles']:
    #         if grid_tile['t'] in self._empty_tile_ids:
    #             continue

    #         pattern = self._get_pattern_for_tile(source_layer['gridTiles'], grid_tile['px'])
    #         rule = copy_update_dict(self._rule_template, {
    #             'uid': self._get_next_uid(),
    #             'tileIds': [grid_tile['t']],
    #             'pattern': pattern,
    #         })
    #         rules.append(rule)
    #     rules = self._remove_duplicate_rules(rules)
    #     rules.sort(key=lambda r: self._sort_pattern(r))

    #     rules = self._simplifier.simplify(rules)

    #     return rules

    # def _sort_pattern(self, rule):
    #     total_sum = sum(rule['pattern'])
    #     return total_sum

    # def _get_pattern_for_tile(self, grid_tiles, position):
    #     x, y = position
    #     left_x, right_x = (x - self._tile_size), (x + self._tile_size)
    #     above_y, under_y = (y - self._tile_size), (y + self._tile_size)

    #     pattern = [
    #         self._tile_is_filled(grid_tiles, [left_x, above_y]),
    #         self._tile_is_filled(grid_tiles, [x, above_y]),
    #         self._tile_is_filled(grid_tiles, [right_x, above_y]),

    #         self._tile_is_filled(grid_tiles, [left_x, y]),
    #         1,
    #         self._tile_is_filled(grid_tiles, [right_x, y]),

    #         self._tile_is_filled(grid_tiles, [left_x, under_y]),
    #         self._tile_is_filled(grid_tiles, [x, under_y]),
    #         self._tile_is_filled(grid_tiles, [right_x, under_y]),
    #     ]
        
    #     return pattern
    
    # def _tile_is_filled(self, grid_tiles, position):
    #     filtered_tile_ids = [t['t'] for t in grid_tiles if t['px'][0] == position[0] and t['px'][1] == position[1]]
    #     if len(filtered_tile_ids) == 0 or self._list_intersects(filtered_tile_ids, self._empty_tile_ids):
    #         return -1
    #     else:
    #         return 0
    
    # def _list_intersects(self, list1, list2):
    #     found = [i1 for i1 in list1 if i1 in list2]
    #     return len(found) > 0

    def _get_next_uid(self):
        self._next_uid += 1
        return self._next_uid - 1

    def _get_json(self, file_name):
        with open(file_name) as fp:
            json_str = fp.read()
        json_obj = json.loads(json_str)
        return json_obj

    def _get_level(self, json_obj, source_level_id):
        levels = json_obj['levels']
        filtered = [l for l in levels if l['identifier'] == source_level_id]
        # TODO: error if len(filtered) != 1
        return filtered[0]

    def _get_level_layer(self, layer_id):
        level_obj = self._get_level(self._json_obj, self._source_level_id)
        levels = level_obj['layerInstances']
        filtered = [l for l in levels if l['__identifier'] == layer_id]
        # TODO: error if len(filtered) != 1
        return filtered[0]

    def _get_def_layer(self, layer_id):
        layers = self._json_obj['defs']['layers']
        filtered = [l for l in layers if l['identifier'] == layer_id]
        if filtered:
            return filtered[0]

        layer = copy_update_dict(self._layer_template, {
            'name': layer_id,
            'uid': self._get_next_uid(),
            'autoRuleGroups': [],
        })

        return layer

    def _prepare_options(self, options):
        prepared_options = copy_update_dict(self._default_options, options or {})
        if prepared_options['simplified']:
            prepared_options = copy_update_dict(prepared_options, SIMPLIFIED_OPTIONS)
        return prepared_options

    def _create_simplifier(self):
        self._simplifier = Simplifier(
            corners=self._options['simplified_corners'],
            tjoins=self._options['simplified_tjoins'],
            point=self._options['simplified_point'],
            stubs=self._options['simplified_stubs'],
            pjoins=self._options['simplified_pjoins'],
        )
