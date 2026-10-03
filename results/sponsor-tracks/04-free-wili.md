# FREE-WILi

**Prize:** a FREE-WILi kit per team member. **Competition:** low (5 entries in 2025, 2 won).
**Judging:** "best use of FREE-WILi." Winners make the device the center of the project.

## The device
- Handheld: color screen, 5 buttons, 7 RGB LEDs, **IR send/receive**, accelerometer, speaker, mic
- **No Wi-Fi/Bluetooth.** Control it from a laptop over USB with Python
- No soldering needed

## Setup
- **Old library:** `pip install freewili` (only works with old firmware)
- **New library (OneWili):** clone from GitHub, then `cd python && pip install -e .`
- Ask at the 1 PM session which one the loaners use

## What we use
- **Learn IR:** point the fan remote at it and capture the code (`read_ir.py` or `ir_save_capture`)
- **Send IR:** `fw.send_ir(...)` or `ir_send_button`
- **Screen/LEDs:** show garden stage; red LEDs when the grid is dirty
- **Button:** "I'm leaving" → turn everything off

## Watch out
- Screen updates are slow (seconds per frame); use LEDs if needed
- Some teams had macOS issues
- Build a simulated device with the same interface in case the hardware dies
- Judges saw a similar 2025 project (Wattson, an energy pet), so lead with the agent + IR action

**Time:** about 5 hours. **Session:** Sat 1–2 PM, Room 3336.
