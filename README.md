# Inmobilike It - Plataforma Inmobiliaria

Inmobilike It es una plataforma inmobiliaria moderna construida con **Django**, que implementa una arquitectura robusta (Repository Pattern y Service Layer) e incluye mensajería en tiempo real usando **Django Channels** (WebSockets).

## Características principales

- **Gestión de Propiedades**: Publicación y búsqueda avanzada de propiedades.
- **Interacciones de Usuarios**: Los usuarios pueden añadir propiedades a sus favoritos, hacer consultas sobre propiedades y contactar directamente a los propietarios.
- **Mensajería en tiempo real**: Chat integrado entre interesados y agentes/propietarios usando WebSockets.
- **Arquitectura Robusta**: Separación clara de responsabilidades en la capa de datos (Repositories), capa de lógica de negocio (Services) y capa de presentación (Views/Templates).

---

## Estructura del Proyecto

El proyecto está organizado en distintas aplicaciones (apps) según su dominio de negocio:
- `apps/core`: Configuraciones comunes y utilidades generales.
- `apps/accounts`: Gestión de perfiles de usuario, agentes y autenticación.
- `apps/properties`: Modelos, servicios y vistas de propiedades (incluyendo la búsqueda avanzada y comparación).
- `apps/interactions`: Lógica para favoritos, notificaciones, consultas, conversaciones y WebSockets.

### Arquitectura del Sistema

El proyecto implementa una arquitectura robusta basada en **Repository Pattern**, **Service Layer** y uso de **WebSockets** con Django Channels. El siguiente diagrama detalla cómo fluyen los datos en la aplicación:

```mermaid
flowchart TD
    %% Entidades Externas
    Client[Cliente / Navegador]
    DB[(PostgreSQL)]
    
    %% Capa de Enrutamiento
    subgraph RoutingLayer [Enrutamiento]
        URLRouter[urls.py HTTP]
        WSRouter[asgi.py / routing.py WS]
    end
    
    %% Capa de Presentación (Manejadores)
    subgraph PresentationLayer [Capa de Presentación]
        View[views.py Vistas]
        Consumer[consumers.py WebSockets]
        Template[Templates HTML]
    end
    
    %% Capa de Negocio (Lógica)
    subgraph ServiceLayer [Capa de Servicios]
        Service[services.py Ej: ContactService, SearchService]
    end
    
    %% Capa de Acceso a Datos
    subgraph RepositoryLayer [Capa de Repositorios]
        Interface[Interfaces / ABC]
        Repository[repositories.py Implementación ORM]
    end
    
    %% Capa de Modelos ORM
    subgraph ORMLayer [Modelos]
        Model[models.py Django ORM]
    end
    
    %% Flujos HTTP
    Client -- 1. Petición HTTP --> URLRouter
    URLRouter -- 2. Delega a Vista --> View
    View -- 3. Invoca lógica negocio --> Service
    
    %% Flujos WebSockets
    Client -- 1. Conexión WebSocket --> WSRouter
    WSRouter -- 2. Delega a Consumidor --> Consumer
    Consumer -- 3. Lógica en tiempo real --> Model
    
    %% Flujos Internos de la Arquitectura
    Service -- 4. Inyección de Dependencias --> Interface
    Interface -. Implementa .- Repository
    Service -- 5. Solicita datos a --> Repository
    Repository -- 6. Construye queries con --> Model
    Model -- 7. Ejecuta SQL en --> DB
    
    %% Flujo de Retorno HTTP
    DB -- 8. Retorna registros --> Model
    Model -- 9. Retorna objetos --> Repository
    Repository -- 10. Retorna data limpia --> Service
    Service -- 11. Entrega resultados --> View
    View -- 12. Inyecta contexto en --> Template
    Template -- 13. Renderiza HTML a --> View
    View -- 14. Respuesta HTTP --> Client

    %% Estilos
    classDef client_db fill:#e6f3ff,stroke:#0066cc,stroke-width:2px;
    classDef layers fill:#f9f9f9,stroke:#999,stroke-width:1px,stroke-dasharray: 5 5;
    class Client,DB client_db;
```

---

## Instrucciones de Instalación (Local sin Docker)

### Prerrequisitos
- Python 3.10 o superior
- pip y virtualenv (recomendado)

### Pasos
1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repo>
   cd Inmobilike_It
   ```

2. **Crear y activar el entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   # venv\Scripts\activate   # En Windows
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Aplicar migraciones**:
   ```bash
   python manage.py migrate
   ```

5. **Iniciar servidor de desarrollo**:
   ```bash
   python manage.py runserver
   ```
   La plataforma estará disponible en `http://localhost:8000`.

---

## Ejecución con Docker

El proyecto incluye un entorno preconfigurado usando `docker-compose` que levanta la aplicación Django junto con una base de datos PostgreSQL y Redis (para Django Channels).

### Pasos
1. Asegúrate de tener instalado **Docker** y **Docker Compose**.
2. Construir la imagen de Docker e iniciar los contenedores:
   ```bash
   docker-compose up --build
   ```
   *(Añade la bandera `-d` al final si quieres que se ejecute en segundo plano)*.

3. Aplicar migraciones en el contenedor (si es la primera vez):
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. Crear un superusuario (opcional):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

---

## Ejemplos de Uso

### 1. Búsqueda Avanzada de Propiedades
Para buscar propiedades por diferentes filtros (ubicación, precio, habitaciones, tipo de operación):
```python
from apps.properties.services.search_service import AdvancedSearchService

search_service = AdvancedSearchService()
resultados = search_service.search({
    "location": "Medellin",
    "operation": "rent",
    "min_price": 1000000,
    "bedrooms": 2
})
```

### 2. Contacto Directo con Propietario (Servicio con Transacciones)
El servicio de contacto crea de forma atómica una consulta (Inquiry) y, si es posible, inicia automáticamente una conversación en el chat.
```python
from apps.interactions.services.contact_service import ContactService

contact_service = ContactService()
inquiry, conversation = contact_service.initiate_contact(
    property_obj=propiedad,
    user=request.user,
    message="Me interesa agendar una visita a este apartamento."
)
```

### 3. Comparación de Propiedades
Para comparar múltiples propiedades y extraer métricas clave (ej. precio por m²):
```python
from apps.properties.services.comparison_service import ComparisonService

comparison_service = ComparisonService()
datos_comparativos = comparison_service.compare_properties([1, 4, 7])
```
