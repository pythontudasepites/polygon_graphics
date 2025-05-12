from fundamental_classes import PolygonGraphics
from typing import Self
import tkinter as tk


class Triangle(PolygonGraphics):
    def __init__(self, canvas: tk.Canvas, *vertex_points, **options):
        self._vertices_coords: tuple = tuple(self._flatten_xycoords(vertex_points))
        if not len(self._vertices_coords) == 6:
            raise ValueError('A megadott pontok nem háromszöget határoznak meg.')
        super().__init__(canvas, **options)

    def _create_graphics(self):
        self.canvas.create_polygon(*self._sort_vertices_for_proper_plotting(self._vertices_coords), tags=(self.id_tag,))

    def _instance_factory(self) -> Self:
        return type(self)(self.canvas, *self.get_coords())
