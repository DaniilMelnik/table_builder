# encoding=utf-8
import arcpy
import sys
import locale
import os

from collections import namedtuple

Coding_CMD_Window = sys.stdout.encoding
Coding_OS = locale.getpreferredencoding()
Coding_Script = sys.getdefaultencoding()
Coding2Use = Coding_CMD_Window
if any('arcpy' in importedmodules for importedmodules in sys.modules):
    Coding2Use = Coding_OS


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "geo_tools"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Table_builder]


class Table_builder(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Table_builder"
        self.description = "The script generates geological table by hole .shp files created CutsBuilder program"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        input_layer = arcpy.Parameter(
            displayName="input layer",
            name="hole_layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        # input_layer = arcpy.Parameter(
        #     displayName="input map",
        #     name="map_path",
        #     datatype="DEMapDocument",
        #     parameterType="Required",
        #     direction="Input")
        field_mapping = arcpy.Parameter(
            displayName="field mapping",
            name="hole_fields",
            datatype="GPFieldMapping",
            parameterType="Optional",
            direction="Input")
        table_offset = arcpy.Parameter(
            displayName="offset",
            name="in_features",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        # field_mapping.columns = [["GPSting", "parameters"], ["GPLong", "Field"]]
        input_layer.value = os.path.join(os.getcwd(), 'DHSBore_pls_LC24.shp')
        # input_layer.value = 'D:\\DS\\table_builder\\data\\test_map.mxd'
        # field_mapping.parameterDependencies = [input_layer.name]
        params = [input_layer, field_mapping, table_offset]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        # if parameters[0].value:
        #     parameters[1].enabled = True
        # else:
        #     parameters[1].enabled = False
        # if parameters[0].altered:
        #     inputTable = parameters[0].value
        #     #
        #     # # add a temporary item to the field mappings list
        #     # # can be removed later by calling parameters[1].value.removeFieldMap(0)
        #     parameters[1].value = str('Empty')
        #     #
        #     # # add table fields
        #     parameters[1].value.addTable(inputTable)

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        arcpy.env.overwriteOutput = True
        path = parameters[0].value
        offset = 50  # param
        table_width = 5  # param
        table_boundaries_offset = 10  # param

        # Hardcoded
        n_fields = 4
        field_names_offset = 50

        # mxd = arcpy.mapping.MapDocument("CURRENT")
        Hole = namedtuple('Hole', ['name', 'x', 'y', 'length'])
        hole_list = []
        bottom_point = None
        left_hole_x, right_hole_x = None, None
        with arcpy.da.SearchCursor(path, ['name', "SHAPE@", 'length']) as cursor:
            for row in cursor:
                hole_list.append(Hole(row[0], row[1].firstPoint.X, row[1].firstPoint.Y, row[2]))
                hole_bottom_point = row[1].lastPoint.Y
                hole_x = row[1].firstPoint.X
                if not bottom_point or hole_bottom_point < bottom_point:
                    bottom_point = hole_bottom_point
                if not left_hole_x or hole_x < left_hole_x:
                    left_hole_x = hole_x
                if not right_hole_x or hole_x > right_hole_x:
                    right_hole_x = hole_x
            arcpy.AddMessage(hole_list)

        table = []
        for hole in hole_list:
            hole_line = arcpy.Polyline(
                arcpy.Array(
                    [arcpy.Point(hole.x, bottom_point - offset - table_width),
                     arcpy.Point(hole.x, bottom_point - offset - 2 * table_width)]
                )
            )
            table.append(hole_line)

        for field_num in range(n_fields + 2):
            if field_num == 3:
                continue
            table_line = arcpy.Polyline(
                arcpy.Array(
                    [arcpy.Point(left_hole_x - table_boundaries_offset - field_names_offset,
                                 bottom_point - offset - table_width * field_num),
                     arcpy.Point(right_hole_x + table_boundaries_offset,
                                 bottom_point - offset - table_width * field_num)]
                )
            )
            table.append(table_line)

        vertical_lines = [
            [(left_hole_x - table_boundaries_offset - field_names_offset,
              bottom_point - offset),
             (left_hole_x - table_boundaries_offset - field_names_offset,
              bottom_point - offset - table_width * (n_fields + 1))
             ],
            [(left_hole_x - table_boundaries_offset,
              bottom_point - offset),
             (left_hole_x - table_boundaries_offset,
              bottom_point - offset - table_width * (n_fields + 1))
             ],
            [(right_hole_x + table_boundaries_offset,
              bottom_point - offset),
             (right_hole_x + table_boundaries_offset,
              bottom_point - offset - table_width * (n_fields + 1))
             ],
        ]
        table.extend([arcpy.Polyline(arcpy.Array([arcpy.Point(*pt) for pt in line])) for line in vertical_lines])
        arcpy.CopyFeatures_management(table, os.path.join(os.getcwd(), 'test.shp'))

        annotations = []
        hole_names = arcpy.Array([arcpy.Point(hole.x, bottom_point - offset - table_width) for hole in hole_list])

        annotations.append(hole_names)

        return

# class NamedList(list):
#     def __init__(self, seq, names):
#         super(NamedList, self).__init__(seq)
#         self.mapping = {k: v for k, v in zip(names, seq)}
#
#     def __getitem__(self, key):
#         return self.mapping[key] if isinstance(key, str) else super(NamedList, self).__getitem__(key)
#
#
