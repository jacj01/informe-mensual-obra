'Inicia el servidor de Informe Mensual de Obra SIN ventana de consola.
'Doble clic en este archivo:
'  - Si el servidor ya esta activo, abre el navegador directamente (inicio casi instantaneo).
'  - Si no, lo arranca en segundo plano (oculto); el propio servidor abre el
'    navegador en cuanto este listo (sin esperas fijas ni sondeos desde aqui).
'Para detenerlo use detener_servidor.bat.
'Nota: si edito archivos del aplicativo, detenga el servidor antes de reabrirlo.

Option Explicit

Dim WshShell, FSO, carpeta, pythonw, pid

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
carpeta = FSO.GetParentFolderName(WScript.ScriptFullName)

Function ServidorSano()
  Dim http
  On Error Resume Next
  Set http = CreateObject("MSXML2.XMLHTTP")
  http.Open "GET", "http://127.0.0.1:5000/robots.txt", False
  http.Send
  If Err.Number = 0 And http.status = 200 Then
    ServidorSano = True
  Else
    ServidorSano = False
  End If
  Err.Clear
  On Error GoTo 0
End Function

Function ProcesoVivo(pid)
  Dim wmi
  On Error Resume Next
  Set wmi = GetObject("winmgmts:\\.\root\cimv2:Win32_Process.Handle='" & pid & "'")
  If Err.Number = 0 Then
    ProcesoVivo = True
  Else
    ProcesoVivo = False
  End If
  Err.Clear
  On Error GoTo 0
End Function

Function LeerPid()
  Dim f, s
  If FSO.FileExists(carpeta & "\informe_web\servidor.pid") Then
    Set f = FSO.OpenTextFile(carpeta & "\informe_web\servidor.pid", 1)
    s = Trim(f.ReadLine)
    f.Close
    If IsNumeric(s) Then
      LeerPid = CLng(s)
    Else
      LeerPid = 0
    End If
  Else
    LeerPid = 0
  End If
End Function

' Atajo ruta rapida: si el servidor ya responde, abre el navegador y termina.
pid = LeerPid()
If pid > 0 Then
  If ProcesoVivo(pid) And ServidorSano() Then
    WshShell.Run "http://127.0.0.1:5000", 0, False
    WScript.Quit
  End If
End If

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

' Lanza el servidor; el abre el navegador por si mismo cuando este listo.
Dim cmd
cmd = """" & pythonw & """ """ & carpeta & "\informe_web\servidor_silencioso.py"""
WshShell.Run cmd, 0, False
