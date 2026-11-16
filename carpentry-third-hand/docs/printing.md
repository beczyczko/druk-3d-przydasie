# Druk na Bambu Lab A1 mini

Oficjalna specyfikacja podaje pole 180 × 180 × 180 mm, dyszę fabryczną 0,4 mm i PETG wśród zalecanych materiałów. Dostarczone układy mieszczą się w tym polu. [Bambu Lab — specyfikacja A1 mini](https://store.bblcdn.eu/s8/default/87c1a9ef9f3a438a87d8f19fd8faea58/Bambu-Lab-A1-mini-tech-specs.pdf).

Poniższe wartości są **zaleceniami projektowymi do próbnego wydruku**, nie przetestowanym profilem fabrycznym. Nie przeprowadzono krojenia ani druku.

| Ustawienie w Bambu Studio | Punkt startowy |
|---|---|
| Drukarka | A1 mini, dysza 0,4 mm |
| Materiał | Suchy PETG, profil zgodny z konkretną szpulą |
| Warstwa / pierwsza warstwa | 0,20 / 0,20 mm |
| Obrysy | B: 6; A: 5–6; C: 5 |
| Górne / dolne pełne warstwy | 6 / 6 |
| Wypełnienie | B: 35% gyroid; A: 30–35%; C: 25% |
| Podpory | Wyłączone, dla domyślnej orientacji i otworów z daszkiem |
| Orientacja | Płaska zewnętrzna powierzchnia mostka w Z=0 na stole; szczeliny i wieże ku górze |
| Brim | Domyślnie 0; przy podwijaniu naroży 3 mm na zewnątrz |
| Kolejność druku | Całymi warstwami, wszystkie części równocześnie |
| Ściana zewnętrzna | Początkowo 40–60 mm/s |
| Ściana wewnętrzna | Początkowo 60–90 mm/s, w granicach przepływu filamentu |
| Przyspieszenie ścian zewnętrznych | 1500–2500 mm/s² jako spokojny punkt startowy |
| Skalowanie | 100%, jednostka mm |
| Kompensacje wymiarów XY | Początkowo 0; dopiero po pomiarze próbki |

Wariant B ma ściany 6 mm. Same obrysy nie muszą wypełnić całego ich przekroju; gyroid wypełnia środek. Nie traktuj 35% jako objętości całej części — obrysy oraz mostek zwiększają udział pełnego materiału. Dla wież i nasad można w slicerze zastosować lokalny modyfikator 60–100% wypełnienia, jeśli próbny wydruk wykazuje ugięcie. Najpierw zwiększ jakość spajania warstw i liczbę obrysów.

## Temperatury i przygotowanie materiału

Użyj profilu producenta filamentu. Przykładowo Bambu PETG HF ma podany zakres dyszy 230–260°C, stołu 65–75°C oraz suszenie 65°C przez 8 godzin w odpowiedniej suszarce. To dane tego konkretnego materiału; nie przenoś ich automatycznie na każdy PETG. Dla niego 250°C / 70°C można przyjąć jako punkt próbny w granicach zaleceń. [Bambu PETG HF — karta techniczna](https://store.bblcdn.com/s6/default/20423d7f839c4a66b9712508549c68b4/Bambu_PETG_HF_TDS.pdf).

Chłodzenie pozostaw początkowo zgodne z profilem szpuli. Utrzymuj nadmuch potrzebny do daszków otworów, ale nie zwiększaj go bez potrzeby przy nasadach ścian. Zbyt zimny lub mokry wydruk może mieć słabe połączenia warstw. Temperaturę i prędkość dobieraj na próbkach, obserwując spajanie, nitki i dokładność.

Przygotuj płytę roboczą zgodnie z jej instrukcją; na powierzchniach wymagających separatora dla PETG zastosuj odpowiedni klej. Nie odrywaj gorącej części siłą. Poczekaj na ostygnięcie stołu.

## Orientacja i wytrzymałość

Mostek płasko daje ciągłe ścieżki XY łączące ramiona T/L. Wieże oraz krótkie ściany wyrastają z szerokiej podstawy, a żebra B rozkładają ich zginanie na większy obszar. Fazowane wloty, zwężające się żebra i daszki otworów nie wymagają podpór geometrycznych.

Ta orientacja pozostawia obciążenie międzywarstwowe u nasad pionowych ścian. Nie usuwa anizotropii FDM. Druk na boku wzmacniałby część połączeń, lecz wymagał podpór i pogarszał bazy pozostałych szczelin. Orientacja dostarczona jest kompromisem pod kątem funkcji, spójnego mostka i dokładności; jej wytrzymałość trzeba sprawdzić w wydruku.

Przewidywane słabe miejsca: nasady wież, narożnik LL, nasady ścian szczelin i obszary przy otworach. Zwiększenie ściany, mostka i zasięgu wzmocnień oraz zastosowanie wariantu B poprawia przekrój. Nie rozwieraj nasadki na za grubą płytę. Nie oceniaj trwałości tylko po procentowym wypełnieniu.

## Pasowanie i dokładność

1. Wykonaj kalibrację przepływu dla szpuli i sprawdź pierwszą warstwę.
2. Wydrukuj próbnik bez zmiany skali, w tej samej orientacji i z tymi samymi obrysami.
3. Usuń nitki i zadziory, nie szlifując całych powierzchni bazowych. Zmierz szczeliny i płytę.
4. Wybierz całkowity dodatek. Domyślne 0,3 mm jest punktem startowym, nie gwarancją dopasowania każdej płyty 18 mm.
5. Jeżeli błąd jest powtarzalny, skoryguj parametr CAD albo świadomie kompensację w slicerze. Nie sumuj kilku korekt bez pomiaru.
6. Sprawdź duży TL i LL na rzeczywistych płytach. Krótka próbka nie wykrywa łuku lub skurczu długich ramion.

Rozlanie pierwszej warstwy dotyczy zewnętrznego mostka; zasadnicza szczelina zaczyna się dopiero ponad nim. Brak poprawnego osadzenia może jednak wynikać także z nadlewek w głębi szczeliny lub wygięcia mostka. Nie dobieraj kompensacji „elephant foot” na ślepo.

## Import i dwa stoły

Wczytaj `plate_1_<wariant>.stl`, zachowaj położenie oraz Z=0. To trzy zamknięte, rozłączone bryły w jednym STL. Jeśli Bambu Studio proponuje podział, można podzielić na obiekty z zachowaniem współrzędnych. Nie uruchamiaj automatycznego obracania na inną powierzchnię ani automatycznego układania, jeśli chcesz zachować zweryfikowany układ.

Po pierwszym wsadzie wydrukuj `plate_2_<wariant>.stl`. Nie drukuj obu stołów nakładających się na siebie. Przy brim 3 mm wariant B ma zapas 2,6 mm do granicy nominalnego pola. Uwzględnij pozycję linii przygotowawczej i ewentualne obszary wyłączone przez własny profil slicera. Kontrolę tych elementów wykonaj w podglądzie przed drukiem.

Nie podano czasu ani rzeczywistej masy filamentu, bo zależą od krojenia. Objętości pełnych brył znajdują się w raporcie JSON; nie są prognozą zużycia przy 35% wypełnieniu.
