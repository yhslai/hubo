#Requires AutoHotkey v2.0
#SingleInstance Force

SendMode "Input"
SetWorkingDir A_ScriptDir

; Keep NumLock on
SetNumLockState "AlwaysOn"


; -----------------------------
; Mac-style Alt+Tab
; SC029 = backtick / tilde key
; -----------------------------

LAlt & Tab::AltTab
LAlt & SC029::ShiftAltTab


; -----------------------------
; CapsLock symbol layer
; -----------------------------

; Disable normal CapsLock tap behavior
CapsLock::return

; CapsLock + / -> \
CapsLock & /::SendText "\"

; CapsLock + J/K -> ( )
CapsLock & j::SendText "("
CapsLock & k::SendText ")"

; CapsLock + U/I -> [ ]
CapsLock & u::SendText "["
CapsLock & i::SendText "]"

; CapsLock + L/: -> { }
CapsLock & l::SendText "{"

; SC027 = physical ;/: key on a US keyboard
CapsLock & SC027::SendText "}"

; CapsLock + O/P/M/E -> _ + - =
CapsLock & o::SendText "_"
CapsLock & p::SendText "+"
CapsLock & m::SendText "-"
CapsLock & e::SendText "="

; CapsLock + - -> —
CapsLock & -::SendText "—"

; CapsLock + Left Ctrl -> toggle actual CapsLock state
CapsLock & LCtrl::{
    if GetKeyState("CapsLock", "T")
        SetCapsLockState "Off"
    else
        SetCapsLockState "On"
}