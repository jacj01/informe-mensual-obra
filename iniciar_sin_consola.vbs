'Inicia Informe Mensual de Obra SIN ventana de consola.
'Doble clic en este archivo:
'  - Modo ADMINISTRADOR: reinicia el servidor en segundo plano garantizando
'    que siempre se ejecute la version mas reciente del aplicativo y abre
'    el navegador automaticamente.
'  - Modo CLIENTE: el script espera a que el servidor del Administrador responda
'    (misma red o Tailscale) y abre el navegador apuntando a esa URL.
'Todo eso lo decide informe_web\servidor_silencioso.py leyendo config_red.py;
'aqui solo se localiza pythonw y se lanza ese script oculto.
'Para detener el servidor use detener_servidor.bat.

Option Explicit

Dim WshShell, FSO, carpeta, pythonw

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
carpeta = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = carpeta & "\informe_web"

' Busca pythonw.exe: primero embebido (junto a este script), luego PATH, luego ruta legacy.
pythonw = ""

' 1) Python embebido: carpeta\python\pythonw.exe
Dim rutaEmbebido
rutaEmbebido = carpeta & "\python\pythonw.exe"
If FSO.FileExists(rutaEmbebido) Then
  pythonw = rutaEmbebido
End If

' 2) Rutas estándar de Python instaladas en la raíz del sistema
If pythonw = "" Then
  Dim rutas, r
  rutas = Array("C:\Python315\pythonw.exe", "C:\Python314\pythonw.exe", "C:\Python313\pythonw.exe", "C:\Python312\pythonw.exe", "C:\Python311\pythonw.exe", "C:\Python310\pythonw.exe")
  For Each r In rutas
    If FSO.FileExists(r) Then
      pythonw = r
      Exit For
    End If
  Next
End If

' 3) PATH del sistema (omitiendo alias vacios de WindowsApps)
If pythonw = "" Then
  Dim sh, exec, salida, lineas, i, l
  Set sh = CreateObject("WScript.Shell")
  Set exec = sh.Exec("cmd /c where pythonw")
  salida = exec.StdOut.ReadAll()
  exec.Terminate
  If Trim(salida) <> "" Then
    lineas = Split(salida, vbCrLf)
    For i = 0 To UBound(lineas)
      l = Trim(lineas(i))
      If l <> "" And InStr(l, "WindowsApps") = 0 And FSO.FileExists(l) Then
        pythonw = l
        Exit For
      End If
    Next
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
cmd = Chr(34) & pythonw & Chr(34) & " " & Chr(34) & carpeta & "\informe_web\servidor_silencioso.py" & Chr(34) & " --reiniciar"
WshShell.Run cmd, 0, False