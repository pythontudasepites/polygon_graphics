import tkinter as tk
from fundamental_classes import Group
from shapes.quadrilaterals import Rectangle, Trapezoid
from shapes.ellipse_and_circle import Ellipse, Circle
from shapes.triangles import Triangle
from shapes.custom_shapes import ConcaveCircularHypotenuse

root = tk.Tk()
root.title('Sokszögből előállított síkidomok alkalmazása összetett grafika készítéséhez')

canvas_width, canvas_height = 600, 600
cnv = tk.Canvas(root, bg='light yellow', width=canvas_width, height=canvas_height)
cnv.pack()

# A PENGE, A HEGY ÉS HORONY LÉTREHOZÁSA.
blade_width, blade_length = 40, 350  # A penge szélessége és hossza.
blade_rectangle = Rectangle(cnv, (- blade_width / 2, 0), (+ blade_width / 2, 0),
                            (-blade_width / 2, blade_length * 0.85), (blade_width / 2, blade_length * 0.85), fill='silver',
                            outline='')
blade_point = Triangle(cnv, (-blade_width / 2, blade_length * 0.85), (blade_width / 2, blade_length * 0.85),
                       (0, blade_length * 0.85 * 1.15), fill='silver', outline='')
blade_fuller = Triangle(cnv, (- blade_width * 0.05, 0), (+ blade_width * 0.05, 0), (0, blade_length * 0.8), fill='gray90',
                        outline='')
blade = Group(blade_rectangle, blade_fuller, blade_point)

# A KERESZTVAS ÉS SAROKFORMÁINAK LÉTREHOZÁSA.
guard_width, guard_height = 120, 15  # A keresztvas szélessége és magassága.
# A kézfejet védő keresztvasat egy téglalappal jelenítjük meg.
cross_rectangle = Rectangle.from_sides(cnv, guard_width, guard_height, 0, 0, fill='gray50', outline='')
# A keresztvas négy sarkára egy-egy íves elemet helyezünk, ami fokozza a védelmet és díszítésként is szolgál.
corner_shape1 = ConcaveCircularHypotenuse(cnv, guard_height, fill='gray50', outline='')
corner_shape1.move(0, guard_height - 1)
corner_shape2 = corner_shape1.clone()
corner_shape2.reflect(cross_rectangle.bbox_center())
corner_shape3 = corner_shape2.clone()
corner_shape3.reflect(cross_rectangle.bbox_center(),
                      (cross_rectangle.bbox_center()[0], cross_rectangle.bbox_center()[1] - 10))
corner_shape4 = corner_shape3.clone()
corner_shape4.reflect(cross_rectangle.bbox_center())
# A teljes keresztvas grafikát a keresztvas téglalap és a sarokelemek együtteseként állítjuk elő.
cross_guard = Group(cross_rectangle, corner_shape1, corner_shape2, corner_shape3, corner_shape4)

# BANDZSOLT MARKOLAT ÉS VÉGSÚLY LÉTREHOZÁS.
grip_width, grip_length = blade_width * 0.8, 100  # A markolat szélessége és hossza.
# A markolaton körbetekert bandázst elolt ellipszisekkel jelenítjük meg.
grip_wrapping_shapes = [Ellipse(cnv, grip_width / 2, grip_width / 4, fill='brown3') for _ in range(20)]
for i, grip_wrap in enumerate(grip_wrapping_shapes):
    grip_wrap.move(0, grip_width / 8 * i)
# A markolat nyakát, amely a pengéhez köti trapéz formával ábrázoljuk.
grip_neck = Trapezoid(cnv, (-grip_width / 2, 0), (+grip_width / 2, 0), (-blade_width / 2, 10), (+blade_width / 2, 10),
                      fill='black')
# A bandázs grafikák és a markolatnyak egy csoportba fogásával előállítjuk a markolat grafikát.
grip_wrappings = Group(*grip_wrapping_shapes)
grip_neck.move(0, grip_wrappings.bbox()[-1] - grip_width / 4)
grip = Group(*grip_wrappings, grip_neck)

# A végsúly létrehozása.
pommel = Circle(cnv, grip_width / 2, fill='green')  # A markolat végén elehelyzkedő végsúlyt egy körrel ábrázoljuk.
pommel.move(0, -blade_width / 2)  # A végsúlyt a markolat végére helyezzük.
grip_and_pommel = Group(*grip, pommel)  # A markolat és végsúly együtteséből álló grafika.

# A KARDRÉSZEKBŐL A TELJES KARD ÖSSZEÁLLÍTÁSA.
grip_and_pommel.move(canvas_width / 2 - grip_and_pommel.bbox_center()[0],
                     canvas_height / 2 - grip_and_pommel.bbox_center()[1])
x1, y1, x2, y2 = grip_and_pommel.bbox()
grip_and_pommel.move(0, -(y2 - y1) / 2 - guard_height / 2 + 3)
blade.move(canvas_width / 2, canvas_height / 2)
cross_guard.move(canvas_width / 2 - cross_guard.bbox_center()[0], canvas_height / 2 - cross_guard.bbox_center()[1])
sword = Group(*blade, *cross_guard, *grip_and_pommel)

# AZ ELKÉSZÜLT KARD GRAFIKA KÖZÉPRE HELYEZÉSE, FELNAGYÍTÁSA ÉS ELFORGATÁSA.
sword.move(0, canvas_height / 2 - sword.bbox_center()[1])
sword.scale(*sword.bbox_center(), 1.5, 1.5)
sword.rotate(45, sword.bbox_center())
#
sword2 = sword.clone()
sword2.rotate(-90, sword2.bbox_center())

root.mainloop()
