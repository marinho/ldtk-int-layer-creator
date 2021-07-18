Some explanation here soon...

## How to use it

1. Use [LDtk](https://ldtk.io/) to create a new project
2. in LDtk, create a new Tiles layer, with a sprites image and draw how the sprites should look like (i.e. manually draw a rectangle, a cross, etc. with the right tiles)
3. save the project
4. install this Python package (https://pypi.org/project/ldtk-intgrid-creator/)
5. Run the script like this:

Following this syntax:

```
create_int_level PROJECT_FILE_PATH SOURCE_LEVEL_ID SOURCE_LAYER_ID OUTPUT_INT_GRID_LAYER_ID TILE_SIZE_PX
```

Example:

```
create_int_level ./examples/source.ldtk Level_0 Tiles IntGrid 16
```

6. Load the project again in LDtk
7. Chose the layer you chose as output (i.e. IntGrid)
8. Start drawing and see if it works as expected

### Bonus tip:

If you want to enforce some tiles to be taken as "empty" reference, hover your mouse cursor over them and copy the ID from status bar in "Tile" tag, and write them separated by comma as a last argument for the script command. For instance: if the tile to represent empty tiles is "137", you should write it like this:

```
create_int_level ./examples/source.ldtk Level_0 Tiles IntGrid 16 137
```

## Missing

* update auto-layers based on  after integer grid is updated (based on intGridCsv)
* better docs (specially about installation)
* better testing
