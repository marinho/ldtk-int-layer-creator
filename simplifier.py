from utilities import copy_update_dict


class Simplifier(object):
    _corners = True
    _tjoins = True
    _point = True
    _stubs = True
    _pjoins = True

    def __init__(self, corners=True, tjoins=True, point=True, stubs=True, pjoins=True):
        self._corners = corners
        self._tjoins = tjoins
        self._point = point
        self._stubs = stubs
        self._pjoins = pjoins

    def simplify(self, rules):
        if self._corners:
            rules = [copy_update_dict(r, {'pattern': self._simplify_pattern_corners(r['pattern'])}) for r in rules]
        if self._tjoins:
            rules = [copy_update_dict(r, {'pattern': self._simplify_pattern_tjoins(r['pattern'])}) for r in rules]
        if self._point:
            rules = [copy_update_dict(r, {'pattern': self._simplify_pattern_point(r['pattern'])}) for r in rules]
        if self._stubs:
            rules = [copy_update_dict(r, {'pattern': self._simplify_pattern_stubs(r['pattern'])}) for r in rules]
        if self._pjoins:
            rules = [copy_update_dict(r, {'pattern': self._simplify_pattern_pjoins(r['pattern'])}) for r in rules]
        return rules

    def _simplify_pattern_corners(self, pattern):
        # 1 tile thin (no filling tile)
        if pattern == [-1,-1,-1,-1,1,0,-1,0,-1]:
            return [-1,-1,0,-1,1,0,0,0,-1]
        elif pattern == [-1,-1,-1,0,1,-1,-1,0,-1]:
            return [0,-1,-1,0,1,-1,-1,0,0]
        elif pattern == [-1,0,-1,-1,1,0,-1,-1,-1]:
            return [0,0,-1,-1,1,0,-1,-1,0]
        elif pattern == [-1,0,-1,0,1,-1,-1,-1,-1]:
            return [-1,0,0,0,1,-1,0,-1,-1]

        # 2+ tiles thick (with filling)
        elif pattern == [-1,-1,-1,-1,1,0,-1,0,0]:
            return [0,-1,0,-1,1,0,0,0,0]
        elif pattern == [-1,-1,-1,0,1,-1,0,0,-1]:
            return [0,-1,0,0,1,-1,0,0,0]
        elif pattern == [0,0,-1,0,1,-1,-1,-1,-1]:
            return [0,0,0,0,1,-1,0,-1,0]
        elif pattern == [-1,0,0,-1,1,0,-1,-1,-1]:
            return [0,0,0,-1,1,0,0,-1,0]

        return pattern

    def _simplify_pattern_tjoins(self, pattern):
        if pattern == [-1,-1,-1,0,1,0,-1,0,-1]: # bar above
            return [0,-1,0,0,1,0,-1,0,-1]
        elif pattern == [-1,0,-1,0,1,0,-1,-1,-1]: # bar under
            return [-1,0,-1,0,1,0,0,-1,0]
        elif pattern == [-1,0,-1,-1,1,0,-1,0,-1]: # bar right
            return [0,0,-1,-1,1,0,0,0,-1]
        elif pattern == [-1,0,-1,0,1,-1,-1,0,-1]: # bar left
            return [-1,0,0,0,1,-1,-1,0,0]
        return pattern

    def _simplify_pattern_point(self, pattern):
        # one single tile with no tiles connecting
        if pattern == [-1,-1,-1,-1,1,-1,-1,-1,-1]:
            return [0,-1,0,-1,1,-1,0,-1,0]
        return pattern

    def _simplify_pattern_stubs (self, pattern):
        if pattern[1] == -1 and pattern[3] == -1 and pattern[5] == -1 and pattern[7] == 0: # connection under
            return [0,-1,0,-1,1,-1,0,0,0]
        elif pattern[1] == 0 and pattern[3] == -1 and pattern[5] == -1 and pattern[7] == -1: # connection above
            return [0,0,0,-1,1,-1,0,-1,0]
        elif pattern[1] == -1 and pattern[3] == 0 and pattern[5] == -1 and pattern[7] == -1: # connection left
            return [0,-1,0,0,1,-1,0,-1,0]
        elif pattern[1] == -1 and pattern[3] == -1 and pattern[5] == 0 and pattern[7] == -1: # connection right
            return [0,-1,0,-1,1,0,0,-1,0]
        return pattern

    def _simplify_pattern_pjoins(self, pattern):
        # looks like a P - bar above
        if pattern == [-1,-1,-1,0,1,0,-1,0,0]:
            return [0,-1,0,0,1,0,-1,0,0]
        elif pattern == [-1,-1,-1,0,1,0,0,0,-1]:
            return [0,-1,0,0,1,0,0,0,-1]
        # looks like a P - bar under
        elif pattern == [-1,0,0,0,1,0,-1,-1,-1]:
            return [-1,0,0,0,1,0,0,-1,0]
        elif pattern == [0,0,-1,0,1,0,-1,-1,-1]:
            return [0,0,-1,0,1,0,0,-1,0]
        # looks like a P - bar left
        elif pattern == [-1,0,-1,-1,1,0,-1,0,0]:
            return [0,0,-1,-1,1,0,0,0,0]
        elif pattern == [-1,0,0,-1,1,0,-1,0,-1]:
            return [0,0,0,-1,1,0,0,0,-1]
        # looks like a P - bar right
        elif pattern == [-1,0,-1,0,1,-1,0,0,-1]:
            return [-1,0,0,0,1,-1,0,0,0]
        elif pattern == [0,0,-1,0,1,-1,-1,0,-1]:
            return [0,0,0,0,1,-1,-1,0,0]
        return pattern
