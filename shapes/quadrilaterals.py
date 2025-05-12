from typing import Iterable, Self
from math import dist, isclose
import tkinter as tk
from fundamental_classes import PolygonGraphics


class Quadrilateral(PolygonGraphics):
    def __init__(self, canvas: tk.Canvas, *vertex_points, **options):
        self._vertices_coords: tuple = tuple(self._flatten_xycoords(vertex_points))
        try:
            if not len(self._vertices_coords) == 8:
                raise ValueError
        except ValueError:
            raise ValueError('A megadott pontok nem négyszöget határoznak meg.')
        super().__init__(canvas, **options)

    def _create_graphics(self):
        self.canvas.create_polygon(*self._sort_vertices_for_proper_plotting(self._vertices_coords), tags=(self.id_tag,))

    def _instance_factory(self) -> Self:
        return type(self)(self.canvas, *self.get_coords())


class Kite(Quadrilateral):
    def __init__(self, canvas: tk.Canvas, *vertex_points, **options):
        super().__init__(canvas, *vertex_points, **options)
        try:
            if not self._is_kite(vertex_points):
                raise ValueError
        except ValueError:
            raise ValueError('A megadott pontok nem deltoidot határoznak meg.')

    def _is_kite(self, *vertices: Iterable) -> bool:
        """Akkor ad vissza True értéket, ha a megadott pontok egy deltoidot alkotnak.
        Egy sokszög deltoid, ha négyszög és két-két szomszédos oldala egyenlő hosszú.
        A csúcspontokat az x, y koordináták egymást követő felsorolsával, vagy az x, y párokat szolgáltató iterálható
        objektumok felsorolásával lehet megadni.
        """
        sides = self.side_lengths(vertices)
        # Ha két-két szomszédos oldal egyenlő, akkor deltoid. Ez a rendezett csúcspontokból meghatározott oldalak sorozatában
        # úgy fordulhat elő, hogy vagy az első kettő és a második kettő oldal egyenlő, vagy a középső kettő és a két szélső.
        return len(sides) == 4 and (self._all_equal(*sides[:2]) and self._all_equal(*sides[2:])) or \
            (self._all_equal(*sides[1:3]) and self._all_equal(sides[0], sides[-1]))


class Trapezoid(Quadrilateral):
    def __init__(self, canvas: tk.Canvas, *vertex_points, **options):
        super().__init__(canvas, *vertex_points, **options)
        try:
            if not self.is_trapezoid(vertex_points):
                raise ValueError
        except ValueError:
            raise ValueError('A megadott pontok nem trapézt határoznak meg.')

    def is_trapezoid(self, *vertices: Iterable) -> bool:
        """Akkor ad vissza True értéket, ha a megadott pontok egy trapézt alkotnak.
        Egy sokszög trapéz, ha négyszög és vannak párhuzamos szemközti oldalai.
        A csúcspontokat az x, y koordináták egymást követő felsorolsával, vagy az x, y párokat szolgáltató iterálható
        objektumok felsorolásával lehet megadni.
        """
        sorted_points = self._sort_vertices_for_proper_plotting(vertices)
        if len(sorted_points) == 4:
            x1, y1, x2, y2, x3, y3, x4, y4 = self._flatten_xycoords(sorted_points)
            # A csúcspontok rendezettségéből adódóan, ha a négyszög trapéz, akkor két eset lehet:
            # 1) az (x1, y1) és (x2, y2) pontokkal meghatározott oldal, valamint az (x3, y3) és (x4, y4) pontokkal
            # meghatározott oldal szemközti oldalak, és ezek párhuzamosak, vagy
            # 2) az (x2, y2) és (x3, y3) pontokkal meghatározott oldal, valamint az (x4, y4) és (x1, y1) pontokkal
            # meghatározott oldal szemközti oldalak, és ezek párhuzamosak.
            # A párhuzamosságot a szemközti oldalak meredekségének összevetésével ellenőrizzük.

            if isclose((y2 - y1) / (x2 - x1), (y4 - y3) / (x4 - x3)) or isclose((y3 - y2) / (x3 - x2), (y4 - y1) / (x4 - x1)):
                return True
        return False


