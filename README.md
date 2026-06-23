# J.A.R.V.I.S. Mark I 🤖

Osobisty asystent AI, który analizuje chaotyczne, nieustrukturyzowane polecenia użytkownika i rozdziela je na zadania To-Do oraz wydarzenia w kalendarzu. Projekt implementuje zaawansowany wzorzec **Dynamicznego Doboru Modelu** (ang. *Dynamic Model Routing*) chroniący limity API oraz **Świadomość Czasu** (systemowy time injection) do precyzyjnego wnioskowania o relatywnych datach (np. "jutro", "za 3 dni").

---

## 🏗️ Architektura Systemu

Poniższy diagram przedstawia przepływ danych w aplikacji:

```mermaid
graph TD
    A[Użytkownik - Streamlit Frontend] -->|Chaotyczny Prompt| B[FastAPI Backend - /process]
    B -->|Inicjalizacja i przekazanie| C[JarvisAgent]
    C -->|Krok 1: Bramkarz (Tani Model)| D{Czy zadanie jest złożone?}
    D -->|NIE - is_complex: False| E[Użyj Taniego Modelu do finalnej ekstrakcji JSON]
    D -->|TAK - is_complex: True| F[Dedykowana zmiana modelu na Pro/Expensive]
    F -->|Krok 2: Wykonawca (Drogi Model)| G[Głęboka analiza i ekstrakcja JSON]
    E --> H[Ustrukturyzowany JSON (Pydantic)]
    G --> H
    H -->|Dane wyjściowe| B
    B -->|Krok 3: Wywołanie Mock Integracji| I[Google Calendar Mock / Google Tasks Mock]
    B -->|Finalna odpowiedź| A
```

---

## 🧠 Główne Funkcjonalności

### 1. Bramkarz i Dynamiczny Dobór Modelu (Model Router)
System chroni limity API oraz optymalizuje koszty przy użyciu dwuetapowego przetwarzania:
*   **Bramkarz (Gatekeeper):** Zawsze jako pierwszy analizuje prompt. Używa szybkiego i taniego modelu (`gemini-1.5-flash` lub `gpt-4o-mini`). Zwraca ustrukturyzowany JSON z flagą logiczną `is_complex` oraz pisemnym uzasadnieniem (`reasoning`).
*   **Wykonawca (Executor):**
    *   Jeśli `is_complex: False` (np. proste dodanie pojedynczego zadania) -> finalny JSON jest generowany przez ten sam tani model.
    *   Jeśli `is_complex: True` (np. wykryte konflikty terminów, wieloetapowy plan działania, niejednoznaczności czasowe) -> agent **dynamicznie przełącza się** na model potężniejszy/droższy (`gemini-1.5-pro` lub `gpt-4o`), przekazując mu zadanie do zaawansowanego wnioskowania.

### 2. Świadomość Czasu (System Time Anchoring)
Przed każdym zapytaniem do modeli LLM, do ich Promptu Systemowego wstrzykiwany jest aktualny czas systemowy w formacie `YYYY-MM-DD HH:MM`. Pozwala to modelom poprawnie interpretować relatywne określenia czasowe takie jak *"jutro"*, *"w przyszły poniedziałek"* czy *"za dwie godziny"*.

### 3. Automatyczne Integracje w Tle (Mocks)
Po poprawnym sprasowaniu danych przez agenta, backend FastAPI automatycznie uruchamia mockowane integracje z:
*   **Google Calendar** (`GoogleCalendarMock.create_event()`) - wypisuje sformatowaną ramkę z nowym wydarzeniem w konsoli serwera.
*   **Google Tasks** (`GoogleTasksMock.create_task()`) - wypisuje sformatowaną ramkę z nowym zadaniem w konsoli serwera.

---

## 📁 Struktura Projektu i Pliki Źródłowe

