# Python 3.12+
import cmath
import contextlib
import tkinter as tk
from abc import ABC, abstractmethod
from itertools import count, batched, starmap, pairwise
from statistics import mean
from typing import Iterable, Self, Annotated, Generator, Callable
from math import radians, cos, sin, dist, atan2, isclose

type PointType = tuple[int | float, int | float]

type AngleDegree = Annotated[int | float, 'szögérték fokban']


class PolygonGraphics(ABC):
    """Absztrakt alaposztály, amelyet a sokszögekből kialakított síkidom konkrét osztályának örökölni kell."""

    _instance_counter = count(1)  # Az azonosítócímke létrehozásához használt, példányonkénti egyedi szám generátor.

    def __init__(self, canvas: tk.Canvas, **options):
        self.canvas = canvas
        # Az új síkidompéldány azonosítócímkéjének előállítása a típusnév és egyedi szám kombinációjával.
        self.id_tag: str = type(self).__name__ + str(next(self._instance_counter))
        # A grafika létrehozása.
        self._create_graphics()
        # Alapértelmezésben az alakzat nincs kitöltve, csak a körvonal látszik.
        self.config(fill='', outline='black', width=1)
        self.config(**options)  # A megadott konfigurációs beállítások érvényesítése.

    @abstractmethod
    def _create_graphics(self) -> None:
        """A sokszögekből kialakított síkidom konkrét osztályában implementálandó metódus, amely a
        síkidom grafikát létrehozza sokszögből a Canvas create_polygon(self.id_tag,...) metódus hívásával
        vagy egy már létező sokszög felhasználásával.
        """
        raise NotImplementedError

    @abstractmethod
    def _instance_factory(self) -> Self:
        """A sokszögekből kialakított síkidom konkrét osztályában implementálandó metódus, amely
        e konkrét osztály konstruktorával előállított új példánnyal tér vissza.
        """
        raise NotImplementedError

    def clone(self) -> Self:
        """A konkrét síkidom olyan új példányával tér vissza, amely konfigurációs jellemzői
        megegyeznek az eredeti példányéval.
        """
        new_inst = self._instance_factory()  # Az új konkrét példány létrehozása.
        new_inst.config(**self.all_cget())  # Az új példány konfigurációjának beállítása az eredetivel megegyezően.
        new_inst.dtag(self.id_tag)  # Az eredeti példány azonosítócímkéjének eltávolítása az új példányról.
        new_inst.set_coords(self.get_coords())  # Az új példány csúcspontjainak beállítása az eredetivel megegyezően.
        return new_inst

    def _flatten_xycoords(self, coords: Iterable):
        """Az x és y koordinátákat adja vissza egymás után függetlenül attól, hogy azokat az argumentum
        közvetlenül szolgáltatja, vagy iterálható objektumból származnak.
        Pl. coords elemei x1, y1, x2, y2 -> kimenet: x1, y1, x2, y2
        coords elemei (x1, y1), [x2, y2] -> kimenet: x1, y1, x2, y2
        """
        for coord in coords:
            try:
                iter(coords)
                if isinstance(coord, (str, bytes, bytearray)):
                    raise TypeError
                yield from self._flatten_xycoords(coord)
            except TypeError:
                if isinstance(coord, (int, float)):
                    yield coord
                else:
                    raise TypeError('A koordináták csak valós számok lehetnek.')

    def vertices_centroid(self, *vertices: Iterable) -> tuple[int | float, int | float]:
        """A megadott csúcspontok középpontját (súlypontját) adja vissza."""
        xy_coordinates = list(self._flatten_xycoords(vertices))  # A kapott lista: [x1, y1, x2, y2, ..., xn, yn]
        # Kinyerjük az x koordináták sorozatát és az y koordináták sorozatát.
        x_coords, y_coords = xy_coordinates[::2], xy_coordinates[1::2]
        # Meghatározzuk a csúcspontok középpontját (súlypontját), ami mint az a geometriából ismert, a
        # csúcspontok számtani közepe.
        center_x, center_y = mean(x_coords), mean(y_coords)
        return center_x, center_y

    def _sort_vertices_for_proper_plotting(self, *vertices) -> tuple[PointType, ...]:
        """Bármilyen sorrendben vannak a kirajzolandó sokszög csúcspontjai megadva, a visszatérési érték a
        csúcspontok olyan sorozata lesz, amellyel a sokszög megfelelően, azaz keresztező vonalak nélkül lesz
        megjelenítve.
        A csúcspontokat az x, y koordináták egymást követő felsorolsával, vagy az x, y párokat szolgáltató
        iterálható objektumok felsorolásával lehet megadni.
        """
        # Meghatározzuk a csúcspontok középpontját (súlypontját)
        center_x, center_y = self.vertices_centroid(vertices)
        xy_coordinates = list(self._flatten_xycoords(vertices))  # A kapott lista: [x1, y1, x2, y2, ..., xn, yn]
        # Kiszámítjuk az egyes csúcspontok középponttól vett szögét.
        vertices_angles = {(x, y): atan2(x - center_x, y - center_y) for x, y in batched(xy_coordinates, 2)}
        # A csúcspontokat a szögeik szerint rendezzük.
        sorted_vertices_angles = sorted(vertices_angles.items(), key=lambda t: t[1])
        # A rendezett csúcspontokkal térünk vissza.
        return tuple(point for point, angle in sorted_vertices_angles)

    @staticmethod
    def _all_equal(*numbers: int | float, relative_tolerance=1e-9) -> bool:
        """True értéket ad vissza, ha az összes argumentum egyenlő az adott relatív tolerancián belül."""
        # Azt, hogy minden érték egyenlő, úgy határozzuk meg, hogy kihasználjuk az egyenlőségi reláció
        # tranzitivitását: ha n1==n2 és n1==n3, akkor ebből következik, hogy n2==n3.
        return all(isclose(numbers[0], number, rel_tol=relative_tolerance) for number in numbers[1:])

    def side_lengths(self, *vertices: Iterable) -> list[float]:
        """A csúcspontok által meghatározott sokszög oldalhosszainak listáját adja vissza."""
        sorted_points = self._sort_vertices_for_proper_plotting(vertices)
        # Ahhoz, hogy a sokszög csúcspontpárokból számolt oldalhosszai között a sorban utolsó oldal is
        # szerepeljen, az első csúcspontot a sorozat végén, utolsóként fel kell venni.
        return [dist(p1, p2) for p1, p2 in pairwise([*sorted_points, sorted_points[0]])]

    def config(self, **options) -> None:
        """A sokszöggel megvalósított síkidom jellemzőit állítja be a kulcsszavas argumentumokkal.
        A konfigurációs opciók megegyeznek a vászon (Canvas) sokszög rajzelemére beállíthatókkal.
        """
        # Ha az argumentum a "tags" opciót is meghatározza, akkor gondoskodni kell arról, hogy
        # az azonosítócímke ne vesszen el.
        tgs = options.get('tags', '')
        if tgs:
            if isinstance(tgs, (tuple, list)):
                tags_string = ' '.join((*tgs, self.id_tag))
            elif isinstance(tgs, str):
                tags_string = ' '.join((tgs, self.id_tag))
            else:
                raise ValueError('A "tags" konfigurációs paraméter értéke string vagy string sorozat lehet')
            options['tags'] = tags_string

        self.canvas.itemconfig(self.id_tag, **options)

    configure = config

    def cget(self, option: str) -> str:
        """A sokszög option által megadott konfigurációs paraméterének aktuális értékével tér vissza."""
        return self.canvas.itemcget(self.id_tag, option)

    config_option_value = cget

    def all_cget(self) -> dict:
        """A sokszög összes konfigurációs paraméterét és aktuális értékét adja vissza."""
        return {k: v[-1] for k, v in self.canvas.itemconfigure(self.id_tag).items()}

    all_config_options = all_cget

    def get_coords(self) -> list[float]:
        """A sokszög pontjainak x, y koordinátáit adja vissza egy listában."""
        return self.canvas.coords(self.id_tag)

    def set_coords(self, *vertices) -> None:
        """A sokszög pointjait a megadottakra változtatja."""
        self.canvas.coords(self.id_tag, *self._flatten_xycoords(vertices))

    def gettags(self) -> tuple[str, ...]:
        """A sokszöghöz rendelt tag-eket adja vissza."""
        return self.canvas.gettags(self.id_tag)

    def add_tag(self, new_tag: str) -> None:
        """A megadott tag-et hozzárendeli a sokszöghöz."""
        self.canvas.addtag_withtag(new_tag, self.id_tag)

    def dtag(self, tag_to_delete: str) -> None:
        """A megadott tag-et eltávolítja a sokszögről. Az azonosítócímkét nem lehet törölni."""
        if tag_to_delete != self.id_tag:
            self.canvas.dtag(self.id_tag, tag_to_delete)

    delete_tag = dtag

    def bind(self, event_pattern_sequence: str | None = None,
             func: Callable[[tk.Event], None] | None = None, add: bool | None = None) -> str:
        """Az első argumentummal meghatározott eseményt vagy eseménysorozatot és eseménykezelőt
        társítja a sokszöghöz.
        Ha az add True igazságértékű objektum, akkor a func függvény a korábban hozzárendelt más
        eseménykezelők lefutása után lesz meghívva, egyébként az eseményre csak a func lesz végrehajtva.
        A metódus visszatérési értéke egy azonosítő, ami lehetővé teszi a func eseménykezelő
        törlését a unbind() metódussal.
        """
        return self.canvas.tag_bind(self.id_tag, event_pattern_sequence, func, add)

    def unbind(self, event_pattern_sequence: str, func_id: str | None = None) -> None:
        """Az első argumentummal meghatározott eseményhez vagy eseménysorozathoz kötött, és a funcid értékével
        azonosított eseménykezelőt eltávolítja.
        """
        self.canvas.tag_unbind(self.id_tag, event_pattern_sequence, func_id)

    def bbox(self) -> tuple[int, int, int, int]:
        """A sokszög befoglaló téglalapja bal felső és jobb alsó sarokpontjának koordinátáival tér vissza."""
        return self.canvas.bbox(self.id_tag)

    def bbox_center(self) -> tuple[int | float, int | float]:
        """A sokszög befoglaló téglalapja középpontjának koordinátáival tér vissza."""
        x1, y1, x2, y2 = self.bbox()
        return (x1 + x2) / 2, (y1 + y2) / 2

    def move(self, dx, dy) -> None:
        """A sokszöget az x tengely irányában dx, az y tengely irányában dy értékkel tolja el."""
        self.canvas.move(self.id_tag, dx, dy)

    def moveto(self, x, y) -> None:
        """A sokszöget áthelyezi olyan módon, hogy befoglaló téglalapjának bal felső pontja
        az x, y koordinátákkal megadott ponton legyen.
        """
        self.canvas.moveto(self.id_tag, x, y)

    def scale(self, ref_x, ref_y, scalefactor_x, scalefactor_y) -> None:
        """A sokszöget átméretezi az első két argumentummal meghatározott referenciaponthoz képest.
        A sokszög minden pontja x koordinátájának referenciaponttól vett távolsága szorzódik a scalefactor_x valós számmal,
        az y koordinátájának referenciaponttól vett távolsága pedig az scalefactor_y valós számmal.
        """
        self.canvas.scale(self.id_tag, ref_x, ref_y, scalefactor_x, scalefactor_y)

    def rotate(self, angle: int | float, center_of_rotation: PointType = (0, 0), in_degrees=True) -> None:
        """A sokszöget, annak minden pontját angle szöggel forgatja el a második argumentummal megadott
        forgáspont körül. Ha az utolsó paraméter értéke True akkor a szög fokokban értendő, False esetén radiánban.
        """
        cor = complex(*center_of_rotation)
        points_to_rotate: Iterable[complex] = starmap(complex, batched(self.canvas.coords(self.id_tag), 2))
        rotated_complex_points: Iterable[complex] = (cmath.exp(1j * (radians(angle) if in_degrees else angle)) * (point - cor) + cor
                                                     for point in points_to_rotate)
        rotated_points: Iterable[tuple[float, float]] = ((c.real, c.imag) for c in rotated_complex_points)
        self.canvas.coords(self.id_tag, *rotated_points)

    def reflect(self, *one_or_two_points) -> None:
        """A grafikát középpontosan vagy tengelyesen tükrözi.
        Ha az argumentum egy pontot határoz meg, akkor erre a pontra vonatkozó tükrözést végez.
        Ha az argumentum két pontot határoz meg, akkor a két ponttal jellemzett egyenesre
        vonatkozó tengelyes tükrözést hajt végre.
        A pontokat meg lehet adni vagy az x, y koordinták felsorolásával, vagy olyan iterálható objektumok
        sorozatával, amelyek az x és y koordintát szolgáltatják. Pl.: x1, y1, x2, y2 vagy (x1, y1), (x2, y2)
        """
        xy_coords: tuple = tuple(self._flatten_xycoords(one_or_two_points))
        if all(isinstance(e, (int, float)) for e in xy_coords):
            if len(xy_coords) == 2:
                self._reflect_across_a_point(*xy_coords)
            elif len(xy_coords) == 4:
                self._reflect_across_a_line(*xy_coords)
            return
        raise ValueError('Tükrözésehez egy vagy két pontot kell megadni.')

    def _reflect_across_a_point(self, x, y) -> None:
        """Középpontos tükrözést végez az x, y koordinátákkal megadott pontra vonatkozóan."""
        self.rotate(180, (x, y))

    @staticmethod
    def _reflect_point_across_line_complex(x, y, x1, y1, x2, y2) -> tuple[float, float]:
        """A megadott x, y pontnak az x1, y1 és x2, y2 pontok által meghatározott tengelyre vett tükörkép pontjával tér vissza.
        """
        # A tükörpont meghatározása komplex számokkal való műveletekkel valósul meg.
        pc, p1c, p2c = complex(x, y), complex(x1, y1), complex(x2, y2)
        psi = (pc - p1c).conjugate()
        psir = psi * (p2c - p1c) / (p2c - p1c).conjugate()
        p_reflected = psir + p1c
        return p_reflected.real, p_reflected.imag

    def _reflect_across_a_line(self, x1, y1, x2, y2) -> None:
        """Az alakzatot az x1, y1 és x2, y2 pontok által meghatározott tengelyre vonatkozóan tükrözi."""
        points_to_reflect = batched(self.canvas.coords(self.id_tag), 2)
        reflected_points = (self._reflect_point_across_line_complex(*p, x1, y1, x2, y2) for p in points_to_reflect)
        self.canvas.coords(self.id_tag, *reflected_points)

    @staticmethod
    def ellipse_arc_points(semi_major_axis: int | float, semi_minor_axis: int | float,
                           center_x: int | float, center_y: int | float,
                           start_angle: AngleDegree = 0, stop_angle: AngleDegree = 360,
                           number_of_points: int | None = None) -> Generator[tuple[int | float, int | float], None, None]:
        """Egy olyan generátorobjektummal tér vissza, amely egy nagy és kis féltengelyével és középppontjával
        megadott ellipszis megadható számú pontjait szolgáltatja egy kezdő és végszöggel meghatározható szögtartományban.
        """
        if semi_major_axis < 0 or semi_minor_axis < 0:
            raise ValueError('Az ellipszis féltengelyeinek hossza vagy a kör sugara nemnegatív szám kell, hogy legyen.')
        if stop_angle < start_angle:
            raise ValueError('Az induló szög nem lehet nagyobb a végszögnél.')

        if number_of_points is None:
            # 1000 pixel hosszú fél nagytengelynél 360 fok felosztása elég 600 pontban. Rövidebb esetben vagy kisebb szögnél
            # arányosan kevesebb pont kell, de egy adott pontszámnál nem lehet kevesebb az ábrázolhatósághoz.
            n1, n2 = 800 * semi_major_axis / 1000 + 64, (stop_angle - start_angle) / 360
            number_of_points = int(round(n1 * n2, 0))

        angle_increment = (stop_angle - start_angle) / number_of_points
        # A pontok koordinátáit az ellipszis paraméteres egyenletrendszere alapján határozzuk meg.
        return ((semi_major_axis * cos(radians(alpha)) + center_x, semi_minor_axis * sin(radians(alpha)) + center_y)
                for alpha in (start_angle + angle_increment * i for i in range(number_of_points)))


