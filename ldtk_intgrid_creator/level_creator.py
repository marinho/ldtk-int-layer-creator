import json
from functools import reduce
from .dict_templates import LAYER_TEMPLATE, DEFAULT_OPTIONS
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
    _default_options = DEFAULT_OPTIONS

    _simplifier = None # Simplifier()
    _group_creator = None # GroupCreator
    _rule_creator = None # RuleCreator

    def __init__(self, file_name, source_level_id, source_layer_id, output_layer_id, tile_size, empty_tile_ids, options=None):
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

    def _create_rules(self):
        source_layer = self._get_level_layer(self._source_layer_id)
        rules = self._rule_creator.create(source_layer)
        return rules

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
        return prepared_options

    def _create_simplifier(self):
        self._simplifier = Simplifier(
            corners=self._options['simplified'] or self._options['simplified_corners'],
            tjoins=self._options['simplified'] or self._options['simplified_tjoins'],
            point=self._options['simplified'] or self._options['simplified_point'],
            stubs=self._options['simplified'] or self._options['simplified_stubs'],
            pjoins=self._options['simplified'] or self._options['simplified_pjoins'],
        )
