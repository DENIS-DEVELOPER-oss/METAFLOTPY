
# MetaFlotPy

MetaFlotPy es una aplicación web profesional desarrollada en Flask para cálculos metalúrgicos, inspirada en el software Promitech. Está diseñada para ingenieros metalúrgicos y profesionales de la minería que necesitan realizar análisis y cálculos especializados.

## 🚀 Características Principales

### Módulos Disponibles

- **Análisis Granulométrico (Tamizado)**: Curvas granulométricas acumulativas y análisis de distribución de tamaños
- **Balance de Masa**: Cálculos de flujos másicos, carga circulante y eficiencias de clasificación  
- **Balance Metalúrgico**: Recuperaciones metalúrgicas, leyes y distribución de elementos valiosos
- **Dimensionamiento**: Estimación de dimensiones de molinos, celdas de flotación y espesadores
- **Valorización**: Cálculo del valor económico de concentrados (en desarrollo)
- **Utilitarios**: Herramientas de conversión y cálculos auxiliares

### Tecnologías Utilizadas

- **Python 3.11+**
- **Flask** con Blueprints para arquitectura modular
- **Plotly** para gráficos interactivos
- **Pandas y NumPy** para cálculos científicos
- **Bootstrap 5** para interfaz responsiva
- **Flask-Login** para autenticación
- **Flask-WTF** para formularios seguros

## 📁 Estructura del Proyecto

```
MetaFlotPy/
├── app/
│   ├── __init__.py
│   ├── auth/                    # Autenticación y usuarios
│   ├── principal/               # Dashboard y páginas principales
│   ├── tamizado/                # Análisis granulométrico
│   ├── balance_masa/           # Balance de masa
│   ├── balance_metalurgico/    # Recuperación y leyes
│   ├── dimensionamiento/       # Cálculo de equipos
│   ├── valorizacion/           # Valorización de concentrados
│   ├── utilitarios/            # Herramientas auxiliares
│   └── templates/              # Templates HTML
├── main.py
├── pyproject.toml
└── README.md
```

## 🔧 Instalación y Configuración

### Requisitos Previos

- Python 3.11 o superior
- Poetry (recomendado) o pip

### Instalación

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias** (Poetry se encarga automáticamente en Replit):
   ```bash
   poetry install
   ```

3. **Ejecutar la aplicación**:
   ```bash
   python main.py
   ```

4. **Acceder a la aplicación**:
   - Abrir navegador en `http://localhost:5000`
   - Usuario demo: `admin`
   - Contraseña demo: `admin123`

## 🖥️ Uso de la Aplicación

### Dashboard Principal

Después de iniciar sesión, accederás al dashboard principal donde podrás:
- Ver resumen de módulos disponibles
- Acceder rápidamente a las herramientas más utilizadas
- Navegar entre los diferentes módulos usando la barra lateral

### Módulo de Tamizado

1. Ingresar el peso total de la muestra
2. Completar los pesos retenidos en cada malla
3. Hacer clic en "Calcular Análisis Granulométrico"
4. Visualizar la curva granulométrica y tabla de resultados

### Módulo de Balance de Masa

1. Ingresar la alimentación fresca en t/h
2. Especificar la razón de carga circulante
3. Definir la eficiencia del clasificador
4. Obtener el diagrama de flujos y balance completo

### Módulo de Balance Metalúrgico

1. Ingresar las leyes de alimentación, concentrado y relave
2. Especificar la razón de concentración
3. Calcular recuperaciones metalúrgicas y en peso
4. Visualizar el análisis gráfico de resultados

## 🔐 Autenticación

La aplicación incluye un sistema básico de autenticación:
- Registro de nuevos usuarios
- Inicio y cierre de sesión
- Protección de rutas sensibles
- Usuario demo para pruebas

## 📊 Visualizaciones

Todos los módulos incluyen visualizaciones interactivas usando Plotly:
- Gráficos de líneas para curvas granulométricas
- Gráficos de barras para balances de masa
- Gráficos combinados para análisis metalúrgicos
- Interactividad completa (zoom, pan, hover)

## 🎯 Casos de Uso

MetaFlotPy es ideal para:
- **Ingenieros de Procesos**: Análisis de circuitos de conminución y concentración
- **Metalurgistas**: Evaluación de recuperaciones y eficiencias
- **Estudiantes**: Aprendizaje de conceptos metalúrgicos
- **Consultores**: Evaluaciones rápidas y reportes técnicos

## 🚧 Desarrollo Futuro

### Módulos en Desarrollo
- Completar módulo de valorización económica
- Ampliar herramientas de dimensionamiento
- Agregar más conversores en utilitarios
- Implementar base de datos persistente
- Exportación de reportes en PDF

### Mejoras Planificadas
- Integración con bases de datos reales
- API REST para integración externa
- Más tipos de gráficos y visualizaciones
- Sistema de usuarios y permisos avanzado
- Modo offline para cálculos móviles

## 📄 Licencia

Este proyecto es desarrollado con fines educativos y profesionales. 

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork del proyecto
2. Crear rama para nueva funcionalidad
3. Commit de cambios
4. Push a la rama
5. Crear Pull Request

## 📞 Soporte

Para preguntas, sugerencias o reportes de errores, por favor crear un issue en el repositorio del proyecto.

---

**MetaFlotPy** - Software profesional para cálculos metalúrgicos 🔧⚒️
