'Inicia Informe Mensual de Obra SIN ventana de consola.
'Doble clic en este archivo:
'  - Modo ADMINISTRADOR: si el servidor ya esta activo, el propio script abre el
'    navegador (inicio casi instantaneo); si no, lo arranca en segundo plano
'    (oculto). El servidor abre el navegador cuando este listo.
'  - Modo CLIENTE: el script espera a que el servidor del Administrador responda
'    (misma red o Tailscale) y abre el navegador apuntando a esa URL.
'Todo eso lo decide informe_web\servidor_silencioso.py leyendo config_red.py;
'aqui solo se localiza pythonw y se lanza ese script oculto.
'Para detener el servidor use detener_servidor.bat.
'Nota: si edito archivos del aplicativo, detenga el servidor antes de reabrirlo.

Option Explicit

Dim WshShell, FSO, carpeta, pythonw

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
carpeta = FSO.GetParentFolderName(WScript.ScriptFullName)

' Busca pythonw.exe: primero embebido (junto a este script), luego PATH, luego ruta legacy.
pythonw = ""

' 1) Python embebido: carpeta\python\pythonw.exe
Dim rutaEmbebido
rutaEmbebido = carpeta & "\python\pythonw.exe"
If FSO.FileExists(rutaEmbebido) Then
  pythonw = rutaEmbebido
End If

' 2) PATH del sistema
If pythonw = "" Then
  Dim sh, exec, salida
  Set sh = CreateObject("WScript.Shell")
  Set exec = sh.Exec("cmd /c where pythonw")
  salida = exec.StdOut.ReadAll()
  exec.Terminate
  If Trim(salida) <> "" Then
    pythonw = Trim(Split(salida, vbCrLf)(0))
  End If
End If

' 3) Ruta legacy (compatibilidad con instalaciones anteriores)
If pythonw = "" Then
  If FSO.FileExists("C:\Python314\pythonw.exe") Then
    pythonw = "C:\Python314\pythonw.exe"
  End If
End If

If pythonw = "" Then
  MsgBox "No se encontro pythonw.exe." & vbCrLf & vbCrLf & _
         "Verifique que la carpeta 'python' este junto a este script," & vbCrLf & _
         "o que Python este instalado en el PATH.", 48, "Informe Mensual de Obra"
  WScript.Quit
End If

' Lanza el script oculto; el decide el modo (administrador/cliente), arranca el
' servidor si corresponde y abre el navegador cuando el servidor responde.
Dim cmd
cmd = """" & pythonw & """ """ & carpeta & "\informe_web\servidor_silencioso.py"""
WshShell.Run cmd, 0, False