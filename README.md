# 🤖 Ark‑bot

Bot de Discord para administración de una tribu de **ARK**, centrado en la gestión de roles, vouch, cuotas y utilidades para la comunidad.

---

## 📌 Características

- ⚙️ Modularidad con *cogs* para separar funcionalidades
- 🗳️ Sistema de vouch que los administradores pueden confirmar
- 🎭 Asignación de roles de idioma y permisos
- 📦 Gestión de cuotas y verificación de entregas
- 🔢 Comandos útiles (`!bp`, `!costbp`, `!quota`, etc.)
- 💾 Persistencia de datos en archivos planos (`txt`, `json`)

---

## 📂 Estructura del proyecto

```
Ark-bot/
├── cogs/               # Extensiones/módulos del bot
├── config.py           # Configuración: token, prefijo, etc.
├── main.py             # Punto de entrada principal
├── requirements.txt    # Dependencias de Python
├── udiscordid.txt      # IDs de usuarios de Discord
├── vote_vouch.txt      # Votos/vouch registrados
└── README.md           # Esta documentación
```

---

## 🚀 Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/F4R3Juan58/Ark-bot.git
   cd Ark-bot
   ```

2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate    # Windows
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura `config.py` con tu **token de Discord** y el prefijo de comandos.

5. Ejecuta el bot:
   ```bash
   python main.py
   ```

---

## ⚙️ Uso

Comandos disponibles (ejemplos):
- `!vouch @usuario` → enviar vouch
- `!quota` → mostrar cuota pendiente
- `!bp número` → mostrar información de blueprint
- `!costbp número` → calcular coste

---

## 📜 Requisitos

- Python 3.9+
- Librería incluida en `requirements.txt` (ej. `discord.py`)
- Token de bot de Discord
- Permisos de administración en el servidor

---

## 👨‍💻 Autor

Desarrollado por **Juan Gabriel Gallardo Martín**  
🔗 [GitHub](https://github.com/F4R3Juan58)
