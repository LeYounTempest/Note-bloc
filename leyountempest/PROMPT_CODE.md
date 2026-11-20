# Prompt para Claude Code

Pega esto tal cual en Claude Code, dentro de la carpeta de este proyecto:

---

Este proyecto es el portafolio personal de LeYounTempest (Walter González, Guatemala): un sitio estático de una sola página, `index.html`, sin build ni dependencias. Las imágenes están en `assets/`. Responde y comenta el código en español.

**Reglas de diseño (no las cambies sin que te lo pida):**
- Tipografía: Tinos (estilo Times New Roman), con fallback "Times New Roman", Times, serif.
- Paleta (variables en `:root`): fondo negro-morado #0b0610, paneles #160d1d, acento rosa corinto #e0527e y #9c1f46, morado #9b6bd6.
- La portada lleva a Aurelia, mi OC (`assets/aurelia-cafe.jpg`), con pétalos de glicina animados en canvas.
- Es un solo archivo HTML con CSS y JS inline. Mantenlo así, sin frameworks.

**Tareas:**
1. Inicializa un repositorio git y súbelo a GitHub con `gh`, como repo público llamado `leyountempest`. Activa GitHub Pages desde la rama `main`, carpeta raíz. Dame la URL final.
2. Añade en el `<head>`: favicon a partir de `assets/aurelia-retrato.jpg` (versión 64×64 y 180×180), metadatos Open Graph y Twitter con `assets/aurelia-cafe.jpg` como imagen, y `<link rel="canonical">` con la URL de Pages.
3. Crea `README.md` corto que explique cómo agregar imágenes y avances.
4. Revisa accesibilidad (alt, contraste, foco visible, navegación con teclado) y rendimiento (imágenes con `loading="lazy"` salvo la portada, `width` y `height`). Corrige solo lo necesario.

**Pendientes que haré yo después (déjalos listos, no los inventes):**
- Capturas: `assets/alice.jpg`, `assets/modelo-1.jpg`, `modelo-2.jpg`, `modelo-3.jpg`. Cuando existan, aparecen solas. Los textos de las fichas se cambian en el HTML.
- Bitácora del RTS: para cada avance, copia un `<li>` de la lista `.log` y ponlo arriba con la fecha nueva.
- Correo de contacto: hoy dice "próximamente". No pongas uno inventado.
- Precios de servicios: hoy dice "cotizo sin compromiso". No pongas cifras.

Al terminar, muéstrame el diff resumido y la URL publicada.
