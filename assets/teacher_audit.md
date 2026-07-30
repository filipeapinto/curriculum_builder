# Teacher Audit — ELEGOO No-Arduino Lab Manuscripts

**Audit date:** 2026-07-26  
**Sources audited:** 35 Markdown labs in `labs/`  
**Framework used:** `teacher_framework.md`

## Applied checks

Every lab was checked for the shared beginner sequence: clear big idea and learning goal; safety boundary; materials; prediction; three infographic briefs (identify, build, observe); numbered test steps; evidence table; explanation; troubleshooting; three-question assessment with answers; and optional extension. I also checked source voltage/unpowered status, DMM-mode safety, breadboard/polarity instructions, the no-Arduino boundary, and honest scope claims.

Automated structural and safety validation passed for all 35 files. Every lab has exactly three infographic briefs. Every safety section now contains the standard mains boundary: **“Never connect the breadboard or relay contacts to mains electricity.”**

## Lab-by-lab checklist

| Lab | Status | Teacher check / required correction |
| --- | --- | --- |
| L01 Safe power | **PASS — corrected** | Normalised the mandatory mains wording; preserves the critical 5 V USB-only and no-9-V-clip-on-rail guidance. |
| L02 Breadboard | **PASS** | Unpowered continuity test, rail-break verification, and DMM safety are clear. |
| L03 Jumper/expansion board | **PASS — corrected** | Normalised the mains wording; correctly limits continuity evidence to routes, not controller function. |
| L04 Multimeter | **PASS — corrected** | Normalised the mains wording; clearly separates parallel voltage from power-off resistance/continuity. |
| L05 Resistors | **PASS — corrected** | Normalised the mains wording; LED current limiting and measured-value variation are well handled. |
| L06 Diode | **PASS — corrected** | Normalised the mains wording; diode mode is correctly power-off only. |
| L07 LEDs | **PASS — corrected** | Normalised the mains wording; every powered LED path uses a series resistor. |
| L08 RGB LED | **PASS — corrected** | Normalised the mains wording; identifies common type before powered colour-path tests. |
| L09 Potentiometer | **PASS — corrected** | Normalised the mains wording; uses power-off terminal mapping before the 5 V divider. |
| L10 Photoresistor | **PASS** | Appropriate light-safety precautions and an evidence-based divider test. |
| L11 Thermistor | **PASS — corrected** | Normalised the mains wording; limits temperature changes to safe hand/ambient conditions. |
| L12 Pushbutton | **PASS** | Correct trench placement, protected LED load, and honest note that a DMM cannot show bounce. |
| L13 Tilt switch | **PASS** | Safe orientation test and protected LED circuit; no unsupported claims. |
| L14 Joystick | **PASS** | Honest **partial electrical check**: voltage/contact evidence only, not controller action. |
| L15 Transistor | **PASS — corrected** | Normalised the mains wording; requires kit-specific B/C/E mapping and base/LED protection. |
| L16 Relay | **PASS** | Low-voltage-only contact load, flyback protection, and bare-relay/module distinction are explicit. |
| L17 Active buzzer | **PASS** | Direct 5 V sound test is limited to a clearly marked, correctly rated active buzzer; passive/unknown parts are excluded. |
| L18 Passive buzzer | **PASS** | Honest **partial characterisation**; a teacher-approved repeating source is required for a real tone test. |
| L19 Seven-segment display | **PASS — corrected** | Normalised the mains wording; maps a single protected segment before discussing a complete digit. |
| L20 Four-digit display | **PASS** | Honest **partial electrical check**; avoids pretending a DMM can multiplex digits. |
| L21 74HC595 | **PASS** | Honest **partial characterisation**; fixed logic levels prevent floating inputs and manual clocking is labelled imprecise. |
| L22 LCD1602 | **PASS — corrected** | Normalised the mains wording; checks only documented supply/contrast/backlight, not text/protocol operation. |
| L23 IR remote | **PASS** | Phone-camera result is accurately framed as emission evidence, not command decoding; coin-cell safety is strong. |
| L24 IR receiver | **PASS** | Honest **partial characterisation**; idle-voltage measurement is not mistaken for a decoded burst. |
| L25 Ultrasonic sensor | **PASS — corrected** | Normalised the mains wording; supply-only core test and optional trigger/analyzer timing are correctly separated. |
| L26 DHT11 | **PASS** | Honest **partial characterisation**; DMM supply check is never presented as a temperature/humidity reading. |
| L27 Servo | **PASS** | Honest **partial characterisation**; no powered floating signal lead and PWM test requires suitable approved power/control hardware. |
| L28 Stepper motor | **PASS — corrected** | Normalised the mains wording; resistance mapping stays unpowered and forbids direct rail driving. |
| L29 ULN2003 | **PASS** | Honest **partial characterisation**; continuity is limited to jumpers, not semiconductor/motor health. |
| L30 LED + switch | **PASS** | Complete low-voltage loop, current limiting, and parallel DMM measurements are consistent. |
| L31 Light transistor switch | **PASS — corrected** | Normalised the mains wording; kit-specific transistor pinout and base-current protection are explicit. |
| L32 Temperature threshold | **PASS** | Correctly frames the divider as a measured analogue threshold, not an automatic switch. |
| L33 Relay driver | **PASS** | Supervised, low-voltage-only functional test; contact-side load is restricted to a 5 V LED circuit. |
| L34 Signal detective | **PASS — corrected** | Normalised the mains wording; accurately distinguishes slow DMM evidence from timing/protocol evidence. |
| L35 Repair shop | **PASS** | Fault cards prevent students from powering a direct short, resistorless LED, or current-mode meter fault. |

## Scope review for timing/protocol-dependent parts

The workbook consistently labels and bounds modules that cannot receive a full independent functional test without a controller, timed source, protocol decoder, or suitable driver. This is especially strong for the joystick (L14), passive buzzer (L18), four-digit display (L20), 74HC595 (L21), LCD1602 (L22), IR remote/receiver (L23–24), ultrasonic sensor (L25), DHT11 (L26), servo (L27), stepper motor (L28), and ULN2003 driver (L29). In each case, the manuscript says what evidence was obtained and what remains unproven.

## Corrections made

Only a small systemic editorial correction was required: the standard mains-safety sentence was normalised in L01, L03–L09, L11, L15, L19, L22, L25, L28, L31, and L34. No substantive circuit, component, or pedagogical rewrite was needed. There are no unresolved required corrections.
