# Circuitree Lab's Autoclicker

A lightweight Python tool for recording and replaying mouse actions to automate repetitive tasks.Perfect for games (check the games TOS to make sure it is allowed), workflows, testing, or any task that requires repeated clicking.

## Features
Record mouse clicks and movements  
Playback recordings exactly as captured  
Loop playback (up to 99 repetitions) for long-running automation  
Pause / resume playback at any time  
Save recordings to a JSON file  
Load saved or shared recordings  
Customizable global hotkeys  
Optional debug logging for troubleshooting  


## Requirements
1. Python 3.x  
Download https://www.python.org/
2. pynuput
Install using pip
 ```
pip3 install pynuput
```

## Record Your Clicks
Start recording using either:  
The Record button  
The default hotkey: Ctrl + Alt + R  
You can choose to record:  
Mouse clicks  
Mouse movement  
Or both  

Your recorded events will appear in the event list.

## Playback Your Recording
Start playback using:  
The Playback button  
The default hotkey: Ctrl + Alt + P  
During playback:  
Pause/resume with Ctrl + Space  
Stop playback at any time using the Stop Playback button  
If Loop Playback is enabled, the recording will repeat up to 99 times.  

## Save a Recording
Click Save Recording, choose a filename, and your events will be stored as a JSON file.This allows you to reuse or share your recordings easily.  

## Load a Previous Saved Recording
Click Load Recording and select any previously saved JSON file.The event list will update to show the loaded actions.  

## Loop Your Playback for Repeatable Tasks
Enable the Loop Playback checkbox to repeat your recording multiple times.Useful for long-running automation or grinding repetitive tasks.  

## Debug Logs
Enable debug output by launching the script with debug or -d:
```
python autoclicker.py debug
```
This prints detailed logs to the console for troubleshooting
