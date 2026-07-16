import streamlit as st
import requests
import os
import json

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="J.A.R.V.I.S. Mark I - Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# BACKEND SERVER URL CONFIGURATION
API_URL = os.getenv("API_URL", "http://localhost:8000")

# =====================================================================
# CUSTOM CSS FOR STUNNING GLASSMORPHIC DARK-MODE AESTHETICS
# =====================================================================
st.markdown(
    """
    <style>
    /* Dark theme overrides and global styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container styling */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid rgba(99, 102, 241, 0.2);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        text-align: center;
    }
    
    .main-title {
        background: linear-gradient(90deg, #818cf8 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .main-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    /* Card design for outputs */
    .card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    
    .card-title {
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Badges */
    .badge {
        padding: 0.25rem 0.6rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-cheap {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .badge-expensive {
        background-color: rgba(234, 179, 8, 0.15);
        color: #facc15;
        border: 1px solid rgba(234, 179, 8, 0.3);
    }
    
    .badge-complex {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .badge-simple {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    
    /* Quick test area */
    .test-box {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        border: 1px dashed rgba(255, 255, 255, 0.1);
    }
    
    /* Interactive custom button animations */
    div.stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
        background: linear-gradient(90deg, #4f46e5 0%, #4338ca 100%) !important;
    }
    
    div.stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Input field design */
    div.stTextArea textarea {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
        transition: border-color 0.2s ease !important;
    }
    
    div.stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================================
# APP HEADER
# =====================================================================
st.markdown(
    """
    <div class="main-header">
        <div class="main-title">J.A.R.V.I.S. Mark I</div>
        <div class="main-subtitle">Osobisty asystent AI do analizy i ustrukturyzowania zadań i kalendarza</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================================
# SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown("### ⚙️ Konfiguracja & Status")
    
    # Simple check backend server connection
    try:
        health_resp = requests.get(f"{API_URL}/health", timeout=3)
        if health_resp.status_code == 200:
            status_data = health_resp.json()
            st.success("🟢 Połączono z Backendem")
            provider = status_data.get("provider")
            provider_str = provider.upper() if provider else "UNCONFIGURED (Check .env)"
            st.info(f"AI Provider: **{provider_str}**")
        else:
            st.warning("⚠️ Backend zgłasza nieprawidłowy status")
    except Exception:
        st.error("🔴 Brak połączenia z Backendem FastAPI (uruchom server.py na porcie 8000)")
        
    st.markdown("---")
    st.markdown(
        """
        ### 📖 O Projekcie
        **J.A.R.V.I.S. Mark I** analizuje chaotyczne notatki i rozdziela je na:
        - **Wydarzenia w kalendarzu** (np. wizyty, spotkania, terminy)
        - **Zadania To-Do** (lista rzeczy do zrobienia)
        
        **Dynamiczny dobór modelu**:
        Bramkarz (Tani model) decyduje czy żądanie jest złożone. W razie potrzeby dynamicznie przełącza się na droższy model do głębokiej analizy.
        """
    )

st.markdown("### 📝 Wprowadź polecenie dla J.A.R.V.I.S.-a")

# Text input for command
command_input = st.text_area(
    "Co chcesz dziś zaplanować? Wpisz to w dowolnej, chaotycznej formie:",
    value=st.session_state.get("command_input", ""),
    height=120,
    placeholder="Np. Jutro o 12:00 mam spotkanie z Janem, a wieczorem muszę zrobić pranie i kupić chleb..."
)

col_run, _ = st.columns([1, 3])
submit_button = col_run.button("Przetwórz i Zaplanuj")

# =====================================================================
# RESULTS PROCESSING & RENDER
# =====================================================================
if submit_button:
    if not command_input.strip():
        st.warning("Wpisz najpierw polecenie do przetworzenia.")
    else:
        with st.spinner("J.A.R.V.I.S. analizuje Twoje dane..."):
            try:
                # Call FastAPI backend
                response = requests.post(
                    f"{API_URL}/process",
                    json={"command": command_input},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    res_json = response.json()
                    
                    # Split details
                    gatekeeper = res_json.get("gatekeeper", {})
                    routing = res_json.get("routing", {})
                    data = res_json.get("data", {})
                    system_time = res_json.get("system_time", "")
                    
                    st.success("✅ Polecenie pomyślnie przetworzone!")
                    
                    # --- METADATA PANEL ---
                    st.markdown("### 📊 Szczegóły Analizy i Dynamicznego Przekierowania")
                    col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
                    
                    with col_meta1:
                        badge_class = "badge-complex" if gatekeeper.get("is_complex") else "badge-simple"
                        badge_label = "ZŁOŻONY (Pro)" if gatekeeper.get("is_complex") else "PROSTY (Flash)"
                        st.markdown(
                            f"""
                            <div class="card" style="text-align: center; height: 130px;">
                                <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">KLASYFIKACJA ZADANIA</div>
                                <span class="badge {badge_class}" style="font-size: 0.9rem; padding: 6px 12px;">{badge_label}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    with col_meta2:
                        tier_class = "badge-expensive" if routing.get("tier") == "expensive" else "badge-cheap"
                        st.markdown(
                            f"""
                            <div class="card" style="text-align: center; height: 130px;">
                                <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">UŻYTY MODEL</div>
                                <code style="color: #a5b4fc; font-size: 1rem; font-weight: bold;">{routing.get('model_used')}</code><br/>
                                <span class="badge {tier_class}" style="font-size: 0.75rem; margin-top: 5px; display: inline-block;">{routing.get('tier').upper()}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                    with col_meta3:
                        st.markdown(
                            f"""
                            <div class="card" style="text-align: center; height: 130px; overflow: auto;">
                                <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">UZASADNIENIE BRAMKARZA</div>
                                <div style="font-size: 0.85rem; color: #e2e8f0; line-height: 1.2;">"{gatekeeper.get('reasoning')}"</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                    with col_meta4:
                        st.markdown(
                            f"""
                            <div class="card" style="text-align: center; height: 130px;">
                                <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">ZAKOTWICZONY CZAS SYSTEMOWY</div>
                                <code style="color: #cbd5e1; font-size: 1rem;">{system_time}</code>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # --- OUTCOME PANELS ---
                    st.markdown("### 📋 Wynik Pracy J.A.R.V.I.S.-a")
                    
                    # Summary card
                    st.markdown(
                        f"""
                        <div class="card" style="border-left: 5px solid #6366f1;">
                            <div class="card-title">📝 Podsumowanie Planu</div>
                            <p style="color: #f1f5f9; font-size: 1.05rem; line-height: 1.6; margin: 0;">{data.get('summary')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    col_left, col_right = st.columns(2)
                    
                    # Calendar events list
                    with col_left:
                        st.markdown("#### 📅 Wydarzenia w Kalendarzu (Google Calendar)")
                        events = data.get("events", [])
                        if not events:
                            st.info("Brak zaplanowanych wydarzeń w kalendarzu.")
                        else:
                            for i, event in enumerate(events):
                                location_html = f"<div style='font-size: 0.85rem; color: #a5b4fc; margin-top: 5px;'>📍 Lokalizacja: {event['location']}</div>" if event.get("location") else ""
                                desc_html = f"<p style='color: #cbd5e1; font-size: 0.9rem; margin-top: 5px;'>{event['description']}</p>" if event.get("description") else ""
                                st.markdown(
                                    f"""
                                    <div class="card">
                                        <div class="card-title" style="color: #c084fc;">
                                            📅 {event['title']}
                                        </div>
                                        <div style="font-size: 0.9rem; color: #94a3b8;">
                                            ⏱️ Czas: <b>{event['start_time']}</b> {f" do {event['end_time']}" if event.get('end_time') else ""}
                                        </div>
                                        {location_html}
                                        {desc_html}
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                
                    # Tasks checklist
                    with col_right:
                        st.markdown("#### 📋 Zadania To-Do (Google Tasks)")
                        tasks = data.get("tasks", [])
                        if not tasks:
                            st.info("Brak wygenerowanych zadań.")
                        else:
                            for i, task in enumerate(tasks):
                                # Determine priority badge color
                                p = task.get("priority", 0)
                                if p == 1:
                                    p_badge = "background-color: rgba(239,68,68,0.2); color:#f87171; border: 1px solid rgba(239,68,68,0.4);"
                                    p_text = "HIGH"
                                else:
                                    p_badge = "background-color: rgba(59,130,246,0.2); color:#60a5fa; border: 1px solid rgba(59,130,246,0.4);"
                                    p_text = "NORMAL"
                                    
                                due_html = f"<span style='color:#94a3b8; font-size: 0.85rem; margin-left: 10px;'>📅 Termin: <b>{task['due_date']}</b></span>" if task.get("due_date") else ""
                                desc_html = f"<p style='color: #cbd5e1; font-size: 0.9rem; margin-top: 5px;'>{task['description']}</p>" if task.get("description") else ""
                                
                                st.markdown(
                                    f"""
                                    <div class="card">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <div class="card-title" style="color: #818cf8; margin-bottom: 0;">
                                                ✔️ {task['title']}
                                            </div>
                                            <span style="font-size:0.7rem; padding: 2px 8px; border-radius: 10px; font-weight:600; text-transform:uppercase; {p_badge}">{p_text}</span>
                                        </div>
                                        <div style="margin-top: 5px;">
                                            {due_html}
                                        </div>
                                        {desc_html}
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                
                    # --- SYNC CONFIRMATION ---
                    st.markdown("---")
                    st.info("🔄 Integracje: Wszystkie powyższe wydarzenia i zadania zostały zsynchronizowane w tle z Google Calendar Mock i Google Tasks Mock (sprawdź konsolę serwera FastAPI).")
                    
                else:
                    st.error(f"Backend zwrócił błąd ({response.status_code}): {response.text}")
            except Exception as conn_err:
                st.error(f"Nie udało się połączyć z backendem FastAPI: {str(conn_err)}")