class Parallelogram(Quadrilateral):
    def __init__(self, canvas: tk.Canvas, *vertex_points, **options):
        super().__init__(canvas, *vertex_points, **options)
        # print('paralogramma methods', [mn for mn in dir(self) if not mn.startswith('__')])
        try:
            if not self._is_parallelogram(vertex_points):
                raise ValueError
        except ValueError:
            raise ValueError('A megadott pontok nem paralelogrammát határoznak meg.')

    def _is_parallelogram(self, *vertices: Iterable) -> bool:
        """Akkor ad vissza True értéket, ha a megadott pontok egy paralelogrammát alkotnak.
        Egy sokszög paralelogramma, ha négyszög és szemközti oldalai párhuzamosak.
        A paralelogramma szemközti oldalai egyenlő hosszúak.
        A csúcspontokat az x, y koordináták egymást követő felsorolsával, vagy az x, y párokat szolgáltató iterálható
        objektumok felsorolásával lehet megadni.
        """
        sorted_points = self._sort_vertices_for_proper_plotting(vertices)
        if len(sorted_points) == 4:
            x1, y1, x2, y2, x3, y3, x4, y4 = self._flatten_xycoords(sorted_points)
            # A csúcspontok rendezettségéből adódóan, ha a négyszög paralelogramma, akkor két eset lehet:
            # 1) az (x1, y1) és (x2, y2) pontokkal meghatározott oldal, valamint az (x3, y3) és (x4, y4) pontokkal
            # meghatározott oldal szemközti oldalak, és ezek párhuzamosak, vagy
            # 2) az (x2, y2) és (x3, y3) pontokkal meghatározott oldal, valamint az (x4, y4) és (x1, y1) pontokkal
            # meghatározott oldal szemközti oldalak, és ezek párhuzamosak.
            # A párhuzamosságot a szemközti oldalak meredekségének összevetésével ellenőrizzük.
            # Párhuzamosság esetén a szakaszhosszok egyenlőségét is ellenőrizni kell.

            if isclose((y2 - y1) / (x2 - x1), (y4 - y3) / (x4 - x3)):
                return isclose(dist((x1, y1), (x2, y2)), dist((x3, y3), (x4, y4)))
            elif isclose((y3 - y2) / (x3 - x2), (y4 - y1) / (x4 - x1)):
                return isclose(dist((x2, y2), (x3, y3)), dist((x4, y4), (x1, y1)))
        return False


class Rhombus(Quadrilateral):
    def __init__(self, canvas: tk.Canvas, *vertex_points, **options):
        super().__init__(canvas, *vertex_points, **options)
        try:
            if not self._is_rhombus(vertex_points):
                raise ValueError
        except ValueError:
            raise ValueError('A megadott pontok nem rombuszt határoznak meg.')

    def _is_rhombus(self, *vertices: Iterable) -> bool:
        """Akkor ad vissza True értéket, ha a megadott pontok egy rombuszt alkotnak.
        Egy sokszög rombusz, ha négyszög és minden oldala egyenlő.
        A csúcspontokat az x, y koordináták egymást követő felsorolsával, vagy az x, y párokat szolgáltató iterálható
        objektumok felsorolásával lehet megadni.
        """
        sides = self.side_lengths(vertices)
        # Ha négyszög (négy oldala van) és minden oldala egyenlő, akkor rombusz.
        return len(sides) == 4 and self._all_equal(*sides)


