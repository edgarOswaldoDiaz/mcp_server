import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

def format_json_response(json_data, title="Respuesta del Servidor"):
    """
    Toma un diccionario o string JSON y lo imprime en la terminal 
    de forma bonita usando una tabla y un panel de Rich.
    """
    try:
        # Si es un string, lo convierte a diccionario
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        # Crear una tabla
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Clave", style="cyan", no_wrap=True)
        table.add_column("Valor", style="green")

        # Llenar la tabla con los datos del JSON
        for key, value in data.items():
            # Convertir valores complejos (listas, diccionarios) a string para la tabla
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value, indent=2)
            else:
                value_str = str(value)
            table.add_row(str(key), value_str)

        # Imprimir la tabla dentro de un panel
        panel = Panel(table, expand=False, border_style="blue")
        console.print(panel)

    except json.JSONDecodeError:
        console.print(f"[bold red]Error:[/bold red] El texto proporcionado no es un JSON válido.")
        console.print(Text(str(json_data), style="dim"))
    except Exception as e:
        console.print(f"[bold red]Error inesperado:[/bold red] {e}")

# (Opcional) Código de prueba para ver cómo funciona:
if __name__ == "__main__":
    ejemplo_json = {
        "status": "success",
        "mensaje": "Políticas de S3 aplicadas correctamente.",
        "archivos_afectados": ["politica-confidencial.json", "politicalector.json"],
        "seguridad": {"DPoP": "Activo", "OAuth": "Validado"}
    }
    
    format_json_response(ejemplo_json, title="Resultado de Operación S3")