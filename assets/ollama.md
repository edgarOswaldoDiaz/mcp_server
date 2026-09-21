# 2.5.1 Ollama como Motor de Ejecución Local de LLMs

## ¿Qué es Ollama?

Ollama es una herramienta gratuita y de código abierto que permite descargar y ejecutar modelos de lenguaje grande directamente en la computadora del usuario, mediante un servidor API local que corre por defecto en `http://localhost:11434`. 
Surge como respuesta a la necesidad de no depender de un proveedor en la nube ni pagar tarifas por token cada vez que se envía un prompt. Su rendimiento, sin embargo, está limitado por el hardware disponible.

En esencia, es un ejecutor de modelos de lenguaje grande diseñado para hacer accesible la IA local en hardware de consumo común. Ollama se encarga de las partes más complicadas de correr un LLM: descarga los pesos del modelo, administra su almacenamiento, detecta la GPU disponible y ofrece una interfaz sencilla para interactuar con el modelo. Su propuesta de valor puede resumirse en que no requiere una clave de API, no implica ninguna suscripción y los datos nunca salen del dispositivo del usuario.

Está pensado principalmente para desarrolladores independientes, equipos pequeños, personas investigadoras y usuarios que priorizan la privacidad y quieren decidir a dónde van sus prompts y cuánto gastan en IA.

## Cómo Funciona Ollama

Ollama corre como un servidor local en la máquina del usuario: carga los pesos del modelo en memoria y expone una API REST en `localhost`, a la cual pueden conectarse tanto la línea de comandos como cualquier aplicación externa.

Los modelos se distribuyen en un formato cuantizado basado en GGUF y se descargan desde la biblioteca de modelos de Ollama con un solo comando. Una vez descargado, todo el ciclo de inferencia ocurre localmente: el prompt entra, el modelo lo procesa en el propio dispositivo y la respuesta se genera sin necesidad de ningún viaje de ida y vuelta hacia la nube.

La clave detrás de este funcionamiento es la **cuantización**: al comprimir los pesos del modelo a formatos numéricos más pequeños, permite que modelos de lenguaje grandes puedan correr en GPUs de consumo estándar, e incluso en máquinas que solo cuentan con CPU, sin necesitar la infraestructura de un centro de datos.

### Componentes Principales de la Arquitectura

* **Servidor API local:** escucha en `http://localhost:11434` por defecto, de modo que cualquier herramienta externa puede conectarse a él.
* **Capa de almacenamiento de modelos:** los modelos quedan en caché en disco después de la primera descarga, evitando tener que descargarlos nuevamente.
* **Abstracción de hardware:** detección automática de GPU (NVIDIA CUDA, Apple Metal o AMD ROCm), con respaldo en CPU cuando no hay GPU disponible.

## Características Principales

* **Biblioteca de modelos de Ollama:** una colección curada y lista para descargar de los LLM de código abierto más populares, explorable por nombre, tamaño y etiqueta.
* **Soporte multiplataforma:** instaladores nativos para macOS, Linux y Windows.
* **API compatible con OpenAI:** un endpoint que puede usarse como reemplazo directo, facilitando la migración de código existente desde APIs en la nube.
* **Personalización mediante Modelfile:** permite definir prompts de sistema, parámetros y modelos base a través de una configuración simple, de forma similar a un Dockerfile.
* **Servicio simultáneo de modelos:** a partir de la versión 0.5, es posible correr varios modelos al mismo tiempo, algo útil en configuraciones multiagente.
* **CLI ligera:** una interfaz de línea de comandos intuitiva para descargar, ejecutar y administrar modelos.

## Ollama vs. IA en la Nube

| Factor | Ollama (Local) | ChatGPT / Claude (Nube) |
|---|---|---|
| Privacidad | Control total de los datos | Datos procesados en servidores del proveedor |
| Costo | Gratis, una vez cubierto el hardware | Suscripción o pago por token |
| Latencia | Depende de la GPU local | Baja, centros de datos optimizados |
| Internet necesario | Solo para descargar el modelo | Siempre |
| Elección de modelo | Biblioteca de código abierto | Limitado al proveedor |
| Esfuerzo de configuración | Moderado | Ninguno |


