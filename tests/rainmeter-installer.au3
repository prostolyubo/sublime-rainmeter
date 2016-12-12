#RequireAdmin
#Region ;**** Directives created by AutoIt3Wrapper_GUI ****
#AutoIt3Wrapper_Compression=4
#AutoIt3Wrapper_UseX64=n
#EndRegion ;**** Directives created by AutoIt3Wrapper_GUI ****
; required to finish the installation

; Open Rainmeter Installer
Run("C:\rainmeter-setup.exe")

; Pause Execution until Installer becomes active Window
$lang = WinWaitActive('[REGEXPTITLE:.*Rainmeter.*]')

; Select Language
ControlClick($lang, "", "[CLASSNN:Button1]")

; new window pops up for installation type
Sleep(100)
$type = WinWaitActive('[REGEXPTITLE:.*Rainmeter.*]')

; click Weiter
ControlClick($type, "", "[CLASSNN:Button2]")

; click Installieren
ControlClick($type, "", "[CLASSNN:Button2]")
ConsoleWrite($type & " second window" & @LF)
Sleep(1000)

; just try over and over again to look if the finish button is enabled
While True
	$isControlEnabled = ControlCommand($type, "", "[CLASSNN:Button2]", "IsEnabled", "")
	ConsoleWrite("Is Enabled: " & $isControlEnabled & @LF)
	if $isControlEnabled Then
		ExitLoop
	EndIf

	Sleep(100)
WEnd

; we found the finish button and just need to click it
ControlClick($type, "", "[CLASSNN:Button2]")
ConsoleWrite($type & " exit window" & @LF)

Exit
