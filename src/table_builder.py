# encoding=utf-8
import os
from collections import namedtuple

import arcpy

Hole = namedtuple('Hole', ['name', 'x', 'y', 'length'])


class TableBuilder(object):
    def __init__(self, hole_path, offset=50, table_width=5, table_boundaries_offset=10, field_names_offset=50):
        self.bottom_point = None
        self.left_hole_x, self.right_hole_x = None, None
        self.hole_list = self._get_holes(hole_path)
        self.offset = offset
        self.table_width = table_width
        self.table_boundaries_offset = table_boundaries_offset
        self.field_names_offset = field_names_offset
        self.n_fields = 4

    def _get_holes(self, path):
        hole_list = []
        with arcpy.da.SearchCursor(path, ['name', "SHAPE@", 'length']) as cursor:
            for row in cursor:
                hole_list.append(Hole(row[0], row[1].firstPoint.X, row[1].firstPoint.Y, row[2]))
                hole_bottom_point = row[1].lastPoint.Y
                hole_x = row[1].firstPoint.X
                if not self.bottom_point or hole_bottom_point < self.bottom_point:
                    self.bottom_point = hole_bottom_point
                if not self.left_hole_x or hole_x < self.left_hole_x:
                    self.left_hole_x = hole_x
                if not self.right_hole_x or hole_x > self.right_hole_x:
                    self.right_hole_x = hole_x
        return hole_list

    def create_table(self):
        table = []
        for hole in self.hole_list:
            hole_line = arcpy.Polyline(
                arcpy.Array(
                    [arcpy.Point(hole.x, self.bottom_point - self.offset - self.table_width),
                     arcpy.Point(hole.x, self.bottom_point - self.offset - 2 * self.table_width)]
                )
            )
            table.append(hole_line)

        for field_num in range(self.n_fields + 2):
            if field_num == 3:
                continue
            table_line = arcpy.Polyline(
                arcpy.Array(
                    [arcpy.Point(self.left_hole_x - self.table_boundaries_offset - self.field_names_offset,
                                 self.bottom_point - self.offset - self.table_width * field_num),
                     arcpy.Point(self.right_hole_x + self.table_boundaries_offset,
                                 self.bottom_point - self.offset - self.table_width * field_num)]
                )
            )
            table.append(table_line)

        vertical_lines = [
            [(self.left_hole_x - self.table_boundaries_offset - self.field_names_offset,
              self.bottom_point - self.offset),
             (self.left_hole_x - self.table_boundaries_offset - self.field_names_offset,
              self.bottom_point - self.offset - self.table_width * (self.n_fields + 1))
             ],
            [(self.left_hole_x - self.table_boundaries_offset,
              self.bottom_point - self.offset),
             (self.left_hole_x - self.table_boundaries_offset,
              self.bottom_point - self.offset - self.table_width * (self.n_fields + 1))
             ],
            [(self.right_hole_x + self.table_boundaries_offset,
              self.bottom_point - self.offset),
             (self.right_hole_x + self.table_boundaries_offset,
              self.bottom_point - self.offset - self.table_width * (self.n_fields + 1))
             ],
        ]
        table.extend([arcpy.Polyline(arcpy.Array([arcpy.Point(*pt) for pt in line])) for line in vertical_lines])
        return table

    def create_annotations(self):
        annotations = []
        hole_names_coord = [(hole.name, '', '',
                             (hole.x, self.bottom_point - self.offset - self.table_width))
                            for hole in self.hole_list]
        annotations.extend(hole_names_coord)

        hole_depth_coord = [("{:.1f}".format(hole.length), '', '',
                             (hole.x, self.bottom_point - self.offset - self.table_width * (self.n_fields + 1)))
                            for hole in self.hole_list]
        annotations.extend(hole_depth_coord)

        hole_distance_coord = [("{:.1f}".format(hole_2.x - hole_1.x), '', '',
                                (hole_1.x + (hole_2.x - hole_1.x) / 2,
                                 self.bottom_point - self.offset - self.table_width * 2))
                               for hole_1, hole_2 in zip(self.hole_list[:-1], self.hole_list[1:])]
        annotations.extend(hole_distance_coord)

        hole_heights_coord = [('', "{:.1f}".format(hole.y), '',
                               (hole.x, self.bottom_point - self.offset - self.table_width * 3))
                              for hole in self.hole_list]
        annotations.extend(hole_heights_coord)

        field_names = [u'Номер выработки'.encode('cp1251'),
                       u'Расстояние между выработками, м'.encode('cp1251'),
                       u'Проектная абсолютная отметка \n устья выработки, м'.encode('cp1251'),
                       u'Проектная глубина выработки'.encode('cp1251')]

        field_names_coord = []
        addition = 1
        for field, name in zip(range(self.n_fields), field_names):
            if field == 3:
                addition = 2
            field_names_coord.append(('', '', name,
                                      (self.left_hole_x - self.table_boundaries_offset - self.field_names_offset,
                                       self.bottom_point - self.offset - self.table_width * (
                                               field + addition) + self.table_width / 2)))

        annotations.extend(field_names_coord)
        return annotations
