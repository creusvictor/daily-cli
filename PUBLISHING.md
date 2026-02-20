# Guía de Publicación en PyPI

Esta guía te ayudará a publicar `daily-cli` en PyPI para que cualquiera pueda instalarlo con `pipx install daily-cli`.

## 📋 Pre-requisitos

✅ Paquete construido correctamente (`dist/` contiene `.whl` y `.tar.gz`)
✅ README.md completo y actualizado
✅ LICENSE incluido (MIT)
✅ pyproject.toml con toda la información necesaria

## 🔐 Paso 1: Crear cuentas en PyPI

### 1.1. Cuenta en PyPI (producción)

1. Ve a https://pypi.org/account/register/
2. Crea una cuenta con tu email: `victorcg98@gmail.com`
3. Verifica tu email
4. **IMPORTANTE**: Habilita 2FA (Two-Factor Authentication)

### 1.2. Cuenta en TestPyPI (opcional pero recomendado)

1. Ve a https://test.pypi.org/account/register/
2. Crea una cuenta (puede ser con el mismo email)
3. Verifica tu email

## 🔑 Paso 2: Crear API Token

### Para PyPI (producción):

1. Inicia sesión en https://pypi.org
2. Ve a Account Settings → API tokens
3. Click en "Add API token"
4. Scope: "Entire account" (la primera vez) o "Project: daily-cli" (después de la primera publicación)
5. Token name: "daily-cli-upload"
6. Copia el token (empieza con `pypi-...`)
7. **GUÁRDALO EN UN LUGAR SEGURO** - Solo se muestra una vez

### Para TestPyPI (opcional):

Repite el proceso en https://test.pypi.org

## 📦 Paso 3: Publicar el paquete

### Opción A: Publicar con `uv` (recomendado)

```bash
# 1. Asegúrate de estar en el directorio del proyecto
cd /home/victor/Personal/daily-cli

# 2. Publica en PyPI
uv publish

# Te pedirá:
# - Username: __token__
# - Password: <tu-api-token-que-copiaste>
```

### Opción B: Publicar con `twine`

```bash
# 1. Instalar twine
pipx install twine

# 2. Verificar el paquete antes de publicar
twine check dist/*

# 3. (Opcional) Probar primero en TestPyPI
twine upload --repository testpypi dist/*
# Username: __token__
# Password: <tu-test-pypi-token>

# 4. Publicar en PyPI
twine upload dist/*
# Username: __token__
# Password: <tu-pypi-token>
```

## 🔒 Paso 4: Guardar el token de forma segura

### Opción 1: Guardar en keyring (recomendado)

```bash
# Instalar keyring
pip install keyring

# Guardar el token
keyring set https://upload.pypi.org/legacy/ __token__

# Ahora puedes publicar sin escribir el token cada vez
twine upload dist/*
```

### Opción 2: Archivo de configuración `.pypirc`

```bash
# Crear archivo ~/.pypirc
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-TU_TOKEN_AQUI

[testpypi]
username = __token__
password = pypi-TU_TEST_TOKEN_AQUI
EOF

# Proteger el archivo
chmod 600 ~/.pypirc
```

## ✅ Paso 5: Verificar la publicación

Después de publicar, verifica:

1. Ve a https://pypi.org/project/daily-cli/
2. Verifica que toda la información se muestra correctamente
3. Prueba la instalación:

```bash
# Crear un entorno temporal
python -m venv /tmp/test-daily
source /tmp/test-daily/bin/activate

# Instalar desde PyPI
pip install daily-cli

# Probar
daily --help

# Limpiar
deactivate
rm -rf /tmp/test-daily
```

## 🔄 Paso 6: Publicar actualizaciones

Para publicar una nueva versión:

1. Actualizar el número de versión en `pyproject.toml`:

```toml
version = "1.0.1"  # o 1.1.0, 2.0.0, etc.
```

2. Limpiar build anterior:

```bash
rm -rf dist/
```

3. Construir nueva versión:

```bash
uv build
```

4. Publicar:

```bash
uv publish
# o
twine upload dist/*
```

## 📊 Versionado Semántico

Usa [Semantic Versioning](https://semver.org/):

- **1.0.0 → 1.0.1**: Bug fixes (PATCH)
- **1.0.0 → 1.1.0**: New features, backwards compatible (MINOR)
- **1.0.0 → 2.0.0**: Breaking changes (MAJOR)

## 🎯 Checklist pre-publicación

- [ ] Tests pasan (`uv run pytest`)
- [ ] README.md actualizado
- [ ] Versión actualizada en `pyproject.toml`
- [ ] CHANGELOG.md actualizado (opcional pero recomendado)
- [ ] Build exitoso (`uv build`)
- [ ] Paquete verificado (`twine check dist/*`)
- [ ] Git tag creado para la versión (`git tag v1.0.0`)

## 🚀 Después de publicar

1. Crear un release en GitHub:
   - Ve a https://github.com/creusvictor/daily-cli/releases
   - Click "Create a new release"
   - Tag: `v1.0.0`
   - Title: `v1.0.0 - Initial Release`
   - Description: Changelog de esta versión

2. Actualizar el README con badge de PyPI:

```markdown
[![PyPI version](https://badge.fury.io/py/daily-cli.svg)](https://pypi.org/project/daily-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/daily-cli.svg)](https://pypi.org/project/daily-cli/)
[![Downloads](https://pepy.tech/badge/daily-cli)](https://pepy.tech/project/daily-cli)
```

3. Anunciar en redes sociales / comunidades relevantes

## 🆘 Troubleshooting

### "File already exists"

PyPI no permite re-subir la misma versión. Debes incrementar la versión en `pyproject.toml`.

### "Invalid distribution file"

```bash
# Limpiar y reconstruir
rm -rf dist/ build/ *.egg-info
uv build
```

### "Authentication failed"

- Verifica que estás usando `__token__` como username
- Verifica que el token no tiene espacios al principio/final
- Verifica que el token no ha expirado

## 📚 Recursos adicionales

- PyPI: https://pypi.org
- Packaging Guide: https://packaging.python.org
- Twine docs: https://twine.readthedocs.io
- uv publish docs: https://docs.astral.sh/uv/guides/publish/
