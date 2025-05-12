import tkinter as tk
from itertools import chain
from math import sqrt, acos, degrees
from fundamental_classes import PolygonGraphics


class ConcaveCircularHypotenuse(PolygonGraphics):

    def __init__(self, canvas: tk.Canvas, side: int | float, k: int | float = 1, **options):
        if side < 0:
            raise ValueError('Az oldalhossz csak pozitív szám lehet.')
        if k < 1:
            raise ValueError('A görbület mértékét meghatározó paraméter értéke nem lehet kisebb, mint 1.')
        self.side = side
        self._r = side * sqrt(k)
        super().__init__(canvas, **options)

    def _create_graphics(self) -> None:
        cx = cy = 0.5 * (self.side + sqrt(2 * self._r ** 2 - self.side ** 2))
        delta = degrees(acos(cx / self._r))
        arc_points = [p for p in self.ellipse_arc_points(self._r, self._r, cx, cy, 180 + delta, 270 - delta)]
        self.canvas.create_polygon(*chain(((0, 0), (0, self.side)), arc_points, ((self.side, 0),)), tags=(self.id_tag,))

    def _instance_factory(self):
        return type(self)(self.canvas, self.side, (self._r / self.side) ** 2)
