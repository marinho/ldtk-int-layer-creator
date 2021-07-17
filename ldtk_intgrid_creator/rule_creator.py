from .dict_templates import RULE_TEMPLATE
from .utilities import copy_update_dict


class RuleCreator(object):
    _rule_template = RULE_TEMPLATE
    _get_next_uid = lambda: None
    _empty_tile_ids = None  # list
    _simplifier = None # Simplifier()
    _tile_size = 16 # px

    def __init__(self, get_next_uid_function, simplifier, empty_tile_ids, tile_size):
        self._get_next_uid = get_next_uid_function
        self._simplifier = simplifier
        self._empty_tile_ids = empty_tile_ids or []
        self._tile_size = tile_size

    def create(self, source_layer):
        rules = []
        for grid_tile in source_layer['gridTiles']:
            if grid_tile['t'] in self._empty_tile_ids:
                continue

            pattern = self._get_pattern_for_tile(source_layer['gridTiles'], grid_tile['px'])
            rule = copy_update_dict(self._rule_template, {
                'uid': self._get_next_uid(),
                'tileIds': [grid_tile['t']],
                'pattern': pattern,
            })
            rules.append(rule)
        rules = self._remove_duplicate_rules(rules)
        rules.sort(key=lambda r: self._sort_pattern(r))

        rules = self._simplifier.simplify(rules)

        return rules

    def _sort_pattern(self, rule):
        total_sum = sum(rule['pattern'])
        return total_sum

    def _get_pattern_for_tile(self, grid_tiles, position):
        x, y = position
        left_x, right_x = (x - self._tile_size), (x + self._tile_size)
        above_y, under_y = (y - self._tile_size), (y + self._tile_size)

        pattern = [
            self._tile_is_filled(grid_tiles, [left_x, above_y]),
            self._tile_is_filled(grid_tiles, [x, above_y]),
            self._tile_is_filled(grid_tiles, [right_x, above_y]),

            self._tile_is_filled(grid_tiles, [left_x, y]),
            1,
            self._tile_is_filled(grid_tiles, [right_x, y]),

            self._tile_is_filled(grid_tiles, [left_x, under_y]),
            self._tile_is_filled(grid_tiles, [x, under_y]),
            self._tile_is_filled(grid_tiles, [right_x, under_y]),
        ]
        
        return pattern
    
    def _tile_is_filled(self, grid_tiles, position):
        filtered_tile_ids = [t['t'] for t in grid_tiles if t['px'][0] == position[0] and t['px'][1] == position[1]]
        if len(filtered_tile_ids) == 0 or self._list_intersects(filtered_tile_ids, self._empty_tile_ids):
            return -1
        else:
            return 0
    
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

    def _list_intersects(self, list1, list2):
        found = [i1 for i1 in list1 if i1 in list2]
        return len(found) > 0
