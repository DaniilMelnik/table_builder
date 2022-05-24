import arcpy
import os


def write_shp(path, name, geometry_type, data, fields=None):
    shp_file = arcpy.CreateFeatureclass_management(path, name, geometry_type)

    field_names = []
    if fields:
        for name, field_type in fields:
            field_names.append(name)
            arcpy.AddField_management(shp_file, name, field_type)
    field_names.append('SHAPE@')

    with arcpy.da.InsertCursor(shp_file, field_names) as cursor:
        for row in data:
            if geometry_type == 'POINT':
                cursor.insertRow(row)
            elif geometry_type in ['POLYLINE', 'POLYGON']:
                cursor.insertRow([row])
            else:
                raise TypeError('Not implemented type in utils')
