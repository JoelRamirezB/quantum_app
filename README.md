# Quantum — Automatización de Facturación Electrónica

Aplicativo web desarrollado para automatizar el proceso de registro de facturas electrónicas en la plataforma contable **SIIGO NUBE** para la empresa Atelcro S.A.S.

El sistema extrae automáticamente la información de facturas electrónicas en formato PDF, permite la validación humana de los datos extraídos y genera un archivo Excel (.xlsx) compatible con la plantilla de importación masiva de SIIGO NUBE.

---

## Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.11 |
| Framework web | Flask |
| Base de datos | MySQL 8.0 |
| ORM | SQLAlchemy |
| Extracción de PDF | pdfplumber |
| Generación de Excel | openpyxl |
| Cifrado | bcrypt |
| Front-end | HTML5, CSS3, JavaScript, Bootstrap 5 |

---

## Estructura del proyecto

```
quantum/
├── app/
│   ├── models/          # Modelos ORM (Usuario, Factura, ItemFactura, etc.)
│   ├── routes/          # Controladores organizados por blueprint
│   ├── services/        # Servicios (ExtractorOCR, SiigoService)
│   ├── templates/       # Plantillas Jinja2
│   └── static/          # Archivos CSS, JS e imágenes
├── migrations/
│   └── schema.sql       # Script de creación de base de datos y triggers
├── requirements.txt     # Dependencias de Python
├── config.py            # Configuración de la aplicación
├── .env.example         # Plantilla de variables de entorno
└── run.py               # Punto de entrada de la aplicación
```

---

## Requisitos previos

- Python 3.11 o superior
- MySQL 8.0 o superior
- pip

---

## Instalación y ejecución local

### 1. Clonar el repositorio

```bash
git clone https://github.com/JoelRamirezB/quantum_app.git
cd quantum
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear la base de datos

Acceder a MySQL y ejecutar el script de creación:

```bash
mysql -u <usuario> -p < migrations/schema.sql
```

Este script crea la base de datos `quantum_db`, las tablas y los cuatro triggers de integridad.

### 5. Configurar variables de entorno

Copiar el archivo de ejemplo y editar con los valores reales:

```bash
cp .env.example .env
```

Editar el archivo `.env`:

```
FLASK_ENV=development
SECRET_KEY=<cadena_aleatoria_segura>
DATABASE_URL=mysql+pymysql://<usuario>:<contraseña>@localhost/quantum_db
```

> ⚠️ **Nunca subas el archivo `.env` al repositorio.** Está incluido en `.gitignore`.

### 6. Crear el usuario administrador inicial

El primer usuario administrador se inserta directamente en la base de datos. Primero genera el hash de la contraseña:

```python
import bcrypt
hash = bcrypt.hashpw(b'<contraseña>', bcrypt.gensalt())
print(hash.decode('utf-8'))
```

Luego ejecuta en MySQL:

```sql
INSERT INTO usuario (nombre_completo, email, contraseña, rol, activo)
VALUES ('<Nombre>', '<correo@empresa.com>', '<hash_generado>', 'ADMINISTRADOR', 1);
```

### 7. Ejecutar la aplicación

```bash
python run.py
```

La aplicación estará disponible en `http://127.0.0.1:5000`

---

## Despliegue en PythonAnywhere

1. Subir el proyecto a PythonAnywhere vía Git o ZIP.
2. Crear un entorno virtual e instalar dependencias con `pip install -r requirements.txt`.
3. Crear la base de datos MySQL desde la pestaña **Databases** del panel.
4. Ejecutar el script `migrations/schema.sql` desde la consola MySQL de PythonAnywhere.
5. Configurar las variables de entorno en el archivo `.env`.
6. Configurar la aplicación web en la pestaña **Web** apuntando al archivo WSGI.
7. Presionar **Reload** para iniciar la aplicación.

---

## Módulos del sistema

| Módulo | Descripción |
|---|---|
| Autenticación | Inicio de sesión con roles (administrador / operativo) |
| Carga | Subida de archivos PDF y extracción automática de datos |
| Validación | Revisión y corrección de los datos extraídos |
| Exportación | Generación del archivo .xlsx para importación masiva en SIIGO |
| Historial | Consulta de facturas procesadas con filtros |
| Configuración | Datos de empresa y token de API SIIGO (solo administrador) |
| Gestión de usuarios | Crear, editar y deshabilitar usuarios (solo administrador) |

---

## Variables de entorno requeridas

| Variable | Descripción |
|---|---|
| `FLASK_ENV` | Entorno de ejecución |
| `SECRET_KEY` | Clave secreta para sesiones Flask |
| `DATABASE_URL` | Cadena de conexión a MySQL |

---

## Autor

**Joel Sebastián Ramírez Bermúdez**  
Universidad Antonio Nariño — Tecnologia en construcción de software 
Trabajo de grado — 2026  
Director: Juan Carlos Martínez