class Group:
    """Olyan iterálható konténerobjektum, amely csoportba foglalja a megadott, sokszögből
    előállított grafikaobjektumokat.
    A csoportba foglalással a grafikaobjektumok együttesen mint egyetlen grafika kezelhetők
    bizonyos műveletekhez (pl. áthelyezés, forgatás, tükrözés).
    """
    _instance_counter = count(1)  # Az azonosítócímke létrehozásához használt, példányonkénti egyedi szám generátor.

    def __init__(self, *polygon_graphics_objects: PolygonGraphics):
        self._id_tag: str = type(self).__name__ + str(next(self._instance_counter))
        self.graphics_objects: list[PolygonGraphics] = []
        self.add_graphics(*polygon_graphics_objects)

    def __contains__(self, polygon_graphics_object: PolygonGraphics) -> bool:
        return polygon_graphics_object in self.graphics_objects

    def __bool__(self) -> bool:
        return bool(self.graphics_objects)

    def __iter__(self):
        return iter(self.graphics_objects)

    def add_graphics(self, *polygon_graphics_objects: PolygonGraphics):
        """Grafikaobjektumok hozzáadása a csoporthoz."""
        self.graphics_objects.extend(polygon_graphics_objects)
        for g in self.graphics_objects:
            g.add_tag(self._id_tag)  # A grafikaobjektumokat ellátjuk a csoport azonosító címkéjével.

    def remove_graphics(self, *polygon_graphics_objects: PolygonGraphics):
        """Grafikaobjektumok eltávolítása a csoportból."""
        for g in polygon_graphics_objects:
            g.dtag(self._id_tag)  # Az eltávolítandó grafikaobjektumokról töröljük a csoport azonosító címkéjét.
            # A grafikaobjektumot eltávolítjuk a csoport konténeréből. Ha eleve nincs benne, akkor nem történik semmi.
            with contextlib.suppress(ValueError):
                self.graphics_objects.remove(g)

    def _get_canvas(self) -> tk.Canvas:
        """A csoportba fogalalt grafikákhoz tartozó vászon elemmel tér vissza, vagy
        hibaüzenettel, ha a csoport üres.
        """
        try:
            return list(self.graphics_objects)[0].canvas
        except IndexError:
            raise ValueError('A csoport nem tartalmaz grafikát')

    def bind(self, event_pattern_sequence: str | None = None,
             func: Callable[[tk.Event], None] | None = None, add: bool | None = None) -> str:
        """Az első argumentummal meghatározott eseményt vagy eseménysorozatot és eseménykezelőt
        társítja a csoportgrafikához.
        Ha az add True igazságértékű objektum, akkor a func függvény a korábban hozzárendelt más
        eseménykezelők lefutása után lesz meghívva, egyébként az eseményre csak a func lesz végrehajtva.
        A metódus visszatérési értéke egy azonosítő, ami lehetővé teszi a func eseménykezelő törlését
        az unbind() metódussal.
        """
        return self._get_canvas().tag_bind(self._id_tag, event_pattern_sequence, func, add)

    def unbind(self, event_pattern_sequence: str, func_id: str | None = None):
        """Az első argumentummal meghatározott eseményhez vagy eseménysorozathoz kötött, és a funcid értékével
        azonosított eseménykezelőt eltávolítja.
        """
        self._get_canvas().tag_unbind(self._id_tag, event_pattern_sequence, func_id)

    def bbox(self) -> tuple[int, int, int, int]:
        """A teljes csoportgrafika befoglaló téglalapja bal felső és jobb alsó sarokpontjának
        koordinátáival tér vissza.
        """
        return self._get_canvas().bbox(self._id_tag)

    def bbox_center(self) -> tuple[int | float, int | float]:
        """A teljes csoportgrafika befoglaló téglalapja középpontjának koordinátáival tér vissza."""
        x1, y1, x2, y2 = self.bbox()
        return (x1 + x2) / 2, (y1 + y2) / 2

    def move(self, dx, dy) -> None:
        """A teljes csoportgrafikát az x tengely irányában dx, az y tengely irányában dy értékkel tolja el."""
        self._get_canvas().move(self._id_tag, dx, dy)

    def moveto(self, x, y) -> None:
        """A teljes csoportgrafikát áthelyezi olyan módon, hogy befoglaló téglalapjának bal felső pontja
        az x, y koordinátákkal megadott ponton legyen.
        """
        self._get_canvas().moveto(self._id_tag, x, y)

    def scale(self, x_origin, y_origin, scalefactor_x, scalefactor_y) -> None:
        """A teljes csoportgrafikát átméretezi az első két argumentummal meghatározott referenciaponthoz képest.
        A sokszögek minden pontja x koordinátájának referenciaponttól vett távolsága szorzódik a scalefactor_x
        valós számmal, az y koordinátájának referenciaponttól vett távolsága pedig az scalefactor_y valós számmal.
        """
        self._get_canvas().scale(self._id_tag, x_origin, y_origin, scalefactor_x, scalefactor_y)

    def rotate(self, angle: int | float, center_of_rotation: PointType = (0, 0), in_degrees=True) -> None:
        """A teljes csoportgrafikát az angle szöggel elforgatja a második argumentummal megadott forgáspont
        körül. Ha az utolsó paraméter értéke True akkor a szög fokokban értendő, False esetén radiánban.
        """
        for g in self.graphics_objects:
            g.rotate(angle, center_of_rotation, in_degrees)

    def reflect(self, *one_or_two_points) -> None:
        """A teljes csoportgrafikát középpontosan vagy tengelyesen tükrözi.
        Ha az argumentum egy pontot határoz meg, akkor erre a pontra vonatkozó tükrözést végez.
        Ha az argumentum két pontot határoz meg, akkor a két ponttal jellemzett egyenesre
        vonatkozó tengelyes tükrözést hajt végre.
        A pontokat meg lehet adni vagy az x, y koordinták felsorolásával, vagy olyan iterálható objektumok
        sorozatával, amelyek az x és y koordintát szolgáltatják. Pl.: x1, y1, x2, y2 vagy (x1, y1), (x2, y2)
        """
        for g in self.graphics_objects:
            g.reflect(*one_or_two_points)

    def clone(self) -> Self:
        """Olyan új csoporttal tér vissza, amelyben új grafikaobjektumok vannak, de az eredeti csoportban
         foglaltakal megegyező jellemzőkkel.
         """
        return type(self)(*[g.clone() for g in self.graphics_objects])
