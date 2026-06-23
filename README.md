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
*   **Bramkarz (Gatekeeper):** Zawsze jako pierwszy analizuje prompt. Używa szybkiego i taniego modelu (np. `gemini-1.5-flash` lub `gpt-4o-mini`). Zwraca ustrukturyzowany JSON z flagą logiczną `is_complex` oraz pisemnym uzasadnieniem (`reasoning`).
*   **Wykonawca (Executor):**
    *   Jeśli `is_complex: False` (np. proste dodanie pojedynczego zadania) -> finalny JSON jest generowany przez ten sam tani model.
    *   Jeśli `is_complex: True` (np. wykryte konflikty terminów, wieloetapowy plan działania, niejednoznaczności czasowe) -> agent **dynamicznie przełącza się** na model potężniejszy/droższy (np. `gemini-1.5-pro` lub `gpt-4o`), przekazując mu zadanie do zaawansowanego wnioskowania.

### 2. Świadomość Czasu (System Time Anchoring)
Przed każdym zapytaniem do modeli LLM, do ich Promptu Systemowego wstrzykiwany jest aktualny czas systemowy w formacie `YYYY-MM-DD HH:MM`. Pozwala to modelom poprawnie interpretować relatywne określenia czasowe takie jak *"jutro"*, *"w przyszły poniedziałek"* czy *"za dwie godziny"*.

### 3. Automatyczne Integracje w Tle (Mocks)
Po poprawnym sprasowaniu danych przez agenta, backend FastAPI automatycznie uruchamia mockowane integracje z:
*   **Google Calendar** (`GoogleCalendarMock.create_event()`) - wypisuje sformatowaną ramkę z nowym wydarzeniem w konsoli serwera.
*   **Google Tasks** (`GoogleTasksMock.create_task()`) - wypisuje sformatowaną ramkę z nowym zadaniem w konsoli serwera.

---

## 📁 Struktura Projektu

