# Walidacja geometrii

Wynik: **PASS**, 2026-11-16. Wszystkie 21 STL sprawdzono bez naprawiania siatek.

OpenSCAD 2021.01 (CGAL) wygenerował STL; niezależne pomiary wykonano na trójkątach STL przy użyciu trimesh, Shapely i Manifold.

| Model | Gabaryt X × Y × Z [mm] | Szczeliny [mm] | Kąt baz [°] | Ścianka [mm] | Mostek [mm] |
|---|---|---|---|---|---|
| LL_compact | 56.4 × 56.4 × 52.0 | 18.29999; 18.29999 | 90.000000 | 4.400 | 3.200 |
| TL_compact | 104.0 × 56.4 × 52.0 | 18.29999; 18.29999 | 90.000000 | 4.400 | 3.200 |
| LL_reinforced | 80.4 × 80.4 × 62.0 | 18.29999; 18.29999 | 90.000000 | 6.000 | 4.800 |
| TL_reinforced | 144.0 × 80.4 × 62.0 | 18.29999; 18.29999 | 90.000000 | 6.000 | 4.800 |
| LL_standard | 75.0 × 75.0 × 58.0 | 18.29999; 18.29999 | 90.000000 | 5.000 | 3.600 |
| TL_standard | 140.0 × 75.0 × 58.0 | 18.29999; 18.29999 | 90.000000 | 5.000 | 3.600 |

## Przeprowadzone sprawdzenia

- Każda krawędź każdej siatki należy do dokładnie dwóch trójkątów; zgodne zwroty ścian, dodatnie objętości, brak trójkątów o zerowym polu.
- Każdy uchwyt i każda próbka stanowi jedną połączoną bryłę. Każdy stół ma trzy rozdzielone bryły, próbnik zbiorczy cztery.
- Szczeliny i grubości obu par ścian zmierzono promieniami przecinającymi rzeczywistą siatkę, tolerancja sprawdzenia 0,001 mm. Jest to dokładność obliczeń, nie druku.
- Normalne zmierzonych powierzchni bazowych są prostopadłe. Punkty łuków na spodzie potwierdzają zewnętrzny promień R3 w tolerancji 0,001 mm.
- Zmierzono trzy otwory TL i obie serie LL: szerokość 6,65 mm, rozstaw osi Z 15 mm, daszek 45°. Okrąg wielokątny ma 64 segmenty; minimalna średnica wpisana wynosi około 6,642 mm.
- Modele dwóch płyt mają 18 mm, stykają się doczołowo i nie przenikają. Dla wszystkich sześciu uchwytów przecięcie brył z każdą płytą ma objętość poniżej 0,0001 mm³.
- Sprawdzono zdejmowanie wzdłuż osi nasuwania: 0; 0,2; 1; 5; 15; 30 mm oraz wysokość uchwytu i wysokość + 2 mm. Dla każdej pozycji brak kolizji. Ciągła droga jest także wolna: odsuwanie w kierunku -Z oddala cały uchwyt od półprzestrzeni zajętej przez płyty, przy niezmienionym przekroju XY płyt.
- Z trójkątów leżących w płaszczyznach baz wyliczono wspólne pola kontaktu: dwie bazy boczne oraz podparcie krawędzi każdej płyty; wszystkie przekraczają 100 mm². Szczegółowe pola zapisano w JSON.
- Kontrola negatywna: modele płyt 18,4 mm powodują kolizję ze szczeliną 18,3 mm. Test wykrywa rzeczywiste niedopasowanie.
- Stoły mieszczą się w 180 × 180 mm, odstęp między gabarytami wynosi co najmniej 8 mm. Na każdym dokładnie 1 TL + 2 LL; dwa stoły dają 2 TL + 4 LL.
- Próbki zmierzono niezależnie: 18,2; 18,3; 18,4; 18,5 mm. Wszystkie modele, również poglądowe płyty, mają gabaryty poniżej 180 mm.

## Zakres i ograniczenia

Nie wykonano wydruków, prób zmęczeniowych, pomiaru kąta na fizycznych płytach, testu nośności ani symulacji MES. Nie uruchamiano krojenia w Bambu Studio; brak G-code i zweryfikowanych czasów druku. Ustawienia w printing.md są punktem startowym.

Luz 0,3 mm umożliwia nasuwanie, ale nie wytwarza siły docisku. Rzeczywisty kąt ustala się przez dosunięcie płyt do baz i sprawdzenie kątownikiem. Orientacyjna swoboda obrotu jednej płyty od luzu to atan(luz / długość kontaktu); nie jest to specyfikacja dokładności narzędzia. Narzędzie służy do pozycjonowania, bez podtrzymywania ciężaru całego korpusu.

Parametryczne zaokrąglenia na zewnątrz i wzmocnienia omijają szczeliny. Prostokątne styki funkcjonalne wewnątrz szczelin pozostają celowo ostre, aby krawędzie płyt dochodziły do mostka. W ich nasadach nadal możliwa jest koncentracja naprężeń; wariant B zwiększa przekrój i rozprowadza obciążenie żebrami, ale wymaga sprawdzenia w druku.

## Odtworzenie

```powershell
.\tools\python\python.exe .\scripts\validate.py
```

Raport maszynowy i sumy SHA-256: [validation_report.json](validation_report.json). Logi renderowania: [export_logs](export_logs). Walidator dotyczy dostarczonych wartości domyślnych; po zmianie parametrów należy dostosować niezależne wartości oczekiwane i ponowić weryfikację.