En resumen, Ollama, resulta más conveniente en privacidad y costo para escenarios de IA local, mientras que la nube ofrece mejor rendimiento puro y cero fricción de configuración. No sustituye a la nube en todos los casos de uso, pero sí es un gran complemento para escenarios sensibles a la privacidad o sin conexión a internet.

## Requisitos del Sistema e Instalación

### Requisitos del Sistema

| Sistema operativo | Requisitos |
|---|---|
| macOS | 13 Ventura o posterior; se recomienda Apple Silicon (M1/M2/M3), aunque también es compatible con Intel |
| Windows | Windows 10/11 (64 bits); GPU NVIDIA con CUDA 11.3+ o GPU AMD con ROCm son opcionales, pero recomendables |
| Linux | Ubuntu 20.04 o superior (o equivalente), con el mismo soporte de GPU que Windows |

En cuanto a memoria, se recomiendan al menos 8 GB de RAM para modelos de 7B (idealmente 16 GB), y 32 GB o más para modelos de 13B en adelante. El espacio en disco necesario varía según el modelo: desde aproximadamente 2 GB en versiones cuantizadas de 3B, hasta 40 GB o más en modelos de 70B. Es posible ejecutar Ollama solo con CPU, aunque el rendimiento es considerablemente más lento, por lo que conviene reservar esa configuración para modelos pequeños (de 1B a 3B).

### Instalación Paso a Paso

1. **macOS / Windows:** descargar el instalador desde `ollama.com`, ejecutarlo; Ollama se iniciará como un servicio en segundo plano.
2. **Linux:** ejecutar el script oficial de instalación con:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
3. **Verificar la instalación:**
   ```bash
   ollama --version
   ```
4. **Descargar el primer modelo:**
   ```bash
   ollama pull llama3
   ```
5. **Comenzar a chatear:**
   ```bash
   ollama run llama3
   ```

## Biblioteca de Modelos: Cómo Elegir el Modelo Correcto

Cada modelo está a un solo `ollama pull` de distancia. Entre las opciones más populares se encuentran Llama 3, Mistral, Gemma 2, Phi-3 y Qwen 2.5. Para tareas más específicas existen modelos de programación como CodeLlama y DeepSeek-Coder, modelos de visión y multimodales como LLaVA y Moondream, y modelos de embeddings como Nomic-Embed-Text, útiles en pipelines de RAG.

Como regla práctica para calcular el tamaño necesario: la cantidad de parámetros del modelo multiplicada por aproximadamente 0.6 GB da una estimación de la VRAM mínima requerida. Los niveles de cuantización (Q4, Q5, Q8) permiten sacrificar precisión a cambio de un menor uso de recursos, siendo Q4 el más ligero y Q8 el más fiel a los pesos originales del modelo. El catálogo completo puede consultarse en `ollama.com/library`.

## Comandos Esenciales de la CLI

| Comando | Qué hace |
|---|---|
| `ollama pull <model>` | Descarga un modelo de la biblioteca |
| `ollama run <model>` | Inicia una sesión de chat interactiva |
| `ollama list` | Muestra todos los modelos instalados localmente |
| `ollama rm <model>` | Elimina un modelo del disco |
| `ollama show <model>` | Muestra los metadatos y parámetros del modelo |
| `ollama serve` | Inicia manualmente el servidor de la API de Ollama |
| `ollama create` | Crea un modelo personalizado a partir de un Modelfile |

También es posible redirigir texto directamente a un modelo, por ejemplo:

```bash
echo "Explain REST APIs" | ollama run mistral
```

Y para ver estadísticas de rendimiento como la velocidad de generación de tokens, puede agregarse la bandera `--verbose`:

```bash
ollama run <model> --verbose
```

## Integraciones y Ecosistema

* **LangChain:** Ollama cuenta con soporte nativo a través del paquete `langchain-ollama`, que permite construir cadenas de LLM locales, agentes y pipelines de RAG sin depender de la nube (`from langchain_ollama import OllamaLLM`).
* **API de Python:** la librería `ollama` (`pip install ollama`) refleja la API REST y resulta ideal para scripts y automatización (`import ollama; response = ollama.chat(model='llama3', messages=[...])`).
* **LlamaIndex:** indexación y recuperación de documentos usando embeddings locales.
* **Open WebUI:** una interfaz de chat basada en navegador, similar a ChatGPT, que se conecta al servidor local de Ollama.
* **Continue** (plugin para VS Code / JetBrains): un asistente de programación con IA impulsado por un modelo local de Ollama.
* **AnythingLLM:** un espacio de trabajo de RAG sin código que utiliza Ollama como backend de inferencia.

