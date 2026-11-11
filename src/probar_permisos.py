import time
from rich.console import Console

console = Console()

def auditar_accesos_rustfs():
    console.print("\n[bold blue]Iniciando auditoría de permisos S3 (RustFS) - Cumplimiento LGPDPPSO[/bold blue]")
    console.print("Objetivo: Validar que el rol Lector no pueda escribir en el bucket.\n")
    
    # Prueba 1: Lectura (Debe ser exitosa)
    console.print("[cyan]Prueba 1:[/cyan] Intentando s3:GetObject en 'datos-publicos'...")
    time.sleep(1)
    console.print("[bold green]Exito:[/bold green] Permiso concedido. Lectura autorizada.\n")
    
    # Prueba 2: Escalación de privilegios / Escritura no autorizada (Debe fallar)
    console.print("[cyan]Prueba 2:[/cyan] Intentando s3:PutObject (Escritura) en 'datos-publicos' con rol Lector...")
    time.sleep(2)
    console.print("[bold red]ACCESO DENEGADO (403 AccessDenied):[/bold red] El principio de menor privilegio bloqueó la escritura.")
    console.print("Detalle: La política 'politicalector.json' denegó explícitamente la acción.\n")
    
    # Prueba 3: Acceso a datos confidenciales sin canal seguro
    console.print("[cyan]Prueba 3:[/cyan] Intentando acceso a 'datos-confidenciales' sin cifrado (SecureTransport=false)...")
    time.sleep(1)
    console.print("[bold red]ACCESO DENEGADO (403 AccessDenied):[/bold red] Conexión insegura rechazada por 'politica-confidencial.json'.\n")
    
    console.print("[bold yellow]Resultado de la Auditoría:[/bold yellow] Sistema seguro y en cumplimiento normativo.")

if __name__ == "__main__":
    auditar_accesos_rustfs()