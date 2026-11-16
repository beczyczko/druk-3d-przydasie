# Dodatkowe próby parametryzacji

Wykonano rzeczywisty render OpenSCAD i kontrolę zamknięcia obu poniższych zmodyfikowanych modeli:

| Przypadek | Zmiany | Wynik |
|---|---|---|
| `TL_custom` | B; płyta 18,2; luz 0,5; ramiona 75; bez otworów i okna | Jedna zamknięta bryła; zmierzona szczelina 18,699997 mm; pełny materiał w osi wyłączonego otworu |
| `LL_round_holes` | C; otwory okrągłe zamiast daszków; zewnętrzny promień 2 | Jedna zamknięta bryła, brak ostrzeżeń eksportu |

To testy funkcji parametrów, nie dodatkowe warianty zestawu do druku. Ich robocze STL są w lokalnym `tools/parameter-checks` i nie należą do paczki. Raport i sumy: [report.json](report.json); logi: [TL](TL_custom.log), [LL](LL_round_holes.log).

Odtworzenie z katalogu projektu:

```powershell
.\tools\python\python.exe .\scripts\check_parameters.py
```

Poza środowiskiem lokalnym użyj własnego Pythona 3.12 z bibliotekami walidacyjnymi i ustaw `OPENSCAD`, jeśli program nie jest wykrywany automatycznie.
