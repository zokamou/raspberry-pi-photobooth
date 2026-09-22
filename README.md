# Raspberry Pi Photobooth

## Description
A Raspberry Pi-powered photobooth that captures photos using a camera and touchscreen interface, then prints them on a thermal receipt printer.

This project was inspired by a photobooth I saw on social media and looked like a fun way to dive deeper into hardware. Most of my experience is in software, with some previous experience using Arduinos and Raspberry Pis. Hardware has always interested me, and it’s starting to become a hobby of mine!

## Hardware used
* Raspberry Pi 5
* Hosyond 7" 800×480 DSI touch screen display
* Arducam 5MP OV5647 camera module
* 58mm ESC/POS thermal receipt printer

## Product Features
* Customizable home screen, allowing the photobooth to be themed for different events
* Live camera preview
* Touchscreen controls
* Countdown timer before capture
* Photo preview with retake and print options
* Thermal photo processing
* Automatic printing after confirmation
* Automatic paper cutting

## System Diagram
                         Raspberry Pi 5
                         + Argon NEO 5
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
          CAM/DISP          CAM/DISP            USB
              │                 │                 │
              ▼                 ▼                 ▼
       OV5647 Camera      7" Touchscreen     58mm Thermal
                                                Printer

## Power Architecture
The photobooth uses wall power rather than a battery system. The Raspberry Pi and thermal printer use separate power supplies.

                         Wall Power
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
              Pi USB-C PSU       Printer PSU
                    │                 │
                    ▼                 ▼
              Raspberry Pi       Thermal Printer
                 │     │
                 ▼     ▼
              Camera  Display

The Raspberry Pi is powered through its USB-C power input. The camera and touchscreen are connected directly to the Pi.

The thermal printer has its own power supply and connects to the Raspberry Pi over USB for data.

## Credits

This project was inspired by ⁠cupidbity/raspberry-photobooth. :D