Każdy z poniższych plików tworzy kompletną aplikację:
1.  [server.py](file:///home/siemabrokul/Projects/jarvis_mark_1/server.py) – Serwer FastAPI z middleware CORS, endpointem `/process` obsługującym proces routingu modeli oraz wywołującym mocki w tle. Zaimplementowano tu graficzne logowanie decyzji w konsoli.
2.  [agent.py](file:///home/siemabrokul/Projects/jarvis_mark_1/agent.py) – Logika agenta AI (wspierająca Pydantic Structured Outputs dla bibliotek `google-genai` oraz `openai`). Zarządza bramkarzem, przekierowaniem modeli oraz formatowaniem systemowych informacji o czasie.
3.  [integrations.py](file:///home/siemabrokul/Projects/jarvis_mark_1/integrations.py) – Klasy symulujące bezpośredni zapis zadań i wydarzeń do systemów Google Calendar i Google Tasks za pomocą eleganckich terminalowych konsol wizualnych.
4.  [app.py](file:///home/siemabrokul/Projects/jarvis_mark_1/app.py) – Interfejs Streamlit stworzony w estetyce Glassmorphic Dark Mode. Pozwala on łatwo wysyłać zapytania, wizualizować ustrukturyzowane tabele i wykresy decyzji routingu modeli w czasie rzeczywistym.
5.  [.env.example](file:///home/siemabrokul/Projects/jarvis_mark_1/.env.example) – Szablon pliku ze zmiennymi środowiskowymi.
6.  [requirements.txt](file:///home/siemabrokul/Projects/jarvis_mark_1/requirements.txt) – Wykaz wszystkich potrzebnych bibliotek Python.
7.  [setup_github.sh](file:///home/siemabrokul/Projects/jarvis_mark_1/setup_github.sh) – Skrypt konfiguracyjny do utworzenia prywatnego repozytorium GitHub i issue tracking.
8.  [.gitignore](file:///home/siemabrokul/Projects/jarvis_mark_1/.gitignore) – Reguły ignorowania plików tymczasowych i sekretów w repozytorium.

---

## 🛠️ Podręcznik Wdrożeniowy Użytkownika (Deployment & Setup)

Wykonaj poniższe kroki, aby w pełni skonfigurować i uruchomić asystenta na swoim komputerze:

### Krok 1: Skonfigurowanie kluczy API w pliku `.env`
1.  Skopiuj szablon środowiskowy w głównym katalogu projektu:
    ```bash
    cp .env.example .env
    ```
2.  Otwórz utworzony plik `.env` i wybierz dostawcę AI za pomocą parametru `AI_PROVIDER`:
    *   **Opcja A: Google Gemini (Zalecane)**
        *   Zostaw `AI_PROVIDER=gemini`.
        *   Zaloguj się na platformie [Google AI Studio](https://aistudio.google.com/) i wygeneruj darmowy klucz API.
        *   Wklej ten klucz w pliku `.env` jako wartość parametru: `GEMINI_API_KEY=twój_klucz_tutaj`.
        *   Domyślne modele Gemini w projekcie to `gemini-1.5-flash` (tani) i `gemini-1.5-pro` (drogi).
    *   **Opcja B: OpenAI**
        *   Ustaw `AI_PROVIDER=openai`.
        *   Pobierz swój klucz z profilu [OpenAI Platform](https://platform.openai.com/).
        *   Wklej ten klucz jako wartość parametru: `OPENAI_API_KEY=twój_klucz_tutaj`.
        *   Domyślne modele OpenAI w projekcie to `gpt-4o-mini` i `gpt-4o`.

### Krok 2: Przygotowanie środowiska Python i zależności
Uruchom w swoim terminalu w głównym katalogu projektu:
```bash
# 1. Tworzenie środowiska wirtualnego venv
python3 -m venv venv

# 2. Aktywacja środowiska wirtualnego
source venv/bin/activate

# 3. Aktualizacja pip oraz instalacja pakietów z requirements.txt
pip install --upgrade pip
pip install -r requirements.txt
```

### Krok 3: Uruchomienie Serwera Backend (FastAPI)
W aktywnym oknie terminala uruchom serwer uvicorn:
```bash
uvicorn server:app --reload
```
*Serwer wystartuje lokalnie pod adresem: `http://localhost:8000`. Jeśli zapomniałeś ustawić klucz API w pliku `.env`, serwer zaloguje ostrzeżenie krytyczne w konsoli, ale nadal wystartuje (błędy pojawią się dopiero przy próbie przetworzenia zapytania).*

### Krok 4: Uruchomienie Interfejsu Użytkownika (Streamlit)
Otwórz drugie okno terminala, przejdź do katalogu projektu, aktywuj venv (`source venv/bin/activate`) i wpisz:
```bash
streamlit run app.py
```
*Frontend Streamlit uruchomi się automatycznie w przeglądarce pod adresem `http://localhost:8501`.*

---

## 🧪 Przebieg Scenariusza Testowego

W interfejsie Streamlit zaimplementowano przycisk ładujący naszą frazę testową:
> *"Jutro muszę złożyć wniosek do wydziału oświaty w sprawie mojego awansu zawodowego na nauczyciela mianowanego (robię według przepisów z 2018 roku), później muszę podejść do szkoły podpisać świadectwo i arkusz. Zrobić pranie firanek i posprzątać mieszkanie."*

### Ścieżka wykonania krok po kroku:
1.  **Kotwiczenie czasu**: System automatycznie wstrzykuje dzisiejszą datę lokalną (np. `Aktualny czas systemu: 2026-06-23 18:32`).
2.  **Klasyfikacja Bramkarza**: Bramkarz analizuje chaotyczne zdanie i wykrywa, że zawiera ono relatywność czasową ("jutro", "później") oraz uwarunkowanie prawne ("przepisy z 2018 roku"). Klasyfikuje je jako złożone (`is_complex: True`) z reasoningiem w języku angielskim/polskim.
3.  **Podmiana modelów**: Kod dynamicznie przełącza się na model droższy i potężniejszy (`gemini-1.5-pro` lub `gpt-4o`).
4.  **Generowanie ustrukturyzowanych danych**: Model droższy rozbija tekst wejściowy na:
    *   **Wydarzenie 1**: Złożenie wniosku do wydziału oświaty (zaplanowane na jutro, np. `2026-06-24`).
    *   **Wydarzenie 2**: Podejście do szkoły i podpisanie świadectwa oraz arkusza (zaplanowane na jutro po wydarzeniu 1).
    *   **Zadanie To-Do 1**: Pranie firanek.
    *   **Zadanie To-Do 2**: Posprzątanie mieszkania.
5.  **Wypisanie Mocków w konsoli**: Backend FastAPI automatycznie wywołuje mockowane integracje i drukuje w terminalu sformatowane ramki.

Oto przykładowy log z konsoli serwera po przetworzeniu powyższej frazy:
```text
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
🤖 [J.A.R.V.I.S. DYNAMIC ROUTING DECISION]
  Gatekeeper Decision:  COMPLEX (Needs Advanced AI)
  Reasoning:            Prompt contains multiple sequential tasks (tomorrow, then school), context about 2018 education rules, and domestic chores.
  Provider Used:        GEMINI
  Model Selected:       gemini-1.5-pro (EXPENSIVE tier)
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

🔌 Triggering Mock Integrations for identified entities...

📅 [GOOGLE CALENDAR] INTEGRATION - CREATING EVENT
  Title:       Złożenie wniosku do wydziału oświaty w sprawie awansu zawodowego
  Start Time:  2026-06-24 09:00
  Description: Składanie wniosku o awans zawodowy nauczyciela mianowanego według przepisów z 2018 r.
==================================================

📅 [GOOGLE CALENDAR] INTEGRATION - CREATING EVENT
  Title:       Podpisanie świadectwa i arkusza w szkole
  Start Time:  2026-06-24 12:00
  Description: Podejście do szkoły i podpisanie dokumentów.
==================================================

📋 [GOOGLE TASKS] INTEGRATION - CREATING TASK
  Title:       Pranie firanek
  Priority:    MEDIUM
==================================================

📋 [GOOGLE TASKS] INTEGRATION - CREATING TASK
  Title:       Posprzątanie mieszkania
  Priority:    MEDIUM
==================================================
```

---

## 📝 Dziennik Prac i Wdrożeń (Logs)

### Wpis: 2026-06-23 (Senior Python/AI & DevOps)
Zrealizowano pełny cykl konfiguracji i wdrożenia osobistego asystenta **J.A.R.V.I.S. Mark I** w środowisku lokalnym oraz integrację z repozytorium GitHub.

#### 1. Zakres wykonanych prac:
*   **Konfiguracja GitHub CLI (`gh`)**: Zaimplementowano w pełni zautomatyzowany skrypt [setup_github.sh](file:///home/siemabrokul/Projects/jarvis_mark_1/setup_github.sh) do inicjalizacji repozytorium, definiowania etykiet (`setup`, `backend`, `ai`, `frontend`) oraz automatycznego tworzenia 4 kamieni milowych (Issues #1-#4).
*   **Architektura Dynamicznego Doboru Modelu**: Uruchomiono dwuetapową procedurę przetwarzania w pliku [agent.py](file:///home/siemabrokul/Projects/jarvis_mark_1/agent.py):
    1.  **Bramkarz (Gatekeeper)**: Klasyfikuje zapytanie za pomocą szybkiego i ekonomicznego modelu (`gemini-1.5-flash`).
    2.  **Wykonawca (Executor)**: W przypadku wykrycia złożoności (`is_complex: True`) przełącza kontekst na zaawansowany model (`gemini-1.5-pro`).
*   **Kotwiczenie czasu**: Wstrzyknięto aktualny czas systemowy (`Aktualny czas systemu: YYYY-MM-DD HH:MM`) do instrukcji systemowych obu modeli Gemini/OpenAI, co umożliwia precyzyjną interpretację dat relatywnych (np. "jutro").
*   **Backend API**: Serwer [server.py](file:///home/siemabrokul/Projects/jarvis_mark_1/server.py) w FastAPI udostępnia endpoint `/process` z wbudowanym mechanizmem logowania decyzji routingu w konsoli oraz automatycznym wywoływaniem mocków integracji z zewnętrznymi serwisami Google.
*   **Mock Integracji**: W pliku [integrations.py](file:///home/siemabrokul/Projects/jarvis_mark_1/integrations.py) zdefiniowano klasy [GoogleCalendarMock](file:///home/siemabrokul/Projects/jarvis_mark_1/integrations.py#L6) i [GoogleTasksMock](file:///home/siemabrokul/Projects/jarvis_mark_1/integrations.py#L42).
*   **Streamlit Frontend**: Zaprojektowano interfejs w pliku [app.py](file:///home/siemabrokul/Projects/jarvis_mark_1/app.py) z wykorzystaniem estetyki Glassmorphic Dark Mode, podglądem routingu w czasie rzeczywistym oraz zintegrowanym przyciskiem ładowania danych testowych.
