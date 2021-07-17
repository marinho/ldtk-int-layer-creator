LAYER_TEMPLATE = {
    "__type": "IntGrid",
    "identifier": "IntGrid",  # affected
    "type": "IntGrid",
    "uid": 0,  # affected
    "gridSize": 16,
    "displayOpacity": 1,
    "pxOffsetX": 0,
    "pxOffsetY": 0,
    "requiredTags": [],
    "excludedTags": [],
    "intGridValues": [{"value": 1, "identifier": None, "color": "#000000"}],
    "autoTilesetDefUid": 1,
    "autoRuleGroups": [],
    "autoSourceLayerDefUid": None,
    "tilesetDefUid": None,
    "tilePivotX": 0,
    "tilePivotY": 0
}

GROUP_TEMPLATE = {
    "uid": '',  # affected
    "name": "New group",  # affected
    "active": True,
    "collapsed": False,
    "isOptional": False,
    "rules": []  # affected
}

RULE_TEMPLATE = {
    "uid": '',  # affected
    "active": True,
    "size": 3,
    "tileIds": [],  # affected
    "chance": 1,
    "breakOnMatch": True,
    "pattern": [],  # affected - e.x. [-1,-1,-1,-1,1,0,0,0,0],
    "flipX": False,  # XXX: later
    "flipY": False,  # XXX: later
    "xModulo": 1,
    "yModulo": 1,
    "checker": "None",
    "tileMode": "Single",
    "pivotX": 0,
    "pivotY": 0,
    "outOfBoundsValue": None,
    "perlinActive": False,
    "perlinSeed": 6841713,  # XXX: no idea
    "perlinScale": 0.2,
    "perlinOctaves": 2
}

DEFAULT_OPTIONS = {
    'simplified': False,
    'simplified_corners': False,
    'simplified_tjoins': False,
    'simplified_point': False,
    'simplified_stubs': False,
    'simplified_pjoins': False,
}

SIMPLIFIED_OPTIONS = {
    'simplified_corners': True,
    'simplified_tjoins': True,
    'simplified_point': True,
    'simplified_stubs': True,
    'simplified_pjoins': True,
}
