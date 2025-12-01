# 📱 WhatsApp Sentiment Analysis API

Sistema de análisis de sentimientos para mensajes de WhatsApp utilizando IA (Google Gemini), con WebSockets en tiempo real, caché Redis y almacenamiento MongoDB.

🌐 **URL de Producción**: [https://whatsapp-sentiment-api-production-98fb.up.railway.app](https://whatsapp-sentiment-api-production-98fb.up.railway.app)

---

## 🎯 Descripción del Proyecto

Este proyecto es una API backend desarrollada en Python/Flask que:

- ✅ Recibe mensajes de WhatsApp vía webhooks (Twilio)
- 🤖 Analiza el sentimiento de los mensajes usando Google Gemini AI
- 💾 Almacena mensajes y análisis en MongoDB
- ⚡ Utiliza Redis para caché y colas de mensajes
- 🔄 Procesa mensajes en background con workers
- 📡 Envía actualizaciones en tiempo real vía WebSockets (Socket.IO)
- 📊 Proporciona dashboard con estadísticas de sentimientos

---

## 🏗️ Arquitectura

```
┌─────────────┐         ┌──────────────┐
│  WhatsApp   │────────▶│   Webhook    │
│   (Twilio)  │         │   Endpoint   │
└─────────────┘         └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ Redis Queue  │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │    Worker    │
                        │   Process    │
                        └──────┬───────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
         ┌───────────┐  ┌───────────┐  ┌───────────┐
         │  Gemini   │  │  MongoDB  │  │  Socket   │
         │    AI     │  │  Storage  │  │    IO     │
         └───────────┘  └───────────┘  └───────────┘
                                              │
                                              ▼
                                       ┌───────────┐
                                       │  Frontend │
                                       │  Clients  │
                                       └───────────┘
```

### Componentes Principales

1. **Flask App**: Servidor HTTP principal con endpoints REST
2. **Worker Process**: Procesador background para análisis de mensajes
3. **MongoDB**: Base de datos principal para persistencia
4. **Redis**: Sistema de caché y cola de mensajes
5. **Socket.IO**: WebSockets para comunicación en tiempo real
6. **Google Gemini**: Modelo de IA para análisis de sentimientos

---

## 🛠️ Tecnologías

### Backend

- **Python 3.11**: Lenguaje principal
- **Flask 3.0**: Framework web
- **Flask-SocketIO 5.3**: WebSockets en tiempo real
- **Gunicorn + Eventlet**: Servidor WSGI para producción
- **PyMongo 4.6**: Cliente MongoDB
- **Redis 5.0**: Cliente Redis

### IA y Análisis

- **Google Generative AI (Gemini)**: Análisis de sentimientos

### Base de Datos

- **MongoDB 7.0**: Almacenamiento de mensajes
- **Redis 7**: Caché y cola de mensajes

### DevOps

- **Docker & Docker Compose**: Contenedorización
- **Railway**: Hosting de servicios (MongoDB, Redis, App)

---

## 📦 Requisitos Previos

### Para Desarrollo Local

- **Docker Desktop**
- **Docker Compose**
- **Git**
- Cuenta de **Google Cloud** (para Gemini API Key)
- Cuenta de **Twilio** (opcional, para webhooks de WhatsApp)

### Para Despliegue en la Nube

- Cuenta en **Railway** (para MongoDB, Redis y/o App)
- Cuenta en **Google Cloud** (Gemini API)

---

## 🚀 Desarrollo Local con Docker

Este proyecto utiliza **Docker** y **Docker Compose** para facilitar el desarrollo local. Docker permite ejecutar toda la aplicación y sus dependencias (MongoDB, Redis) en contenedores aislados sin necesidad de instalar nada localmente.

### 🐳 ¿Qué es Docker y Docker Compose?

**Docker** es una plataforma que permite empaquetar aplicaciones en contenedores. Un contenedor incluye todo lo necesario para ejecutar la aplicación (código, runtime, librerías, etc.) de forma aislada.

**Docker Compose** es una herramienta para definir y ejecutar aplicaciones multi-contenedor. Con un archivo YAML, defines todos los servicios (app, MongoDB, Redis, worker) y Docker Compose los levanta todos juntos.

### 📥 Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/BryanJGomez/whatsapp-sentiment-api.git
cd whatsapp-sentiment-api
```

### ⚙️ Paso 2: Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env
```

**Importante:**

- El mismo `.env` funciona tanto para desarrollo como producción
- Para desarrollo: usa `docker-compose.dev.yml` (Flask con hot-reload)
- Para producción: usa `docker-compose.yml` (Gunicorn + eventlet)

**Nota importante:** Los nombres `mongo` y `redis` en las URIs corresponden a los **nombres de los servicios** definidos en `docker-compose.yml`. Docker Compose crea una red interna donde los contenedores pueden comunicarse usando estos nombres.

### 🚀 Paso 3: Levantar los Servicios con Docker Compose

Docker Compose permite iniciar todos los servicios con un solo comando:

#### Opción A: Desarrollo con docker-compose.dev.yml (Recomendado)

Este archivo incluye MongoDB y Redis locales, ideal para desarrollo:

```bash
# Iniciar todos los servicios (app + worker + mongo + redis)
docker-compose -f docker-compose.dev.yml up

# O en modo detached (background)
docker-compose -f docker-compose.dev.yml up -d

# Ver logs en tiempo real
docker-compose -f docker-compose.dev.yml logs -f

# Ver logs de un servicio específico
docker-compose -f docker-compose.dev.yml logs -f app
docker-compose -f docker-compose.dev.yml logs -f worker
docker-compose -f docker-compose.dev.yml logs -f mongo
docker-compose -f docker-compose.dev.yml logs -f redis
```

**¿Qué hace este comando?**

1. Construye la imagen Docker de tu aplicación (usa el `Dockerfile`)
2. Descarga las imágenes de MongoDB 7.0 y Redis 7
3. Crea una red Docker llamada `backend` para que los contenedores se comuniquen
4. Levanta 4 contenedores:
   - `app`: Aplicación Flask directa (dev_server.py) con hot-reload
   - `worker`: Procesador de mensajes en background
   - `mongo`: Base de datos MongoDB
   - `redis`: Cache y cola de mensajes
5. Monta tu código local en `/app/` dentro del contenedor (hot reload automático)

**Diferencias entre dev y producción:**

- **Desarrollo** (`docker-compose.dev.yml`): Usa `python dev_server.py` → Flask puro, hot-reload, WebSockets estables
- **Producción** (`docker-compose.yml`): Usa `gunicorn + eventlet` → Mejor rendimiento, sin hot-reload

#### Opción B: Producción simulada con docker-compose.yml

Este archivo es más simple, asume que MongoDB y Redis están externos (Railway, por ejemplo):

```bash
# Iniciar solo app y worker con gunicorn (producción)
docker-compose up -d
```

### 🛑 Paso 5: Detener los Servicios

```bash
# Detener servicios (mantiene datos en volúmenes)
docker-compose -f docker-compose.dev.yml down

# Detener y eliminar volúmenes (BORRA TODOS LOS DATOS de MongoDB y Redis)
docker-compose -f docker-compose.dev.yml down -v

# Detener pero mantener contenedores
docker-compose -f docker-compose.dev.yml stop

# Reiniciar servicios detenidos
docker-compose -f docker-compose.dev.yml start

# Reconstruir imágenes (después de cambios en Dockerfile o requirements.txt)
docker-compose -f docker-compose.dev.yml up --build
```

---

### 🔄 Actualización y CI/CD

Railway hace deploy automático cuando haces push a `main`:

```bash
# 1. Hacer cambios en tu código local
git add .
git commit -m "feat: nueva funcionalidad"

# 2. Push a GitHub
git push origin main

# 3. Railway detecta el push y despliega automáticamente
# Ver progreso en el dashboard de Railway
```

---

## 📁 Estructura del Proyecto

```
whatsapp-sentiment-api/
├── src/
│   ├── main.py                      # Punto de entrada principal
│   ├── config/
│   │   └── settings.py              # Configuración centralizada
│   ├── app/
│   │   ├── dashboard/               # Módulo de dashboard
│   │   │   ├── http/
│   │   │   │   └── dashboard_blueprint.py
│   │   │   ├── repositories/
│   │   │   │   └── dasboard_repository.py
│   │   │   └── usecases/
│   │   │       └── manage_dashboard_usecase.py
│   │   └── messages/                # Módulo de mensajes
│   │       ├── entities/
│   │       │   └── message.py
│   │       ├── http/
│   │       │   └── webhook_blueprint.py
│   │       ├── repositories/
│   │       │   └── message_repository.py
│   │       ├── services/
│   │       │   └── sentiment_analysis_service.py
│   │       └── usecases/
│   │           └── message_usecases.py
│   ├── frameworks/                  # Infraestructura
│   │   ├── cache/
│   │   │   └── redis_cache.py
│   │   ├── db/
│   │   │   ├── mongo.py
│   │   │   ├── redis.py
│   │   │   ├── collections.py
│   │   │   └── serializers.py
│   │   ├── http/
│   │   │   ├── flask.py
│   │   │   ├── decorators.py
│   │   │   └── error_handlers.py
│   │   ├── logging/
│   │   │   └── logger.py
│   │   ├── queue/
│   │   │   └── message_queue.py
│   │   └── websocket/
│   │       └── socketio_manager.py
│   ├── scripts/
│   │   ├── init_database.py         # Inicialización de BD
│   │   └── update_schema.py         # Actualización de esquema
│   └── utils/
│       └── datetime_utils.py
├── worker.py                        # Worker de procesamiento
├── dockerfile                       # Imagen Docker
├── docker-compose.yml               # Orquestación Docker (producción)
├── docker-compose.dev.yml           # Orquestación Docker (desarrollo)
├── gunicorn_config.py              # Configuración Gunicorn
├── requirements.txt                 # Dependencias de producción
├── requirements-dev.txt             # Dependencias de desarrollo
├── runtime.txt                      # Versión de Python
└── .env.example                     # Plantilla de variables de entorno
```

### Patrones de Arquitectura

El proyecto sigue **Clean Architecture** con separación en capas:

1. **Entities**: Modelos de dominio (`message.py`)
2. **Use Cases**: Lógica de negocio (`message_usecases.py`)
3. **Repositories**: Acceso a datos (`message_repository.py`)
4. **Services**: Servicios externos (`sentiment_analysis_service.py`)
5. **Frameworks**: Implementaciones técnicas (Flask, MongoDB, Redis)
6. **HTTP**: Controllers/Blueprints (APIs REST)

---

### Convenciones de Commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva característica
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Formato, no cambia código
- `refactor:` Refactorización
- `test:` Agregar/modificar tests
- `chore:` Mantenimiento

---

## 📝 Notas Adicionales

### Obtener API Key de Google Gemini

1. Ir a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crear un nuevo proyecto o usar uno existente
3. Generar API Key
4. Copiar la key al archivo `.env`

### Configurar Twilio para WhatsApp

1. Numero configurado para este proyecto en sandbox +14155238886

#### Paso 1: Crear cuenta y obtener Sandbox

1. Crear cuenta en [Twilio](https://www.twilio.com)
2. Ir a **Messaging** → **Try it out** → **Send a WhatsApp message**
3. Verás el **número de sandbox de Twilio** (ej: `+1 415 523 8886`)
4. **IMPORTANTE**: Para activar tu WhatsApp personal con el sandbox:
   - Abre WhatsApp en tu teléfono
   - Inicia un chat con el número del sandbox (ej: `+1 415 523 8886`)
   - Envía el mensaje que te muestra Twilio (ej: `join current-doctor`)
   - Recibirás una confirmación de Twilio
   - ⚠️ **Sin este paso, tus mensajes NO llegarán a tu aplicación**
   - La conexión dura 72 horas, después debes repetir el proceso

#### Paso 2: Configurar Webhook

1. En Twilio Console, ve a **Messaging** → **Settings** → **WhatsApp Sandbox Settings**
2. En **"When a message comes in"**, configura:
   - **URL**: `https://tu-app.railway.app/webhook/whatsapp` (o tu ngrok URL para desarrollo local)
   - **Método**: `POST`
3. Guarda los cambios

#### Paso 3: Probar la Integración

1. Asegúrate de que tu aplicación esté corriendo (`docker-compose up`)
2. Envía un mensaje de WhatsApp al número del sandbox desde tu teléfono
3. Verifica en los logs que el mensaje fue recibido:
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f app
   docker-compose -f docker-compose.dev.yml logs -f worker
   ```
4. El análisis de sentimientos se procesará en background

#### 🔧 Desarrollo Local con ngrok

Si quieres probar webhooks en tu máquina local:

```bash
# Instalar ngrok
brew install ngrok  # macOS
# O descargar desde https://ngrok.com/download

# Exponer tu puerto local (8301 por defecto)
ngrok http 8301

# Copiar la URL HTTPS que ngrok te da (ej: https://abc123.ngrok.io)
# Actualizar el webhook en Twilio con: https://abc123.ngrok.io/webhook/whatsapp
```

---

## 📄 Licencia

Este proyecto es de código privado. Todos los derechos reservados.

---

## 📧 Contacto

**Bryan J. Gomez**

- GitHub: [@BryanJGomez](https://github.com/BryanJGomez)

---

**¿Problemas o preguntas?** Abre un issue en GitHub.
