#!/usr/bin/env bash
# =====================================================================
# J.A.R.V.I.S. Mark I - GitHub CLI Repo Setup & Issues Initialization
# =====================================================================

# Ensure the script exits on error
set -e

echo "🚀 Starting GitHub repository setup for jarvis-mark-1..."

# 1. Initialize Git repository locally if not already initialized
if [ ! -d ".git" ]; then
    echo "⚙️ Initializing local Git repository..."
    git init
fi

# Add all files and make initial commit
echo "📝 Committing project files..."
git add .
git commit -m "Initial commit - J.A.R.V.I.S. Mark I Skeleton" || echo "Nothing to commit (or already committed)."

# 2. Create the private repository on GitHub and push the code
echo "🔑 Creating private GitHub repository 'jarvis-mark-1'..."
# Uses the current directory (.) as source, sets remote 'origin', and pushes the 'main' or current branch
gh repo create jarvis-mark-1 --private --source=. --remote=origin --push

# 3. Create the 4 structural issues
echo "🏷️ Creating labels on GitHub..."
gh label create setup --color "E9967A" --description "Initial setup and project structure" || echo "Label 'setup' already exists."
gh label create backend --color "8FBC8F" --description "FastAPI backend services" || echo "Label 'backend' already exists."
gh label create ai --color "4682B4" --description "AI modeling and routing" || echo "Label 'ai' already exists."
gh label create frontend --color "DDA0DD" --description "Streamlit frontend interface" || echo "Label 'frontend' already exists."

echo "📋 Creating issues on GitHub..."

gh issue create \
  --title "Setup: Szkielet projektu" \
  --body "Zadanie polega na przygotowaniu struktury katalogów, konfiguracji środowiska (.env), wymagań w requirements.txt oraz pliku README.md." \
  --label "setup"

gh issue create \
  --title "Backend: FastAPI, CORS, Logowanie" \
  --body "Implementacja serwera FastAPI z obsługą middleware CORS, endpointem /process oraz zaawansowanym systemem logowania przekierowań modeli." \
  --label "backend"

gh issue create \
  --title "AI: Dynamiczny dobór modelu i świadomość czasu" \
  --body "Implementacja klasy JarvisAgent w agent.py obsługującej Bramkarza (cheap model) i Wykonawcę (expensive model) z wstrzykiwaniem czasu systemowego." \
  --label "ai"

gh issue create \
  --title "Frontend: UI w Streamlit" \
  --body "Stworzenie intuicyjnego interfejsu użytkownika w Streamlit pozwalającego przesyłać chaotyczne polecenia i wizualizować ustrukturyzowane plany zadań i wydarzeń." \
  --label "frontend"

echo "✅ GitHub setup complete! Repository created and 4 issues initialized."
