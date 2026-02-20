# 🚀 Publicación Automática en PyPI con GitHub Actions

Esta guía explica cómo publicar `daily-cli` en PyPI usando **Trusted Publishers** (sin necesidad de tokens manualmente).

## 🎯 Ventajas del Trusted Publisher

✅ **Más seguro**: No necesitas guardar tokens/contraseñas
✅ **Automático**: Se publica al crear un release en GitHub
✅ **Menos errores**: No hay riesgo de tokens expirados o filtrados
✅ **Recomendado por PyPI**: Es la forma oficial moderna

## 📋 Configuración Inicial (Una sola vez)

### 1. Crear cuenta en PyPI

1. Ve a https://pypi.org/account/register/
2. Usa tu email: `victorcg98@gmail.com`
3. Verifica el email
4. **Habilita 2FA** (obligatorio)

### 2. Configurar Trusted Publisher en PyPI

Basándome en tu captura de pantalla, la configuración es:

```
PyPI Nombre del proyecto: daily-cli
Propietario: creusvictor
Nombre de repositorio: daily-cli
Nombre del flujo de trabajo: flujodetrabajo.yml
Environment name: pypi
```

**Pasos en PyPI**:

1. Ve a https://pypi.org/manage/account/publishing/
2. Click en "Add a new pending publisher"
3. Rellena:
   - **PyPI Project Name**: `daily-cli`
   - **Owner**: `creusvictor`
   - **Repository name**: `daily-cli`
   - **Workflow name**: `flujodetrabajo.yml`
   - **Environment name**: `pypi`
4. Click "Add"

> ⚠️ **IMPORTANTE**: Esto crea un "pending publisher". La primera vez que publiques, 
> PyPI creará automáticamente el proyecto `daily-cli`.

### 3. Crear Environment en GitHub

1. Ve a tu repositorio: https://github.com/creusvictor/daily-cli
2. Ve a **Settings** → **Environments**
3. Click "New environment"
4. Nombre: `pypi` (debe coincidir con lo configurado en PyPI)
5. Click "Configure environment"
6. (Opcional) Añade protección:
   - ✓ Required reviewers: Tú mismo (para aprobar antes de publicar)
   - ✓ Wait timer: 0 minutes

## 🚀 Cómo Publicar una Nueva Versión

### Paso 1: Actualizar versión

Edita `pyproject.toml`:

```toml
version = "1.0.0"  # Cambiar a 1.0.1, 1.1.0, etc.
```

### Paso 2: Commit y push

```bash
git add pyproject.toml
git commit -m "Bump version to 1.0.0"
git push origin main
```

### Paso 3: Crear Git tag

```bash
git tag v1.0.0
git push origin v1.0.0
```

### Paso 4: Crear Release en GitHub

**Opción A: Desde la web**

1. Ve a https://github.com/creusvictor/daily-cli/releases
2. Click "Create a new release"
3. Click "Choose a tag" → Selecciona `v1.0.0`
4. Release title: `v1.0.0 - Initial Release`
5. Describe los cambios:
   ```markdown
   ## 🎉 Initial Release
   
   ### Features
   - ✅ Log daily work (`daily did`, `plan`, `block`, `meeting`)
   - ✅ Cheat sheet for standups (`daily cheat`)
   - ✅ Interactive search with fzf (`daily search`)
   - ✅ Tag support and filtering
   - ✅ Markdown-based storage
   ```
6. Click "Publish release"

**Opción B: Desde terminal con gh**

```bash
gh release create v1.0.0 \
  --title "v1.0.0 - Initial Release" \
  --notes "Initial release of daily-cli"
```

### Paso 5: ¡Automático! 🎉

El workflow de GitHub Actions se ejecutará automáticamente y:

1. ✅ Construirá el paquete
2. ✅ Lo publicará en PyPI
3. ✅ En ~2 minutos estará disponible para instalar

**Verificar**:

1. Ve a https://github.com/creusvictor/daily-cli/actions
2. Verás el workflow "Publish to PyPI" ejecutándose
3. Cuando termine (marca verde ✓), el paquete estará en PyPI
4. Verifica en https://pypi.org/project/daily-cli/

## 🔄 Flujo Completo para Actualizaciones

```bash
# 1. Editar código/features
vim daily/core.py

# 2. Actualizar versión
vim pyproject.toml  # Cambiar version = "1.0.1"

# 3. Commit
git add .
git commit -m "Add new feature X"
git push

# 4. Tag
git tag v1.0.1
git push origin v1.0.1

# 5. Release (esto dispara la publicación automática)
gh release create v1.0.1 \
  --title "v1.0.1" \
  --notes "### Bug Fixes\n- Fixed issue X\n- Improved Y"

# ✨ En 2 minutos → disponible en PyPI
```

## 📊 Versionado Semántico

Usa [Semantic Versioning](https://semver.org/):

- `1.0.0 → 1.0.1`: Bug fixes (PATCH)
- `1.0.0 → 1.1.0`: New features, backwards compatible (MINOR)
- `1.0.0 → 2.0.0`: Breaking changes (MAJOR)

## ✅ Checklist Pre-Release

Antes de crear un release, verifica:

- [ ] Tests pasan: `uv run pytest`
- [ ] Versión actualizada en `pyproject.toml`
- [ ] Código commiteado y pusheado
- [ ] CHANGELOG.md actualizado (opcional)
- [ ] README.md actualizado si hay cambios en uso

## 🆘 Troubleshooting

### "Trusted publishing exchange failure"

**Causa**: El nombre del workflow, environment o repo no coinciden con PyPI.

**Solución**: Verifica que en PyPI tienes exactamente:
- Workflow: `flujodetrabajo.yml`
- Environment: `pypi`
- Owner: `creusvictor`
- Repo: `daily-cli`

### "Package already exists"

**Causa**: La versión ya fue publicada.

**Solución**: Incrementa el número de versión en `pyproject.toml`.

### El workflow no se ejecuta

**Causa**: El workflow solo se ejecuta cuando creas un **release**, no con tags solamente.

**Solución**: Crea el release en GitHub (no solo el tag).

## 📚 Recursos

- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions Publishing](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Semantic Versioning](https://semver.org/)

## 🎯 Primera Publicación

Para la primera publicación (v1.0.0):

```bash
cd /home/victor/Personal/daily-cli

# 1. Asegurar que todo está commiteado
git add .
git commit -m "Prepare for first release"
git push

# 2. Crear tag
git tag v1.0.0
git push origin v1.0.0

# 3. Crear release
gh release create v1.0.0 \
  --title "v1.0.0 - Initial Release" \
  --notes-file RELEASE_NOTES.md

# O hazlo desde la web: https://github.com/creusvictor/daily-cli/releases/new
```

¡Y listo! GitHub Actions se encargará de publicar en PyPI automáticamente. 🚀
