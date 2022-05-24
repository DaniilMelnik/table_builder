# encoding=utf-8
import arcpy
import os

import table_builder
import utils

arcpy.env.overwriteOutput = True
reload(table_builder)
reload(utils)


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "geo_tools"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [TableBuilder]


class TableBuilder(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "TableBuilder"
        self.description = "The script generates geological table by hole .shp files created CutsBuilder program"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        input_layer = arcpy.Parameter(
            displayName="input layer (name and length field required)",
            name="hole_layer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        output_folder = arcpy.Parameter(
            displayName="output_folder",
            name="output_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")
        name_field = arcpy.Parameter(
            displayName="name_field",
            name="name_field",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        length_field = arcpy.Parameter(
            displayName="length_field",
            name="length_field",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        table_offset = arcpy.Parameter(
            displayName="offset",
            name="in_features",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        table_width = arcpy.Parameter(
            displayName="table_width",
            name="table_width",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        table_boundaries_offset = arcpy.Parameter(
            displayName="table_boundaries_offset",
            name="table_boundaries_offset",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        field_names_offset = arcpy.Parameter(
            displayName="field_names_offset",
            name="field_names_offset",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        name_field.value = 'name'
        length_field.value = 'length'

        # testing
        # input_layer.value = os.path.join(os.getcwd(), 'DHSBore_pls_LC24.shp')
        # output_folder.value = os.getcwd()

        params = [input_layer, output_folder, name_field, length_field, table_offset, table_width,
                  table_boundaries_offset, field_names_offset]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[0].value:
            parameters[1].enabled = True
        else:
            parameters[1].enabled = False

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        input_file = parameters[0].value
        output_path = str(parameters[1].value)
        name_field = parameters[2].value if parameters[2].value else 'name'
        length_field = parameters[3].value if parameters[3].value else 'length'
        table_offset = parameters[4].value if parameters[4].value else 50
        table_width = parameters[5].value if parameters[5].value else 5
        table_boundaries_offset = parameters[6].value if parameters[6].value else 10
        field_names_offset = parameters[7].value if parameters[7].value else 50

        tb = table_builder.TableBuilder(
            input_file,
            offset=table_offset,
            table_width=table_width,
            table_boundaries_offset=table_boundaries_offset,
            field_names_offset=field_names_offset,
            name_field=name_field,
            length_field=length_field
        )

        table = tb.create_table()
        utils.write_shp(output_path, 'test.shp', 'POLYLINE', table)

        annotations = tb.create_annotations()
        utils.write_shp(parameters[1].value, 'anno.shp', 'POINT', annotations,
                        [('top', 'TEXT'), ('height', 'TEXT'), ('row_names', 'TEXT')])

        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        arcpy.mapping.AddLayer(df, arcpy.mapping.Layer(os.path.join(output_path, 'test.shp')), "BOTTOM")
        arcpy.mapping.AddLayer(df, arcpy.mapping.Layer(os.path.join(output_path, 'anno.shp')), "BOTTOM")

        # template_layer = arcpy.mapping.ListLayers(mxd, "anno", df)[0]
        # source_Layer = arcpy.mapping.Layer(os.path.join(os.getcwd(), 'template.shp'))

        # base_label_classes = [lbl_class for lbl_class in template_layer.labelClasses]
        # arcpy.AddMessage(base_label_classes)
        # source_Layer.labelClasses = base_label_classes

        return