class Rectangle(Quadrilateral):

    def __init__(self, canvas: tk.Canvas, *vertex_points, **options):
        super().__init__(canvas, *vertex_points, **options)
        if not self._is_rectangle(vertex_points):
            raise ValueError('A megadott pontok nem téglalapot határoznak meg.')

    @classmethod
    def from_sides(cls, canvas: tk.Canvas, a: int | float, b: int | float, upperleft_x=0, upperleft_y=0, **options):
        """A téglalapot az a és b oldalainak hosszával lehet megadni. Ekkor egy olyan téglalap jön létre, amelynek a oldala
        az x, b oldala az y tengellyel párhuzamos.
        A négyzetet létrehozáskor elhelyezni a bal felső sarkának koordinátáival lehet, amely alapértelmezetten az origó.
        """
        points = ((upperleft_x, upperleft_y), (upperleft_x + a, upperleft_y),
                  (upperleft_x + a, upperleft_y + b), (upperleft_x, upperleft_y + b))
        return cls(canvas, *points, **options)

    def _is_rectangle(self, *vertices: Iterable) -> bool:
        """Akkor ad vissza True értéket, ha a megadott pontok egy téglalapot alkotnak.
        Egy sokszög téglalap, ha négyszög és minden szöge egyenlő.
        Ebből következik, hogy a csúcsok középponttól (sűlyponttól) mért távolsága egyenlő.
        A csúcspontokat az x, y koordináták egymást követő felsorolsával, vagy az x, y párokat szolgáltató iterálható
        objektumok felsorolásával lehet megadni.
        """
        # Az ellenörzés módja: négy csúcs van-e, és a csúcsok középponttól (súlyponttól) mért távolsága egyenlő-e.
        sorted_points = self._sort_vertices_for_proper_plotting(vertices)
        # Meghatározzuk a csúcspontok középpontját (súlypontját).
        centroid_x, centroid_y = self.vertices_centroid(vertices)
        # Ha négyszög és a csúcsok távolsága a középpontól egyenlő, akkor téglalap.
        distances_to_vertices = (dist((centroid_x, centroid_y), vertex) for vertex in sorted_points)
        return len(sorted_points) == 4 and self._all_equal(*distances_to_vertices)


class Square(Quadrilateral):
    def __init__(self, canvas: tk.Canvas, *vertex_points, **options):
        super().__init__(canvas, *vertex_points, **options)
        try:
            if not self._is_square(vertex_points):
                raise ValueError
        except ValueError:
            raise ValueError('A megadott pontok nem négyzetet határoznak meg.')

    @classmethod
    def from_side(cls, canvas: tk.Canvas, side: int | float, upperleft_x=0, upperleft_y=0, **options):
        """A négyzetet a side oldalhosszával lehet megadni. Ekkor egy olyan négyzet jön létre, amelynek oldalai
        az x és y tengelyekkel párhuzamosak.
        A négyzetet létrehozáskor elhelyezni a bal felső sarkának koordinátáival lehet, amely alapértelmezetten az origó.
        """
        points = ((upperleft_x, upperleft_y), (upperleft_x + side, upperleft_y),
                  (upperleft_x + side, upperleft_y + side), (upperleft_x, upperleft_y + side))
        inst = cls(canvas, *points, **options)
        inst._vertices_coords = points
        return inst

    def _is_square(self, *vertices: Iterable) -> bool:
        """Akkor ad vissza True értéket, ha a megadott pontok egy négyzetet alkotnak.
        Egy sokszög négyzet, ha négyszög és minden szöge egyenlő és minden oldala egyenlő.
        Ebből következik, hogy a csúcsok középponttól (sűlyponttól) mért távolsága egyenlő.
        A csúcspontokat az x, y koordináták egymást követő felsorolsával, vagy az x, y párokat szolgáltató iterálható
        objektumok felsorolásával lehet megadni.
        """
        sorted_points = self._sort_vertices_for_proper_plotting(vertices)
        sides = self.side_lengths(vertices)
        # Meghatározzuk a csúcspontok középpontját (súlypontját).
        centroid_x, centroid_y = self.vertices_centroid(vertices)
        # Ha négyszög és a csúcsok távolsága a középpontól egyenlő, akkor téglalap.
        distances_to_vertices = (dist((centroid_x, centroid_y), vertex) for vertex in sorted_points)
        # Ha téglalap és minden oldala egyenlő, akkor négyzet.
        return self._all_equal(*distances_to_vertices) and self._all_equal(*sides)
