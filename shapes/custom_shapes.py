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


# TESZT
if __name__ == '__main__':
    root = tk.Tk()

    cnv = tk.Canvas(root, bg='light yellow', width=1000, height=1000)
    cnv.pack()

    cnv.create_rectangle((100 - 4, 100 - 4), (100 + 4, 100 + 4), fill='black')

    chyp = ConcaveCircularHypotenuse(cnv, 300, k=3,
                                     fill='red',
                                     outline='black',
                                     width=1,
                                     tags=('abc', 'def')
                                     )

    chyp.move(400, 400)

    # chyp2 = ConcaveCircularHypotenuse(cnv, 200, fill='green', width=1)
    chyp2 = chyp.clone()
    chyp2.config(fill='green')
    # chyp2.move(200, 200)
    # chyp2.rotate(90, (200, 200))
    # chyp2.move_to(400 - chyp2.side - 1, 399)
    cnv.create_line((200, 0), (200, 200))
    chyp2.reflect((200, 0), (200, 200))
    chyp2.reflect((0, 200), (200, 200))
    chyp2.reflect(400, 400)
    chyp2.move(200, 200)

    root.mainloop()
