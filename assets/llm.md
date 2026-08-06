# 2.4.1 LLMs

## ¿Qué son los LLM?

Los modelos de lenguaje grande (LLM) son una categoría de modelos de aprendizaje profundo entrenados con grandes cantidades de datos, esto los hace capaces de comprender y generar lenguaje natural, así como otros tipos de contenido para realizar diversas tareas.

> **Recordatorio:** MCP es un protocolo abierto para conectar aplicaciones basadas en LLM con herramientas y fuentes de contexto externas.

## Fortalezas y Debilidades de los LLMs

| Excelentes en... | Débiles a menos que se diseñe para ello |
|---|---|
| Resumir y transformar tono/estructura | Hechos recientes sin búsqueda o recuperación |
| Redactar, generar ideas, comparar opciones | Salida estructurada confiable sin un esquema |
| Extraer patrones de lenguaje desordenado | Acciones irreversibles sin validación |
| Planear siguientes pasos cuando las herramientas son visibles | Contextos largos si solo se "rellenan" sin curaduría |
| Clasificación y etiquetado | Fronteras de seguridad (la superficie de ataque está alrededor del modelo) |

## Tool Use & Function Calling

El modelo puede elegir herramientas y redactar sus argumentos, pero la aplicación debe validar, restringir y registrar las acciones consecuentes.

* Documentar las herramientas como buenas APIs: nombre claro, descripción, tipos de parámetros.
* Preferir herramientas de alto nivel sobre primitivas de bajo nivel.
* Validar las llamadas consecuentes antes de la ejecución.
* Preguntar antes de acciones riesgosas o irreversibles.

## Técnicas de Prompting

* **Few-shot (ejemplos):** mostrar de 1 a 3 ejemplos del resultado deseado; es la forma más rápida de transmitir tono, formato y reglas de estilo implícitas.
* **Descomposición/razonamiento deliberado:** para tareas difíciles, pedir al modelo que divida el problema en pasos, verifique supuestos o produzca un razonamiento breve antes de la respuesta final; se prefieren salidas intermedias estructuradas sobre razonamiento libre.
* **Salida estructurada/esquema:** cuando la salida debe ser procesada por código, se debe entregar un esquema JSON o una especificación de formato explícita, eliminando la necesidad de expresiones regulares o post-procesamiento.
* **Bucles de razonamiento asistidos por herramientas:** para tareas que requieren evidencia o acciones, permitir que el modelo busque, calcule o invoque herramientas, y verificar los resultados antes de responder.
* **Ejemplos negativos:** mostrar qué NO se debe producir; útil para corregir estilo y evitar fallas comunes.
* **Instrucciones de sistema:** instrucciones de mayor prioridad provistas por la aplicación, que suelen persistir durante toda la sesión o flujo de trabajo; se usan para definir rol, tono y restricciones de seguridad.

## Estructura de un Buen Prompt

Un prompt sólido suele componerse de cinco capas, aunque no todas son necesarias en todos los casos; se recomienda usar solo la estructura mínima que la tarea requiera:

1. **Rol/Persona:** define la experticia y perspectiva desde la que responde el modelo.
2. **Tarea + Criterio de éxito:** qué debe hacerse y cómo se ve un resultado "terminado".
3. **Contexto:** información de fondo, restricciones y entorno de la tarea.
4. **Restricciones:** límites, casos borde y qué hacer ante la incertidumbre.
5. **Formato de salida:** estructura, extensión, esquema o ejemplos esperados.

**Ejemplo:**

```
1 Rol: Eres un ingeniero de seguridad.
2 Tarea: Redacta una revisión de diseño para este flujo de trabajo con IA.
3 Contexto: el sistema envía transcripciones de reuniones a un LLM 
  para generar resúmenes automáticos.
4 Restricciones:
   - identifica riesgos de privacidad e inyección de prompts
   - solicita aclaración si el flujo de datos no es claro
   - cierra con 3 recomendaciones concretas y accionables
5 Formato de salida: markdown con encabezados + tabla de riesgos
```

## Antipatrones: Cómo Fallan los Proyectos con LLMs

| Antipatrón | Causa raíz |
|---|---|
| Prompt vago, confianza ciega en la salida | Tarea mal especificada |
| Meter toda una wiki en el contexto | Falta de curaduría sobre qué información importa ahora |
| Usar un agente para una tarea determinística | El sistema tiene más autonomía de la necesaria |
| Otorgar credenciales amplias "para ahorrar tiempo" | Permisos demasiado abiertos |
| Medir "sensaciones" en vez de precisión | No existe un ciclo de retroalimentación |
| Omitir la revisión de transcripciones | Falta de análisis de errores |

La solución suele ser sencilla: reducir el alcance, mejorar el contexto, ajustar los permisos y definir evaluaciones explícitas.

---

## Referencias

> Maes, J.F. *LLM Usage Cheat Sheet v1.0*. SANS Institute — SANS.org/offensive-operations

> Stryker, C. (2025, November 26). *Modelos de lenguaje de gran tamaño*. IBM.com. https://www.ibm.com/mx-es/think/topics/large-language-models
