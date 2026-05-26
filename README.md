# Central de Plantillas IT: Infraestructura Contenerizada y Observabilidad en OpenStack

Este proyecto consiste en una aplicación web interactiva diseñada para optimizar los tiempos de respuesta del equipo de soporte técnico mediante la centralización y copia rápida de respuestas e instructivos centralizados anteriormente trabajados y gestionados en la herramienta: Evernote.

Más allá de la funcionalidad de la aplicación (la cual consiste en una interfaz minimalista con buscador e instructivos/respuestas pre seteadas con un copiado rápido), el núcleo de este proyecto radica en la arquitectura de infraestructura utilizada, dado que fue desplegado de forma segura en un servicio IaaS privado, basado en OpenStack. Contenerizado mediante microservicios y monitoreado con un stack moderno de observabilidad.

## Arquitectura:

El siguiente diagrama (desarrollado en código Mermaid) detalla el flujo de datos desde el acceso de los usuarios hasta la recolección distribuida de telemetría dentro de la red virtual del servidor:

Link acortado MERMAID PNG: https://goo.su/dffQYXh

## Stack Tecnológico & Justificación

### Aplicación (Python 3.10 + Streamlit): 
Se eligió Streamlit por su capacidad de construir interfaces reactivas de forma rápida, minimizando complejidad innecesaria en el frontend y permitiendo centrar el esfuerzo en la arquitectura de despliegue, contenerización y observabilidad de la plataforma.

Python 3.10 aporta compatibilidad estable con el ecosistema utilizado y simplifica la integración con herramientas de automatización y monitoreo dentro del entorno Linux.

### Contenerización (Docker & Docker Compose): 
La aplicación fue desacoplada mediante microservicios contenerizados para garantizar portabilidad, reproducibilidad y consistencia entre entornos.

Se implementó una estrategia de Dockerfile por capas (Layer Caching), separando la instalación de dependencias pesadas (pip install) de los cambios frecuentes del código fuente, optimizando significativamente los tiempos de build y reduciendo el consumo innecesario de recursos durante despliegues iterativos.

Docker Compose actúa como orquestador local de infraestructura, permitiendo administrar observabilidad, networking y persistencia desde una única definición declarativa.


## IaaS (OpenStack + Ubuntu Server): 

Desplegué una instancia de Linux en un proyecto interno, dentro de una nube privada.

TS: Una vez en marcha el docker compose y la construcción del dockerfile (docker compose up -d --build) se observó que la instalación de las dependencias en la construcción de la app_plantillas llegó a descargar 5.7 MB de los 7.1 MB que pesa la librería "pillow" a una velocidad de (105 MB/s). Antes de completarse la instalación se cortó. Para mitigar fallas de fragmentación de paquetes (errores MTU) se realizó la siguiente configuración:

```yaml
services:
  app-plantillas:
    build:
      context: .
      network: host # <--- Esta directiva le indica a Docker no usar su red virtual interna, sino utilizar la red del host para esta descarga.
    container_name: app_plantillas
    ports:
      - "8501:8501"
    volumes:
      - ./plantillas:/app/plantillas
    restart: unless-stopped
```

Luego se relanzó el comando y los microservicios levantaron sin errores.

## Persistencia (Bind Mounts): 

Almacenamiento desacoplado mediante archivos planos (plantillas.json): 

```yaml
volumes:
  - ./plantillas:/app/plantillas
```

El uso de volúmenes montados permite una sincronización en tiempo real. Logrando algo fundamental: que la web se vaya actualizando constantemente sin necesidad de reiniciar los containers ni interrumpir el servicio.

## Modelo de Observabilidad y Telemetría:

Implementé un modelo pasivo, sin agentes intrusivos ni modificaciones en el código para medir el rendimiento.

### Las herramientas utilizadas:

1)_ Google cAdvisor: Se ejecuta como un demonio contenerizado que lee los contadores de rendimiento nativos del Kernel de Linux. Exponiendo el consumo bruto de CPU, RAM y red de cada microservicio.

2)_ Prometheus: Configurado como una base de datos de series temporales, realiza un proceso de scraping activo cada 5 segundos sobre cAdvisor, estampando el tiempo y consolidando el historial métrico.

3)_ Grafana: Centraliza la visualización analítica. Implementé un dashboard optimizado de la comunidad (ID 14282) específico para cAdvisor, lo que permite auditar en tiempo real picos de consumo, detectar fugas de memoria y garantizar la estabilidad de la infraestructura.

## Nota:

La app Plantillas tiene 2 formas de despliegue.

1)_ La nativa en la cual corre actualmente, es desde la plataforma: https://streamlit.io/

Basicamente con tu cuenta, clonando tu repositorio podés en pocos clicks levantar la app y dar acceso restringido por usuario.

Las plantillas/instructivos los actualizás agregando líneas al archivo: 

```yaml 
plantilla.json.
```
## Para replicar este entorno de forma idéntica en cualquier servidor Ubuntu:

### Podes realizar lo siguiente: 

1. Clonar el repositorio usando SSH Deploy Keys

```bash
git clone git@github.com:tu-usuario/tu-repositorio.git
cd tu-repositorio
```
2. Desplegar toda la infraestructura en segundo plano

```bash
docker compose up -d --build
```

3. Verificar la salud de los servicios

```bash
docker compose ps
```

Asegúrese de abrir los puertos 8501 (App) y 3000 (Grafana) en los Security Groups de su proveedor de nube, manteniendo los puertos de Prometheus (9090) y cAdvisor (8080) cerrados al exterior por seguridad perimetral.

# Psdata:

Si bien el almacenamiento en archivo plano actual cumple eficientemente con los requisitos del MVP para el volumen de usuarios actual, el mapa de ruta arquitectónico contempla:

- Migrar a MongoDB, mudar la persistencia a un contenedor dedicado para soportar alta concurrencia y habilitar un panel de edición de plantillas desde la propia UI web.

- Gestión de secretos: Implementar variables de entorno y docker-secrets para desacoplar las credenciales de la base de datos del código fuente.

- A nivel monitoreo: Añadir Grafana Loki y Promtail al Docker Compose para capturar y auditar las interacciones de los usuarios en tiempo real.
