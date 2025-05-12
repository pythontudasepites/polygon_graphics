import tkinter as tk
from typing import Self
from fundamental_classes import PolygonGraphics


class Ellipse(PolygonGraphics):

    def __init__(self, canvas: tk.Canvas, semi_major_axis: int | float, semi_minor_axis: int | float,
                 center_x: int | float = 0, center_y: int | float = 0, **options):
        self.semi_major_axis, self.semi_minor_axis = semi_major_axis, semi_minor_axis
        self._center_point = (center_x, center_y)
        super().__init__(canvas, **options)

    @property
    def center_point(self) -> tuple[int | float, int | float]:
        """Az elliszis aktuális középpontjának koordinátáit adja vissza."""
        # Ha már létrejött a grafika, akkor annak aktuális befoglaló téglalapjából határozzuk meg a középpontot.
        # Ha még nem jött létre (példányosításkor), akkor a konstruktorban megadott lesz.
        try:
            return self.bbox_center()
        except (TypeError, AttributeError):
            return self._center_point

    def _create_graphics(self) -> None:
        arc_points = (p for p in self.ellipse_arc_points(self.semi_major_axis, self.semi_minor_axis, *self.center_point))
        self.canvas.create_polygon(*arc_points, tags=(self.id_tag,))

    def _instance_factory(self) -> Self:
        return type(self)(self.canvas, self.semi_major_axis, self.semi_minor_axis, *self.center_point)


class Circle(PolygonGraphics):

    def __init__(self, canvas: tk.Canvas, radius: int | float, center_x: int | float = 0, center_y: int | float = 0, **options):
        self.radius = radius
        self._center_point = (center_x, center_y)
        self._circle = Ellipse(canvas, radius, radius, center_x, center_y, **options)
        super().__init__(canvas, **options)

    @property
    def center_point(self) -> tuple[int | float, int | float]:
        """A kör középpontjának koordinátáit adja vissza."""
        try:
            return self.bbox_center()
        except (TypeError, AttributeError):
            return self._center_point

    def _create_graphics(self) -> None:
        # Az ellipszis grafikához hozzáadjuk a körpéldány azonosítócímkéjét, majd töröljül az ellipszis eredeti azonosítóját.
        self.canvas.addtag_withtag(self.id_tag, self._circle.id_tag)
        self.canvas.dtag(self.id_tag, self._circle.id_tag)

    def _instance_factory(self) -> Self:
        return type(self)(self.canvas, self.radius, *self.center_point)
