class Simplifier(object):
    def __init__(self, options):
        self._options = options

    def simplify(self, rules):
        if self._options['simplified_corners']:
            rules = [self._copy_update_dict(r, {'pattern': self._simplify_pattern_corners(r['pattern'])}) for r in rules]
        if self._options['simplified_tjoins']:
            rules = [self._copy_update_dict(r, {'pattern': self._simplify_pattern_tjoins(r['pattern'])}) for r in rules]
        if self._options['simplified_point']:
            rules = [self._copy_update_dict(r, {'pattern': self._simplify_pattern_point(r['pattern'])}) for r in rules]
        if self._options['simplified_ends']:
            rules = [self._copy_update_dict(r, {'pattern': self._simplify_pattern_ends(r['pattern'])}) for r in rules]
        if self._options['simplified_pjoins']:
            rules = [self._copy_update_dict(r, {'pattern': self._simplify_pattern_pjoins(r['pattern'])}) for r in rules]
        return rules

    def _copy_update_dict(self, d1, d2):
        the_copy = d1.copy()
        the_copy.update(d2)
        return the_copy

    def _simplify_pattern_corners(self, pattern):
        # Thin
        if pattern == [-1,-1,-1,-1,1,0,-1,0,-1]:
            return [-1,-1,0,-1,1,0,0,0,-1]
        elif pattern == [-1,-1,-1,0,1,-1,-1,0,-1]:
            return [0,-1,-1,0,1,-1,-1,0,0]
        elif pattern == [-1,0,-1,-1,1,0,-1,-1,-1]:
            return [0,0,-1,-1,1,0,-1,-1,0]
        elif pattern == [-1,0,-1,0,1,-1,-1,-1,-1]:
            return [-1,0,0,0,1,-1,0,-1,-1]

        # Thick
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
        if pattern == [-1,-1,-1,0,1,0,-1,0,-1]:
            return [0,-1,0,0,1,0,-1,0,-1]
        elif pattern == [-1,0,-1,0,1,0,-1,-1,-1]:
            return [-1,0,-1,0,1,0,0,-1,0]
        elif pattern == [-1,0,-1,-1,1,0,-1,0,-1]:
            return [0,0,-1,-1,1,0,0,0,-1]
        elif pattern == [-1,0,-1,0,1,-1,-1,0,-1]:
            return [-1,0,0,0,1,-1,-1,0,0]
        return pattern

    def _simplify_pattern_point(self, pattern):
        if pattern == [-1,-1,-1,-1,1,-1,-1,-1,-1]:
            return [0,-1,0,-1,1,-1,0,-1,0]
        return pattern

    def _simplify_pattern_ends (self, pattern):
        if pattern[1] == -1 and pattern[3] == -1 and pattern[5] == -1 and pattern[7] == 0:
            return [0,-1,0,-1,1,-1,0,0,0]
        elif pattern[1] == 0 and pattern[3] == -1 and pattern[5] == -1 and pattern[7] == -1:
            return [0,0,0,-1,1,-1,0,-1,0]
        elif pattern[1] == -1 and pattern[3] == 0 and pattern[5] == -1 and pattern[7] == -1:
            return [0,-1,0,0,1,-1,0,-1,0]
        elif pattern[1] == -1 and pattern[3] == -1 and pattern[5] == 0 and pattern[7] == -1:
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
