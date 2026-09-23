#!/usr/bin/env bash
# Instalador de Sword para Linux y macOS
set -e

cat <<'EOF'

  ==============================================
   Sword - Limpia y une Excel en segundos
   Instalador para Linux / macOS
  ==============================================

EOF

if ! command -v python3 >/dev/null 2>&1; then
    echo "  [ERROR] No se encontró Python 3."
    echo "  Instálalo con el gestor de paquetes de tu sistema:"
    echo "    Debian/Ubuntu:  sudo apt install python3 python3-venv python3-pip"
    echo "    Fedora:         sudo dnf install python3 python3-virtualenv python3-pip"
    echo "    Arch:           sudo pacman -S python python-pip"
    exit 1
fi

echo "  [1/4] Creando entorno virtual..."
python3 -m venv .venv

echo "  [2/4] Actualizando pip..."
.venv/bin/python -m pip install --upgrade pip >/dev/null

echo "  [3/4] Instalando dependencias (primera vez puede tardar)..."
.venv/bin/pip install -r requirements.txt

echo "  [4/4] Instalando Sword..."
.venv/bin/pip install -e .

echo
echo "  =============================================="
echo "   Listo! Sword quedó instalado correctamente."
echo "  =============================================="
echo
echo "  Uso:"
echo "    .venv/bin/sword CARPETA_CON_EXCELS"
echo
echo "  Atajo (después de esto, basta escribir 'sword'):"
echo "    echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc && . ~/.bashrc"
echo
echo "  O activa el entorno de una vez:"
echo "    source .venv/bin/activate"
echo