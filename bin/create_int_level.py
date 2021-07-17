import argparse
from ldtk_intgrid_creator import LevelCreator

def prepare_and_parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('ldtk_file', help='Path to LDtk project file. i.e. "../my-project.ldtk"',)
    parser.add_argument('source_level', help='ID of the level to base rules on. i.e. "Level_0"')
    parser.add_argument('source_layer', help='ID of the Tiles layer inside level to base rules on. i.e. "Tiles"')
    parser.add_argument('output_layer', help='ID of the IntGrid layer to save the rules into. i.e. "IntGrid"')
    parser.add_argument('empty_tile', default='', nargs='?', help='IDs (separated by comma) of the tiles that should be taken as empty space. i.e. "137"')
    parser.add_argument('--no-simplified', action='store_true', help='Inform this argument if not wanting simplifier optimiations when defining patterns.')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = prepare_and_parse_args()
    empty_tile_ids = filter(lambda a: bool(a), args.empty_tile.split(','))
    empty_tile_ids = list(map(lambda a: int(a), empty_tile_ids))

    creator = LevelCreator(
        args.ldtk_file,
        args.source_level,
        args.source_layer,
        args.output_layer,
        empty_tile_ids,
        tile_size=16, # FIXME add argument for this
        options=dict(simplified=args.no_simplified)
    )
    creator.update_file_with_int_level()
