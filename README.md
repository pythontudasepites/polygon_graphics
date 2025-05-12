# Grafikák készítése objektumokba foglalt, sokszögből előállított síkidomokkal

A *tkinter* vászon (*Canvas*) grafikus elemén alapban megjeleníthető rajzelemek többsége (ellipszis, ellipszisív és téglalap) nem forgatható el alaktartóan, vagyis a forgatás után torzulnak, és az ellipszis tengelyei, valamint a téglalap oldalai továbbra is a vízszintes és függőleges koordináta-tengelyekkel lesznek párhuzamosak. 

Ha alaktartó forgatást szeretnénk, akkor azt csak úgy érhetjük el, hogy az említett síkidomokat egy-egy sokszöggel valósítjuk meg, mert ha egy sokszög minden csúcspontjára alkalmazzuk a forgatást, akkor maga a sokszög alaktartóan fog elfordulni az adott forgáspont körül. Ha tehát tudjuk, hogy hogyan kell egy pontot forgatni, akkor ezen ismeretek birtokában megnyílik az út ellipszis, ellipszisív és téglalap forgatására is. Ennek egy lehetséges megoldása, ha a *Canvas* osztályt specializáljuk egy olyan alosztállyal, amely képes olyan ellipszist, ellipszisívet és téglalapot előállítani, amelyeket alaktartóan lehet forgatni egy adott pont körül. Ha azonban nem csak e három síkidomot kívánjuk forgathatóvá tenni, hanem másokat is, akkor minden ilyenhez egy új létrehozó metódust kell definiálni a specializált *Canvas* alosztályban. Ez azonban nem igazán jó megközelítés, mert vagy az alosztályt kell módosítani minden új síkidomhoz, ami a nyitott-zárt elvet (open-closed principle) sérti, vagy ezt elkerülendő mindig egy új alosztályt kell létrehozni, aminek szintén vannak hátrányai (pl. áttekinthetőség és karbantarthatóság csökkenése; az öröklési hierarchia változtatással szembeni sérülékenysége; a kliens kód esetleges módosítási szükségessége.)

Mindezek miatt egy másik megközelítés alkalmazunk. 

Az elv az, hogy számbavesszük, hogy egy vászon grafikus elemen megjelenített sokszöggel megvalósított síkidomokhoz milyen számunkra fontos, általános, vagyis minden síkidomra értelmezhető műveletek rendelhetők. Ezeket egy közös alaposztályba szervezzük, aminek neve legyen **PolygonGraphics**. Ezen osztály metódusaiként definiáljuk tehát például
-	a geometriai transzformációkat (pl. forgatás, tükrözés, eltolás, áthelyezés, átméretezés),
-	a grafika befoglaló téglalapja ellentétes sarokpontjainak meghatározását, és e téglalap középpontjának meghatározását,
-	a sokszög csúcspontjainak középpontjának (súlypontjának) meghatározását,
-	a sokszög oldalhosszainak kikérését,
-	a sokszög csúcspontjainak kikérését és megváltoztatását,
-	a sokszög egy adott, vagy minden konfigurációs paramétere értékének kinyerését,
-	a sokszög konfigurációs jellemzőinek (pl. kitöltőszín, körvonalszín, körvonal vastagság) beállíthatóságát,
-	címkék (tag-ek) hozzárendelését, törlését, lekérdezését,
-	események és eseménykezelők hozzárendelését és törlését

A felsorolt metódusok működéséhez szükséges néhány privát segédmetódus. Mivel a *Canvas* *create_polygon()* metódus a csúcspontokat azok felsorolási sorrendjében köti összekötése, ezért kell egy metódus, amely a sokszög csúcspontjait, azok koordinátáit a megfelelő sorrendbe rendezi, hogy azokat így átadva a *create_polygon()* metódusnak a sokszög keresztező vonalak nélkül legyen kirajzolva. Egy másik segédmetódus azt teszi lehetővé, hogy a csúcspontokat rugalmasan lehessen megadni, vagyis akár az x, y koordináták közvetlen felsorolásával, akár két elemet szolgáltató iterálható objektumok sorozataként.  E segédmetódus az x és y koordinátákat fogja kiadni egymás után függetlenül attól, hogy a pontok milyen formában lettek megadva. De ilyen segédmetódus lehet egy ellipszis pontjait adott szögtartományban szolgáltató is, ami egyéni síkidomok megalkotásakor könnyítheti a munkát.

Az egyes, sokszöggel megvalósított síkidomokat egy-egy osztályban definiáljuk, amelyek öröklik a **PolygonGraphics** osztályt, vagyis a konkrét síkidomosztályok a **PolygonGraphics** alosztályai lesznek. Ha így teszünk, akkor az egyes síkidomosztályok szerkezete egyszerű lesz, mert kötelezően csak egy olyan metódust kell tartalmazni, ami a síkidom grafikát létrehozza sokszögből a *Canvas* osztály *create_polygon()* metódusának hívásával vagy egy már létező sokszög felhasználásával. A kötelezően implementálandó metódusnak azonos neve lehet minden alosztályban, ami legyen most **_create_graphics()**. Mivel a grafika létrehozás és kirajzolás minden síkidom esetén egy kötelezően megvalósítandó feladat, ezért a **_create_graphics()** meghívását betehetjük a **PolygonGraphics** szülőosztályba, konkrétan annak *\__init__* metódusába. Ezzel párhuzamosan a **PolygonGraphics** osztályban definiálunk egy absztrakt **_create_graphics()** metódust, ami kikényszeríti az alosztályokban történő implementálást. Ezzel a **PolygonGraphics** osztály absztrakt osztály lesz, ezért az *abc* modul *ABC* osztályát örökölnie kell. 