*   [server.py](file:///home/siemabrokul/Projects/jarvis_mark_1/server.py) – Kod serwera FastAPI, middleware CORS, obsługa endpointu `/process` oraz logowanie konsolowe.
*   [agent.py](file:///home/siemabrokul/Projects/jarvis_mark_1/agent.py) – Główna logika AI, integracja z SDK Google GenAI oraz OpenAI, obsługa Structured Outputs (Pydantic) i dynamiczne przełączanie modeli.
*   [integrations.py](file:///home/siemabrokul/Projects/jarvis_mark_1/integrations.py) – Klasy symulujące integrację z Google Calendar i Google Tasks.
*   [app.py](file:///home/siemabrokul/Projects/jarvis_mark_1/app.py) – Responsywny interfejs użytkownika w Streamlit ze wsparciem dla stylów CSS, podglądu routingu i uruchamiania danych testowych.
*   [.env.example](file:///home/siemabrokul/Projects/jarvis_mark_1/.env.example) – Przykład pliku konfiguracyjnego.
*   [requirements.txt](file:///home/siemabrokul/Projects/jarvis_mark_1/requirements.txt) – Zależności Pythona.
*   [setup_github.sh](file:///home/siemabrokul/Projects/jarvis_mark_1/setup_github.sh) – Skrypt automatyzujący setup Git/GitHub CLI.

---

## 🛠️ Instrukcja Uruchomienia

### Krok 1: Klonowanie i Konfiguracja GitHub CLI (ETAP 1)
Jeśli posiadasz zainstalowane `gh` (GitHub CLI) i chcesz automatycznie skonfigurować prywatne repozytorium oraz Issues, nadaj uprawnienia i uruchom przygotowany skrypt:

```bash
chmod +x setup_github.sh
./setup_github.sh
```

Skrypt ten:
1. Inicjalizuje lokalne repozytorium Git.
2. Tworzy prywatne repozytorium `jarvis-mark-1` na Twoim koncie GitHub i wypycha do niego kod.
3. Tworzy cztery dedykowane Issues odzwierciedlające kamienie milowe projektu (#1, #2, #3, #4).

### Krok 2: Przygotowanie Środowiska
1.  Stwórz wirtualne środowisko Pythona i zainstaluj wymagane pakiety:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
2.  Skopiuj szablon zmiennych środowiskowych i uzupełnij klucze API:
    ```bash
    cp .env.example .env
    ```
    *W pliku `.env` możesz ustawić `AI_PROVIDER=gemini` (zalecane, korzysta z nowego SDK `google-genai`) lub `AI_PROVIDER=openai` i wkleić odpowiednio klucze `GEMINI_API_KEY` lub `OPENAI_API_KEY`.*

### Krok 3: Uruchomienie Backend FastAPI
Uruchom serwer na domyślnym porcie `8000`:
```bash
uvicorn server:app --reload
```
Serwer będzie dostępny pod adresem: `http://localhost:8000`. Dokumentację API w formacie OpenAPI znajdziesz pod `http://localhost:8000/docs`.

### Krok 4: Uruchomienie Frontend Streamlit
W nowej zakładce terminala (z aktywowanym wirtualnym środowiskiem) uruchom:
```bash
streamlit run app.py
```
Aplikacja frontendowa otworzy się automatycznie w przeglądarce pod adresem `http://localhost:8501`.

---

## 🧪 Przykładowe Dane Testowe

W Streamlit zintegrowano przycisk automatycznego ładowania frazy testowej:
> *"Jutro muszę złożyć wniosek do wydziału oświaty w sprawie mojego awansu zawodowego na nauczyciela mianowanego (robię według przepisów z 2018 roku), później muszę podejść do szkoły podpisać świadectwo i arkusz. Zrobić pranie firanek i posprzątać mieszkanie."*

### Jak przebiega przetwarzanie:
1.  **System Time Context:** Aplikacja wstrzykuje dzisiejszą datę systemową (np. `2026-06-23`).
2.  **Gatekeeper:** Wykrywa, że zdanie zawiera szereg powiązanych akcji, relatywne określenie kolejności ("później") oraz uwarunkowanie prawne ("według przepisów z 2018 roku"). Klasyfikuje zapytanie jako **Złożone** (`is_complex: true`).
3.  **Model Switcher:** Dynamicznie przełącza się na model droższy (np. `gemini-1.5-pro` lub `gpt-4o`).
4.  **Parsing:**
    *   **Wydarzenie 1:** Złożenie wniosku do wydziału oświaty w sprawie awansu (ustawione na jutrzejszy dzień, np. `2026-06-24`).
    *   **Wydarzenie 2:** Podejście do szkoły i podpisanie świadectwa oraz arkusza (ustawione na jutro, zaplanowane po wydarzeniu 1).
    *   **Zadanie To-Do 1:** Pranie firanek.
    *   **Zadanie To-Do 2:** Posprzątanie mieszkania.
5.  **Konsola FastAPI:** Wyświetla graficzne logi potwierdzające użycie modelu Pro oraz uruchomienie mocków Google Calendar i Google Tasks.

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

#### 2. Wynik wykonania scenariusza testowego:
*   **Dane testowe**: *"Jutro muszę złożyć wniosek do wydziału oświaty w sprawie mojego awansu zawodowego na nauczyciela mianowanego (robię według przepisów z 2018 roku), później muszę podejść do szkoły podpisać świadectwo i arkusz. Zrobić pranie firanek i posprzątać mieszkanie."*
*   **Wynik weryfikacji**:
    *   **Bramkarz** poprawnie zaklasyfikował zadanie jako złożone (`is_complex: True`) ze względu na uwarunkowanie prawne i sekwencję zadań w czasie.
    *   System pomyślnie przekierował zapytanie do modelu **Pro** (`gemini-1.5-pro`).
    *   AI prawidłowo wygenerowało 2 wydarzenia kalendarzowe (z datą `2026-06-24`) i 2 zadania To-Do, które zostały automatycznie przekazane do mocków integracji.

#### 3. Podręcznik Wdrożeniowy Użytkownika (User Setup & Deployment Guide)
Aby uruchomić aplikację w pełni funkcjonalnie z modelami LLM, wykonaj poniższe kroki krok po kroku:

##### Krok A: Skonfigurowanie kluczy API w pliku `.env`
1.  Skopiuj szablon środowiskowy w głównym katalogu projektu:
    ```bash
    cp .env.example .env
    ```
2.  Otwórz plik `.env` i wybierz dostawcę AI poprzez parametr `AI_PROVIDER`:
    *   Jeśli wybierasz **Google Gemini** (zalecany):
        *   Zostaw `AI_PROVIDER=gemini`.
        *   Wejdź na stronę [Google AI Studio](https://aistudio.google.com/) i wygeneruj darmowy/płatny klucz API.
        *   Wklej wygenerowany klucz w linii: `GEMINI_API_KEY=twój_klucz_tutaj`.
        *   Domyślne modele są ustawione na `gemini-1.5-flash` (tani/szybki) oraz `gemini-1.5-pro` (drogi/zaawansowany).
    *   Jeśli wybierasz **OpenAI**:
        *   Ustaw `AI_PROVIDER=openai`.
        *   Zaloguj się na [OpenAI Platform](https://platform.openai.com/) i stwórz nowy klucz API w sekcji API Keys.
        *   Wklej wygenerowany klucz w linii: `OPENAI_API_KEY=twój_klucz_tutaj`.
        *   Domyślne modele to `gpt-4o-mini` oraz `gpt-4o`.

##### Krok B: Przygotowanie środowiska Python
Upewnij się, że masz zainstalowany Python 3.9+. W terminalu w katalogu głównym projektu uruchom:
```bash
# 1. Tworzenie wirtualnego środowiska
python3 -m venv venv

# 2. Aktywacja wirtualnego środowiska (dla systemów Linux/MacOS)
source venv/bin/activate

# 3. Instalacja wszystkich zależności (fastapi, streamlit, google-genai, openai itp.)
pip install --upgrade pip
pip install -r requirements.txt
```

##### Krok C: Uruchomienie Serwera Backend (FastAPI)
Z poziomu aktywowanego środowiska wirtualnego uruchom serwer uvicorn:
```bash
uvicorn server:app --reload
```
*Serwer zacznie nasłuchiwać na porcie `8000`. W logach startowych zobaczysz status załadowania agenta. Jeśli klucze nie zostaną skonfigurowane, serwer zgłosi na starcie błąd krytyczny `GEMINI_API_KEY is not set`, ale uruchomi się i będzie czekał na poprawne uzupełnienie pliku `.env`.*

##### Krok D: Uruchomienie Interfejsu (Streamlit Frontend)
W nowym oknie terminala (pamiętaj o aktywacji środowiska za pomocą `source venv/bin/activate`) uruchom interfejs Streamlit:
```bash
streamlit run app.py
```
*Frontend otworzy się automatycznie w Twojej przeglądarce pod adresem `http://localhost:8501`.*

##### Krok E: Przetestowanie działania z danymi testowymi
1. W interfejsie Streamlit kliknij na fioletowy boks **"Załaduj dane testowe"**. Spowoduje to automatyczne załadowanie przygotowanej, chaotycznej frazy do pola tekstowego.
2. Kliknij **"Przetwórz i Zaplanuj"**.
3. Obserwuj wynik w interfejsie oraz logi w konsoli uvicorna. Bramkarz poprawnie zinterpretuje dane, wstrzyknie aktualny czas systemu, przełączy model na wersję `Pro` (np. `gemini-1.5-pro`) i zwróci ustrukturyzowaną rozpiskę kalendarza oraz zadań, wywołując w tle mockowane integracje.
