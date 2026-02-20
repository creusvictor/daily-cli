#!/bin/bash
# Script para preparar la primera release de daily-cli en PyPI

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║  🚀 Preparando primera release de daily-cli v1.0.0            ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml no encontrado"
    echo "   Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar que los tests pasan
echo "📋 1/6: Ejecutando tests..."
if uv run pytest; then
    echo "✅ Tests pasados"
else
    echo "❌ Error: Los tests no pasan"
    echo "   Arregla los tests antes de continuar"
    exit 1
fi

# Add all changes
echo ""
echo "📦 2/6: Añadiendo archivos al stage..."
git add .
echo "✅ Archivos añadidos"

# Commit
echo ""
echo "💾 3/6: Haciendo commit..."
git commit -m "feat: Add search command and prepare for PyPI release

- Add interactive search with fzf (daily search)
- Tag filtering support
- Simplified display format (date, weekday, tags)
- GitHub Actions workflow for automated PyPI publishing
- Complete documentation and publishing guides
- Tests for search functionality (9 tests)

Ready for v1.0.0 release"
echo "✅ Commit creado"

# Push to origin
echo ""
echo "🌐 4/6: Pusheando a GitHub..."
git push origin main
echo "✅ Código pusheado a GitHub"

# Create tag
echo ""
echo "🏷️  5/6: Creando tag v1.0.0..."
git tag v1.0.0
git push origin v1.0.0
echo "✅ Tag v1.0.0 creado y pusheado"

# Instructions for release
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║  ✅ Preparación completada                                    ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1️⃣  Configurar Trusted Publisher en PyPI:"
echo "   → https://pypi.org/manage/account/publishing/"
echo "   → Add new pending publisher con estos datos:"
echo "      - PyPI Project: daily-cli"
echo "      - Owner: creusvictor"
echo "      - Repository: daily-cli"
echo "      - Workflow: flujodetrabajo.yml"
echo "      - Environment: pypi"
echo ""
echo "2️⃣  Crear environment en GitHub:"
echo "   → https://github.com/creusvictor/daily-cli/settings/environments"
echo "   → New environment → Nombre: pypi"
echo ""
echo "3️⃣  Crear Release en GitHub:"
echo ""
echo "   Opción A (Web):"
echo "   → https://github.com/creusvictor/daily-cli/releases/new"
echo "   → Tag: v1.0.0 (ya existe)"
echo "   → Title: v1.0.0 - Initial Release"
echo "   → Description: Copy contenido de RELEASE_NOTES.md"
echo "   → Publish release"
echo ""
echo "   Opción B (Terminal):"
echo "   gh release create v1.0.0 \\"
echo "     --title \"v1.0.0 - Initial Release\" \\"
echo "     --notes-file RELEASE_NOTES.md"
echo ""
echo "4️⃣  ¡Publicación automática!"
echo "   → GitHub Actions publicará en PyPI automáticamente"
echo "   → Monitorea: https://github.com/creusvictor/daily-cli/actions"
echo "   → En ~2 min estará en: https://pypi.org/project/daily-cli/"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