A grafika létrehozás és kirajzolás természetesen egy adott *Canvas* példányon történik, ezért mind a PolygonGraphics mind alosztályai konstruktora kell, hogy egy *Canvas* példányt fogadjon. És ugyanezen okból mind a PolygonGraphics mind alosztályai konstruktorában lehetőséget kell biztosítani kulcsszavas argumentumokkal, hogy a sokszög konfigurációját meg lehessen adni.

Ezeken felül a konkrét síkidomokat megvalósító alosztályok konstruktorában kell megadni a sokszög csúcspontjait is olyan síkidomoknál, ahol a síkidom maga ténylegesen sokszög. Ott, ahol ez releváns lehet, az ilyen síkidom geometriai meghatározására alternatív módot is lehet biztosítani egy-egy osztálymetódussal. Így például a téglalap és négyzet esetén az osztálymetódus a csúcspont-koordináták helyett az oldalhosszakat és a kezdeti pozíció koordinátáit fogadhatja. Bármilyen geometriai adatokkal is határozzuk is meg a síkidomokat a példányosító osztálymetódusokban, követelmény, hogy a *Canvas* példányt és a sokszög konfigurációját is meg lehessen adni.

Az olyan síkidomok esetén, amelyek nem sokszögek, hanem csak sokszögeket használunk a közelítésükre (pl. ellipszis vagy kör) az implementáló osztály konstruktora természetesen a csúcspontok helyett más adatot fog fogadni. Például kör esetén ezek lehetnek a sugárhossz és a középpont.

Hasznos művelet még egy síkidom másolása, klónozása. Mivel ez minden síkidom esetén elvégezhető, ezért a **PolygonGraphics** szülőosztályban definiáljuk **clone()** néven. Az egyetlen gond, hogy e metódus által visszaadott új példányt az adott konkrét síkidomtól függően más-más módon kell előállítani. Ezt a problémát úgy oldjuk fel, hogy egy **_instance_factory()** nevű közös absztrakt példánylétrehozó metódust definiálunk a **PolygonGraphics** osztályban, amit a **clone()** meghív. Mivel az **_instance_factory()** absztrakt, ezért azt kötelező minden konkrét síkidomosztálynak implementálnia a sajátosságainak megfelelően. Ez azonban nem bonyolult, többnyire egy egyszerű konstruktorhívás lesz.

Az eddig ismertetett metódusokon felül igény szerint mások is definiálhatók, legyenek azok általánosak, mint például a terület és kerület, vagy síkidomspecifikusak mint például háromszög esetén annak nevezetes pontjait meghatározók.

A grafikák előállításának lehetőségeit nagymértékben bővíti, ha az egyes síkidomokat csoportba tudjuk foglalni, és a különféle műveleteket (pl. forgatást, tükrözést, áthelyezést) a csoport egészére tudjuk végezni. Ezt egy Group nevű osztállyal valósítjuk meg. Mivel ez nem grafikákat hoz létre, hanem meglévő grafikus objektumokat tárol és ezen végez műveleteket, ezért ennek konstruktora csak a csoportba foglalni kívánt PolygonGraphics típusú objektumokat kell, hogy fogadja, a Canvas példányt és a konfigurációs értékeket nem. Ami a metódusokat illeti, a a tartalmazásvizsgálaton, iterálhatóságon és igazságérték meghatározásán, valamint a csoporthoz adás és abból való eltávolítás műveletén felül a **PolygonGraphics** metódusai közül azokat valósítjuk meg, amelyek csoportra értelmezhetők.

A fenti elvek alapján elkészített PolygonGraphics és **Group** osztály definícióját a fundamental_classes nevű modul tartalmazza. A modulnév utal arra, hogy ezek az alapvető osztályok a sokszögekkel megvalósított síkidomokkal készítendő grafikákákhoz.

A *shapes* mappában találhatók a konkrét síkidomok definíciói. A *quadrilaterals* modulba vannak foglalva a négyszögek (deltoid, trapéz, paralelogramma, rombusz, téglalap, négyzet) alosztályai. Az ellipszis és kör, a háromszög, valamint egy egyéni tervezésű alakzat osztálya külön modulokban vannak definiálva. 
A működéshez Python 12+ verzió szükséges.

## Alkalmazási példák

Két alkalmazási példát mutatunk ezen osztályok használatára. Ezek programkódja az *application_examples* mappában található. Az egyik két, keresztező kardot rajzol ki, a másik egy absztrakt alkotás, ami felülnézetben lehet akár egy park a közepén szökőkúttal, vagy akár egy futópálya. Ezek képe látható alább. Mindenesetre a cél mindkét esetben a lehetőségek bemutatása.

A *demo_application1* képernyőképe:
![demo_app1_screenshot.png](images%2Fdemo_app1_screenshot.png)

A *demo_application1* képernyőképe:
![demo_app2_screenshot.png](images%2Fdemo_app2_screenshot.png)
