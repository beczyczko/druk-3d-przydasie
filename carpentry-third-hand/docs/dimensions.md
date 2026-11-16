# Wymiary i bazy funkcjonalne

Wszystkie wartości są w milimetrach. Tabela przedstawia założenia projektowe oraz wymiary funkcjonalne poszczególnych wariantów.

| Parametr efektywny | A standard | B reinforced | C compact |
|---|---:|---:|---:|
| Nominalna płyta `board_thickness` | 18 | 18 | 18 |
| Całkowity dodatek `clearance` | 0,3 | 0,3 | 0,3 |
| Szczeliny na prostych odcinkach | 18,3 | 18,3 | 18,3 |
| Długość ramienia `arm_length` | 70 | 72 | 52 |
| Szerokość poprzeczki TL | 140 | 144 | 104 |
| Ścianka `wall_thickness` | 5 | 6 | 4,4 |
| Mostek `base_thickness` | 3,6 | 4,8 | 3,2 |
| Głębokość chwytu `body_height` nad mostkiem | 24 | 28 | 20 |
| Całkowite Z `guide_height` | 58 | 62 | 52 |
| Zasięg trójkątnych wzmocnień `reinforcement_size` | 11 | 17 | 7 |
| Dodatkowy występ żebra wieży na zewnątrz | 0 | 2,4 | 0 |
| Zewnętrzny promień głównego obrysu `corner_radius` | 3 | 3 | 3 |
| Szerokość wieży TL / każdego boku LL | 18 | 18,65 | 18 |
| Faza wlotu szczeliny, 45° | 0,6 | 0,6 | 0,6 |
| Okrąg nominalny otworu pomocniczego | 6,65 | 6,65 | 6,65 |
| Rozstaw osi otworów | 15 | 15 | 15 |
| Odsunięcie pierwszej osi od mostka | 10 | 10 | 10 |

Szerokość wieży jest automatyczna: `max(board_thickness, guide_hole_diameter + 2*wall_thickness)`. Wartości `0` dla długości, grubości i wysokości w konfiguracji wybierają domyślną wartość wariantu. Ustaw liczbę dodatnią, aby ją nadpisać. `corner_radius`, `lead_in`, średnica i rozstaw są bezpośrednie.

## Osie i rzeczywiste połączenie płyt

W źródłach mostek leży od Z=0 do Z=b. Płyty mają odsłonięte krawędzie w Z=b i rozciągają się ku +Z; w użytkowaniu całość odwraca się mostkiem do góry. `demo.scad` wykonuje ten obrót, nie zmieniając dopasowania.

Przy oznaczeniach `t=18`, `s=t+clearance`, `a=arm_length`:

| Typ | Pierwsza płyta A | Druga płyta B | Bazy narzędzia |
|---|---|---|---|
| TL | X przez całą poprzeczkę, Y=0…t | X=−t/2…t/2, Y zaczyna się w t | Y=0 dla A; X=−t/2 dla B |
| LL | X od 0 wzdłuż ramienia, Y=0…t | X=0…t, Y zaczyna się w t | Y=0 dla A; X=0 dla B |

Płyta B styka się czołem z A w Y=t. Nie ma sztucznej przerwy między płytami ani ich przenikania. Dodatkowe miejsce w szczelinie znajduje się po stronie przeciwnej do bazy; nie dodaje się połowy luzu do każdej nominalnej grubości.

Mostek bazuje na krawędziach obu płyt. Wspólne płaszczyzny boczne mają dokładny kąt 90° w modelu. Przy dodatnim luzie płytę trzeba dosunąć do bazy. Narzędzie nie wymusza zerowej odchyłki kąta bez docisku. Na krótszej próbce luz daje większą swobodę obrotu niż na całym ramieniu.

## Gabaryty i stoły

| Model | X × Y × Z | Obrys jednego stołu | Najmniejszy margines stołu |
|---|---|---|---:|
| TL / LL A | 140 × 75 × 58 / 75 × 75 × 58 | 158 × 158 | 11 |
| TL / LL B | 144 × 80,4 × 62 / 80,4 × 80,4 × 62 | 168,8 × 168,8 | 5,6 |
| TL / LL C | 104 × 56,4 × 52 / 56,4 × 56,4 × 52 | 120,8 × 120,8 | 29,6 |

Każdy stół zawiera 1 TL + 2 LL; dwa stoły tworzą zestaw 2 TL + 4 LL. Odstęp między gabarytami wynosi co najmniej 8 mm. To odstęp dla druku całymi warstwami; nie jest wystarczającą deklaracją luzu głowicy w druku sekwencyjnym. Brim do 3 mm mieści się w domyślnym układzie B z zapasem.

## Otwory i zaokrąglenia

TL ma trzy otwory w zewnętrznej ścianie naprzeciw przegrody, na X=0. LL ma dwie prostopadłe serie po trzy: środki na X=t/2 w tylnej ścianie i Y=t/2 w bocznej. Wysokości osi od stołu to `base_thickness + 10 + i*15`, i=0,1,2.

Domyślny otwór zawiera nominalny okrąg i górny daszek 45°. Jego szerokość wynosi 6,65 mm, a pełna wysokość przekroju około 8,03 mm. Nie jest idealnym kołem. `$fn=64` daje minimalną średnicę wpisaną około 6,642 mm; to błąd dyskretyzacji poniżej 0,01 mm, niezależny od większych błędów wydruku. Minimalny pionowy mostek między otworami to około 6,97 mm. `support_free_holes=false` przywraca okrągły otwór i wymaga osobnej oceny jego druku.

Okno TL Ø12 przechodzi przez mostek; minimalny boczny pas mostka w poprzek szczeliny ma około 3,15 mm szerokości. LL ma okno w kształcie L, o szerokości 6 mm, odsunięte od zewnętrznych brzegów. Okna służą do kontroli ułożenia, nie do deklarowanego prowadzenia wiercenia.

R3 dotyczy głównego zewnętrznego obrysu. Wysoki narożny słupek LL ma zewnętrzny łuk o promieniu równym grubości ściany. Ścianki szczelin pozostają płaskie; żebra i wzmocnienia leżą poza obwiednią płyt. Prostokątne styki przy mostku pozostają miejscami koncentracji naprężeń — nie dodano tam dodatnich filletów, które zablokowałyby nieścięte krawędzie płyty.

## Zmiany parametrów

Zmiana ramion lub grubości może uniemożliwić układ 1 TL + 2 LL na stole 180 mm, mimo że pojedynczy model nadal pasuje. `print_layout.scad` wtedy zatrzyma render. Nie zmniejszaj modelu skalą procentową. Rozłóż części na dodatkowe stoły i sprawdź nowe gabaryty.

Zwiększając liczbę otworów, podnieś także `guide_height`. Nie zmniejszaj odstępu między otworami poniżej wartości dopuszczonej asercją. Wyłączenie otworów przez `include_guide_holes=false` pozostawia pełne wieże, co zwiększa ich przekrój. Nie jest to przełącznik usuwający całe przedłużenie.

Źródła i definicje: [config.scad](../src/config.scad), [common.scad](../src/common.scad). Pomiary STL: [validation_report.json](validation_report.json).
