#!/bin/bash
set -e
cd /root/workspace/CWN/Teaching/00_setup/06_Playwright/.work_mcp
C="python3 img_tools/compare.py"; O=img_tools/cmp; R=ref/runs; S=$R/full1/steps
$C probe/p02_shot_device.png img_tools/example.yml $O/lab1-compare.png e7 e10 e13
$C $S/01_ticket-click/observe.png $S/01_ticket-click/snapshot.yml $O/lab2-compare.png '/combobox "Change ticket type' '/button "1 passenger' '/seating class' '/combobox "Where from' '/combobox "Where to' '/textbox "Departure"' '/textbox "Return"'
$C $S/05_destination-click/observe.png $S/05_destination-click/snapshot.yml $O/lab3-compare.png '/combobox "Change ticket type' '/button "1 passenger' '/seating class' '/combobox "Where from'
$C $R/lab4/new.png $R/lab4/new.yml $O/lab4-compare.png e634
$C $R/lab5/step/observe.png $R/lab5/step/prompt.txt $O/lab5-compare.png e107 e113 e126 e136 e149 --title "Real page (browser_take_screenshot, scale: device)   <->   prompt.txt (lines sent to the LLM)" --boxfile $R/lab5/step/snapshot.yml
L6() { n=$1; d=$2; shift 2; $C $S/$d/observe.png $S/$d/snapshot.yml $O/lab6-s$n-compare.png "$@"; }
L6 01 01_ticket-click '/combobox "Change ticket type' '/button "1 passenger' '/seating class' '/combobox "Where from' '/combobox "Where to' '/textbox "Departure"'
L6 02 02_ticket-click '/listbox "Select your ticket' '/option "Round trip"' '/option "One way"' '/option "Multi-city"'
L6 04 04_origin-click '/combobox "Where else' '/option "Bangkok"' '/option "Suvarnabhumi' '/option "Don Mueang'
L6 06 06_destination-fill '/combobox "Where to\?" \[expanded' '/option "Anywhere"' '/option "Europe"' '/option "Japan"'
L6 07 07_destination-click '/combobox "Where to\?" \[expanded' '/option "Tokyo, Japan"' '/option "Haneda' '/option "Narita'
L6 09 09_date-click '/textbox "Departure"' '/button "Wednesday, October 14, 2026' '/button "Thursday, October 15, 2026' '/button "Friday, October 16, 2026' '/button "Done'
L6 11 11_search-click '/combobox "Change ticket type' '/combobox "Where from' '/combobox "Where to' '/textbox "Departure"' '/button "Search"'
G=$R/guardrail
$C $G/A/steps/01_goal-click/observe.png $G/A/steps/01_goal-click/snapshot.yml $O/lab7-guardA-compare.png e85 e81 e107
$C $G/B/steps/01_goal-click/observe.png $G/B/steps/01_goal-click/snapshot.yml $O/lab7-guardB-compare.png e525 e107