## Privacidad y Seguridad de Datos

La garantía principal de privacidad de Ollama es que toda la inferencia ocurre en el propio equipo del usuario, por lo que los prompts y las respuestas nunca salen de la máquina local; no existe telemetría, no se requiere ninguna cuenta y no hay dependencia de un proveedor externo.

Esto convierte a Ollama en una opción adecuada para manejar información sensible —notas médicas, documentos legales, código fuente propietario, datos empresariales confidenciales— y facilita el cumplimiento de marcos regulatorios como GDPR o HIPAA, así como de políticas internas de gobernanza de datos. Vale la pena señalar que incluso los modelos de pesos abiertos, cuando se accede a ellos a través de una API en la nube, exponen los datos al proveedor correspondiente; la ejecución local elimina por completo ese riesgo.

## Casos de Uso

* **Asistente de programación con IA:** ejecutar modelos como CodeLlama o DeepSeek-Coder localmente dentro de VS Code, por ejemplo mediante el plugin Continue.
* **Pipelines de RAG:** combinar Ollama con una base de datos vectorial (como Chroma o Qdrant) para responder preguntas sobre documentos privados.
* **Asistente de IA sin conexión:** utilizar Ollama en escenarios sin acceso a internet o con conectividad poco confiable.
* **Agentes de IA locales:** construir agentes autónomos con frameworks como LangChain o AutoGen, usando un modelo local como base.
* **Educación y experimentación:** un entorno seguro para probar prompts y estudiar el comportamiento de los modelos sin generar costos inesperados.

## Limitaciones

* **Límite de hardware:** el rendimiento depende directamente de la VRAM de la GPU local; los modelos muy grandes (70B en adelante) requieren GPUs de gama alta o estaciones de trabajo especializadas.
* **Sin interfaz integrada:** Ollama funciona solo por CLI y API, por lo que se necesita una herramienta adicional (como Open WebUI) para contar con una interfaz de chat.
* **Brecha en la calidad del modelo:** incluso los mejores LLM de código abierto pueden quedar por debajo de modelos de punta como GPT-4o o Claude 3.5 Sonnet en tareas de razonamiento complejo.
* **Tamaño de descarga inicial:** los modelos son archivos considerablemente grandes (entre 2 y 40 GB), lo que puede hacer lenta la puesta en marcha con una conexión limitada.
* **Soporte para Windows en desarrollo:** algunas funcionalidades todavía van un paso detrás de las implementaciones disponibles para macOS y Linux.

## Llamada a Herramientas (Tool Calling) con Ollama

La llamada a herramientas es la capacidad de un LLM para interactuar con herramientas, servicios o APIs externas con el fin de realizar tareas, ampliando así su funcionalidad más allá de su conocimiento entrenado. Por ejemplo, un modelo puede invocar una herramienta de búsqueda web para obtener datos en tiempo real, ejecutar código en Python para hacer cálculos o análisis, o llamar a un endpoint de servicio externo. Esta capacidad permite que un asistente conversacional sea más dinámico y adaptable, ofreciendo respuestas más precisas y relevantes basadas en datos o en tareas especializadas fuera de su base de conocimiento inmediata.

Ollama, al ser una plataforma que ejecuta modelos de código abierto directamente en el dispositivo del usuario, no requiere una cuenta, ya que el modelo corre en la máquina local. Esto la hace adecuada para una arquitectura de llamada de herramientas, dado que el modelo puede acceder directamente a las capacidades del entorno local: datos, programas y software personalizado.

---

## Referencias

> Caetano, G. (2026, Agosto 9). *¿Qué Es Ollama? Guía Completa para Ejecutar Modelos de IA Localmente*. Bleap. https://www.bleap.finance/es-mx/blog/que-es-ollama

> Stryker, C. *Llamada a herramientas con Ollama*. IBM.com. https://www.ibm.com/mx-es/think/topics/tool-calling
