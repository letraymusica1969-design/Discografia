# Discografia — Sandro Saavedra

Box set **«Canciones de una ciudad»** — un box set de seis discos en vinilo, 79 canciones, del autor **Sandro Saavedra** (música y letra).

## Guía rápida (leer primero)

Este repositorio es la fuente de trabajo completa. Contiene: audio (MP3), portadas (front/back), el generador de portadas, los datos del box set y el sitio web.

### Contexto que debe conocer la IA/persona que continúe

- **Autor:** Sandro Saavedra. Créditos en el dorso: «Música y letra: Sandro Saavedra / Arreglos: Estudio Central / Producción: El Desván del Vinilo — 2026». Los créditos del autor van en la **esquina inferior derecha** del dorso.
- **Box set:** 6 discos (VOL.01–06): Medianoche, Ciudad de Neon, Ochentas, Llamas, Euforia, Directo. 79 temas en total. Calibrados por BPM, de la balada nocturna a la euforia.
- **Fuente de verdad de datos:** `box_set.json` (títulos, tracklists con BPM y duraciones, totales por disco, nº canciones).
- **Portadas:** se generan con `make_covers.py` (v3 artística: Perlin fractal en NumPy puro — sin SciPy), a 1500×1500 JPG. **No llevar número de disco a la portada** (ni «NO. 01/05», ni «VOL. X/5», ni numeración fantasma). El nº de volumen es un elemento decorativo solo de la web.
- **No remasterizar audio.** Los MP3 ya están finales. No convertir/analizar con herramientas externas sin aprobación.
- El asistente/IA **no puede previsualizar imágenes**: validar portadas por código (tamaño, contraste, paletas) y pedir confirmación al autor.

## Estructura

```
box_set.json            datos maestros del box set
make_covers.py          genera las 10 tapas (front+back) en Discos/Tapas/
Discos/
  Tapas/                portadas finales (Disco_N_<nombre>_front/back.jpg)
  <Discos>/             audio por disco (79 MP3)
web/                    sitio web Next.js (App Router, JSX)
  data/box.json         copia de box_set.json para el sitio
  public/covers/        portadas servidas por la web
  public/fonts/         fuentes locales (Agency, Bodoni, BookAntiqua)
INFORME.md              bitácora del proyecto
```

## Cómo seguir trabajando

### 1) Preparar el entorno

- Git, Node.js (LTS 20 o 22) y Python 3 con NumPy y Pillow (portadas).

### 2) Clonar y verificar

```bash
git clone https://github.com/letraymusica1969-design/Discografia.git
cd Discografia
```

Repo **público** → no requiere login para clonar. Para **subir cambios** ejecutar una vez: `gh auth login`.

### 3) Sitio web

```bash
cd web
npm install        # regenera node_modules (no está en el repo)
npm run dev        # http://localhost:3000
```

- Rutas principales: `/` (portada), `/musica` (Archivo), `/disco/<slug>` (ficha con tracklist).
- Después de aprobar, preparar producción: `npm run build` y deploy a **Vercel**.
- Cambios de contenido: editar `web/lib/data.js` o `web/data/box.json` y re-generar.

### 4) Portadas

```bash
python make_covers.py    # regenera los 10 JPG en Discos/Tapas/
```

- Si cambian las portadas, copiarlas a `web/public/covers/` para el sitio.

## Convenciones y estado

- Identidad git local ya configurada en la máquina original; en la nueva configurar `git config user.name` / `user.email` si se va a hacer commit.
- `.gitignore`: excluye `node_modules/`, `.next/`, `dev.log`, credenciales. No fuerzarlos en el repo.
- Publicado bajo cuenta `letraymusica1969-design`. Rama: `main`.