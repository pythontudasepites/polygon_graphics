import tkinter as tk
from fundamental_classes import Group
from shapes.quadrilaterals import Rectangle, Square
from shapes.ellipse_and_circle import Ellipse, Circle
from shapes.custom_shapes import ConcaveCircularHypotenuse

root = tk.Tk()
root.title('Sokszögből előállított síkidomok alkalmazása összetett grafika készítéséhez')

cnv = tk.Canvas(root, bg='light yellow', width=800, height=600)
cnv.pack()

rectangle = Rectangle.from_sides(cnv, 600, 400, 0, 0, fill='light blue')
cx, cy = rectangle.bbox_center()

group = Group(*(ConcaveCircularHypotenuse(cnv, 150, fill='light green') for _ in range(4)))
cch1, cch2, cch3, cch4 = group
group.scale(0, 0, 1.5, 1)
group.move(35, 35)

cch2.reflect(cx, cy)
cch3.reflect(cx, cy, cx - 10, cy)
cch4.reflect((cx, cy), (cx, cy + 10))

ellipse = Ellipse(cnv, 230, 140, cx, cy, fill='gray90', outline='blue', width=5)
square = Square.from_side(cnv, 120, cx - 60, cy - 60, fill='white')
circle = Circle(cnv, 6, *ellipse.center_point, fill='red')

group.add_graphics(rectangle, ellipse, circle, square)
cnv_cx, cnv_cy = cnv.winfo_reqwidth() / 2, cnv.winfo_reqheight() / 2
group.move(cnv_cx - cx, cnv_cy - cy)
group.rotate(-5, (cx, cy))

root.mainloop()
