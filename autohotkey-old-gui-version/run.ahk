#SingleInstance force
#NoEnv

;Tray tip
Menu, tray, Tip, Window Fill

;Suspend mode (1=Do suspend global hotkey)
suspend_mode := 0
main_window_showing := 0

;Read default HK
IniRead, savedHK, hotkey.ini, hotkey, hotkey, ^+q
Hotkey, %savedHK%, ExecuteHotkey, On

;Menu options
Menu, tray, NoStandard
Menu, tray, Add, Configure Hotkey, ConfigureHandler
Menu, tray, Add, Suspend Global Hotkey, SuspendHandler
Menu, tray, Add, Help, HelpHandler
Menu, tray, Add, Exit, ExitHandler
Menu, tray, Default, Configure Hotkey
;Do not execute past this point now
return


;{---}
GuiClose:
main_window_showing = 0
Gui, Cancel
return

;TODO: BUG: Gui does not flash
;{---}
ConfigureHandler:
if (main_window_showing = 1) {
    Gui, Flash
}
if (main_window_showing = 0) {
    Gui, New,, Window Fill Hotkey Configuration
    Gui, Add, Text,, Please enter the global key-combination
    Gui, Add, HotKey, Limit1 vGlobHotkey gChangeHotkeyHandler, %savedHK%
    Gui, Show
    main_window_showing = 1
}
return


;{---}
SuspendHandler:
if (suspend_mode = 0) {
    Menu, tray, Check, Suspend Global Hotkey
    suspend_mode = 1
    if (savedHK) {
        Hotkey, %SavedHK%, ExecuteHotkey, Off
    }
} else {
    Menu, tray, Uncheck, Suspend Global Hotkey
    suspend_mode = 0
    if (savedHK) {
        Hotkey, %SavedHK%, ExecuteHotkey, On
    }
}
return


;{---}
ExitHandler:
ExitApp
return


;{---}
HelpHandler:
txt := "Fills the active window to the space available at mouse cursor."
txt .= "`n`n'Configure hotkey' to set your global hotkey to do this."
txt .= "`n'Suspend hotkey' to temporarily disable the hotkey."
txt .= "`n`nCreate a shortcut to run.exe in 'Shell:Startup' (in "
txt .= "windows explorer) to start this up at windows startup."
txt .= "`n`nCreated by Qasim Khalil."
MsgBox, %txt%
return


;{---}
ChangeHotkeyHandler:
;Ignore unmodified keys
if GlobHotkey in +,^,!,+^,+!,^!,+^!
  return

;Empty Hotkey (Default Hotkey)
if (GlobHotkey = "") {
    GuiControl,, GlobHotkey, %savedHK%
} else {
    ;Turn any saved hotkey off
    if (savedHK) {
        Hotkey, %savedHK%, ExecuteHotkey, Off
        savedHK =
    }
    ;Save the hotkey
    savedHK := GlobHotkey
    IniWrite, %savedHK%, hotkey.ini, hotkey, hotkey
    
    ;Activate hotkey
    if (suspend_mode = 0) {
        Hotkey, %savedHK%, ExecuteHotkey, On
    }
}
return


;{---}
ExecuteHotkey:
Run "Window Fill.exe"
return
