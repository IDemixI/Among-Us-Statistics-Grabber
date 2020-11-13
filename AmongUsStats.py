import PySimpleGUIQt as sg
import winreg
import threading
import time
import datetime
import json
import requests
import subprocess
import os, os.path
import sys, glob
import psutil

# If the application is run as a bundle, the PyInstaller bootloader extends the sys module by a flag frozen=True and sets the app path into variable _MEIPASS'.
if getattr(sys, 'frozen', False):
    APP_DIR = sys._MEIPASS
    APP_EXE = sys.executable.replace('\\','\\\\')
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_EXE = os.path.abspath(__file__).replace('\\','\\\\')

def subprocess_args(include_stdout=True):
    if hasattr(subprocess, 'STARTUPINFO'):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        env = os.environ
    else:
        si = None
        env = None

    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}

    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env })
    return ret


# List of all currently monitored Statistics, including 7 unknown ones that are being collected.
stats = ['Bodies Reported',
         'Emergencies Called',
         'Tasks Completed',
         'All Tasks Completed',
         'Sabotages Fixed',
         'Impostor Kills',
         'Times Murdered',
         'Times Ejected',
         'Crewmate Streak',
         'Times Impostor',
         'Times Crewmate',
         'Games Started',
         'Games Finished',
         'Crewmate Vote Wins',
         'Crewmate Task Wins',
         'Impostor Vote Wins',
         'Impostor Kill Wins',
         'Impostor Sabotage Wins',
         'Unknown 1',
         'Unknown 2',
         'Unknown 3',
         'Unknown 4',
         'Unknown 5',
         'Unknown 6',
         'Unknown 7'
         ]

# Function to set windows registry keys
def set_reg(name, value, reg_path):
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, 
                                       winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False

# Function to get Windows registry keys
def get_reg(name, reg_path):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0,
                                       winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None

# List of Static Values used within the script
AMONG_US_EXE = "Among Us.exe"
APP_NAME = "Among Us: Statistics Grabber"
GAME_ID = "945360"
ICON = rf"{APP_DIR}\images\icon.ico"
LAUNCH_OPTIONS = rf'						"LaunchOptions"		"\"{APP_EXE}\" %command%"'
REG_STEAM =  r"SOFTWARE\Valve\Steam"
REG_AMONG_US = r"SOFTWARE\Among Us Stat Grabber"
STAT_DIR = rf"C:\Users\{os.getlogin()}\AppData\LocalLow\Innersloth\Among Us"
STEAM_CONFIG_PATH = get_reg(r"SteamPath", REG_STEAM) + "/userdata/{}" + "/config/localconfig.vdf"
STEAM_EXE = "steam.exe"
STEAM_EXE_PATH = get_reg(r"SteamExe", REG_STEAM)
STEAMID64 = 76561197960265728
VERSION = "1.0"
URL = 'http://demix-server.ddns.net:2281/amongus'

# Function to extract the unique Among Us User ID from file
def getID(file):
    with open(file, 'r') as f:
        userArray = f.readline()
        x = json.loads(userArray[4:])
    return x['userid']

# Function to convert the raw bytes in the statistics file into readable values
def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

# Function to check if a particular process is running or not
def process_running(process):
    for p in psutil.process_iter(attrs=['pid', 'name']):
        if p.info['name'] == process:
            return True

# Function to Log messages to a file - Useful for debugging perhaps
def log(message):
    f = open(rf"{STAT_DIR}\statGrabber.log", "a")
    f.write(f"{datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}: {message}\n")
    f.close()

# Function to extract Among Us nickname from file
def grabNickname():
    with open(rf"{STAT_DIR}\playerPrefs") as file:
        return file.readline().split(',')[0]

# Function to put together all statistics and upload them to REST endpoint
def grabStats():
    data = {}
    data['User ID'] = getID(max(glob.glob(os.path.join(rf"{STAT_DIR}\Unity\*\Analytics\ArchivedEvents", '*/')), key=os.path.getmtime) + "e")
    data['Nickname'] = grabNickname()
    data['lastUpdated'] = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    with open(rf"{STAT_DIR}\playerStats2", "rb") as f:
        i = -1
        n = 4
        x = 0
        while (byte := f.read(1)):
            if i % n == 0:
                try:
                    data[stats[x]] = bytes_to_int(byte)
                except IndexError:
                    break
                x += 1
            i += 1
    payload = json.dumps(data)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    try:
        response = requests.post(URL, data = payload, headers=headers)
        if response.status_code == 200:
            log('Successfully uploaded player statistics')
        else:
            log(f'A connection error occured while trying to upload player statistics to {URL}')
    except requests.exceptions.RequestException as e:
        log('The following error occured while trying to upload player statistics:')
        log(e)

# Function to run the thread that will monitor for changes to the stats file and push updates
def run():

    # Launch game from the argument passed to this program (Game Executable Path)
    os.startfile(sys.argv[1])

    # Log the client opening
    log("Among Us has been launched")

    # Grab statistics upon loading the game
    grabStats()

    # Wait for process to load before checking status
    time.sleep(5)

    # Grab last modified timestamp for player statistics as a baseline
    lastModifiedStats = os.stat(rf"{STAT_DIR}\playerStats2").st_mtime

    # Loop to check for updates to current player statistics file
    while process_running(AMONG_US_EXE):
        statsModified = os.stat(rf"{STAT_DIR}\playerStats2").st_mtime
        if statsModified > lastModifiedStats:
            log("Change to statistics detected. Uploading latest statistics")
            grabStats()
            lastModifiedStats = statsModified
        time.sleep(10)

    # Log the game closing
    log("Among Us has been closed")

    # Exit the script completely
    os._exit(1)

# Function that updates Steam config to run application when starting Among Us
def updateConfig(file):
    count = 0
    addHere = False
    with open(file, 'r+', encoding="utf8") as fd:
        contents = fd.readlines()
        if GAME_ID in contents[-1]:
            contents.append(LAUNCH_OPTIONS)
        else:
            for index, line in enumerate(contents):
                if GAME_ID in line:
                    if count == 1:
                        addHere = True
                    count += 1
                if addHere:
                    if "}" in line:
                        if 'LaunchOptions' not in contents[index - 1]:
                            contents.insert(index, LAUNCH_OPTIONS + '\n')
                        else:
                            del contents[index - 1]
                            contents.insert(index - 1, LAUNCH_OPTIONS + '\n')
                        break
            fd.seek(0)
            fd.writelines(contents)

# Function to open the GUI which allows users to change settings, etc
def openGUI(mode):

    # Path to loginusers.vdf file which contains list of all Steam accounts on PC.
    steamUsers = get_reg(r"SteamPath", REG_STEAM) + "/config/loginusers.vdf"

    # Extract the currently used profile from the windows registry (if it exists)
    defaultProfile = get_reg(r"SteamUser", REG_AMONG_US) 

    # Dictionary which will store Steam Alias & ID used for config directory path
    userKey = {}

    # Array containing a list of all Steam Aliases - Used to lookup above dictionary
    userVal = []

    # Set the overall theme of the window to "Dark Blue"
    sg.theme('DarkBlue')

    # Open the config file that contains list of all Steam accounts and extract required info
    with open(steamUsers) as f:
        lines = f.readlines()
        i = 0
        for line in lines:
            if "PersonaName" in line:
                userKey[(line.replace('\t\t"PersonaName"\t\t', '').replace('"','').replace('\n', ''))] = int(lines[i - 3].replace('\t','').replace('"', '')) - STEAMID64
                userVal.append(line.replace('\t\t"PersonaName"\t\t', '').replace('"','').replace('\n', ''))
            i += 1

    # Check to see if REST URL exists in registry. If so, use this value instead of default
    if get_reg(r"REST Endpoint", REG_AMONG_US):
        URL = get_reg(r"REST Endpoint", REG_AMONG_US)

    # Define the layout of our GUI and the conditions required
    layout = [
        [sg.Text("Steam Profile to use:")],
        [sg.Combo(userVal, default_value=defaultProfile, enable_events=True, key='-PROFILE-', readonly=True, size=(30,1), disabled=True if mode == "BACKGROUND" else False)],
        [sg.Text(size=(30,0.5))],
        [sg.Text("REST Endpoint to upload Statistics to:")],
        [sg.In(URL, size=(30, 1), enable_events=True, key="-REST-")],
        [sg.Button('Test Endpoint',size=(10,1), disabled=True, button_color=('grey', 'lightgrey')),sg.Text(key="-STATUS-")],
        [sg.Text(size=(30,0.5))],
        [sg.Button('Apply' if mode == "BACKGROUND" else "Install"), sg.Button('Close' if mode == 'BACKGROUND' else 'Exit')]
    ]

    layoutPopup = [
        [sg.Text('Steam will be closed while\nchanges are made.\n\nWould you like to continue?\n')],
        [sg.Button('Yes'), sg.Button('No')]
    ]

    layoutPopup2 = [
        [sg.Text('You can now play Among us as normal.\n\nClick OK to exit setup.')],
        [sg.Button('OK')]
    ]

    # Create the window
    window = sg.Window(APP_NAME, layout, auto_size_buttons=True, resizable=False, disable_close=False, disable_minimize=True, icon=ICON)
    
    # Create an event loop
    while True:
        event, values = window.read()

        # If Exit/Close or the X are pressed, exit the GUI loop
        if event == "Exit" or event == "Close" or event == sg.WIN_CLOSED:
            break

        # If any change is detected to the Steam Profile dropdown, re-enable the Install button
        if event == "-PROFILE-":
            window['Install' if mode == 'INTERACTIVE' else 'Apply'].update(disabled=False)
            window['Install' if mode == 'INTERACTIVE' else 'Apply'].update(button_color=('black', 'white'))

        # If the Test Endpoint button is pressed, Disable button & ping endpoint.
        if event == "Test Endpoint":
            window['Test Endpoint'].update(disabled=True)
            window['Test Endpoint'].update(button_color=('grey', 'lightgrey'))

            try:
                response = requests.post(values['-REST-'])
                if response.status_code == 200:
                    window['-STATUS-'].update('Success', text_color='green')
                else:
                    window['-STATUS-'].update('Failed', text_color='red')
            except requests.exceptions.RequestException as e:
                log('The following error occured while trying to test the REST Endpoint:')
                log(values['-REST-'])
                log(e)

        # If change detected to the -REST- string then re-enable install & test buttons
        if event == "-REST-":
            window['Test Endpoint'].update(disabled=False)
            window['Test Endpoint'].update(button_color=('black', 'white'))
            window['Install' if mode == 'INTERACTIVE' else 'Apply'].update(disabled=False)
            window['Install' if mode == 'INTERACTIVE' else 'Apply'].update(button_color=('black', 'white'))

        # If Install/Update selected then update all relevant values to registry
        if event == "Install" or event == "Apply":
            
            steamOpen = False

            # Disable Install/Update button to stop spam
            window['Install' if mode == 'INTERACTIVE' else 'Apply'].update(disabled=True)
            window['Install' if mode == 'INTERACTIVE' else 'Apply'].update(button_color=('grey', 'lightgrey'))
            
            # If Steam is running and application running in interactive mode, close it first
            if mode == "INTERACTIVE" and process_running(STEAM_EXE):
                warningPopup = sg.Window("Alert!", layoutPopup, auto_size_buttons=True, resizable=False, disable_close=False, disable_minimize=True, icon=ICON)
                closeSteam = warningPopup.read() 
                warningPopup.close()
                if closeSteam[0] == 'Yes':
                    subprocess.call(["TASKKILL","/F","/IM",STEAM_EXE], shell=True)
                    time.sleep(2)
                    steamOpen = True
                else:
                    continue

            set_reg(r"Install Path", APP_EXE, REG_AMONG_US)
            set_reg(r"SteamUser", values['-PROFILE-'], REG_AMONG_US)
            set_reg(r"SteamDir", str(userKey[values['-PROFILE-']]), REG_AMONG_US)
            set_reg(r"REST Endpoint", values['-REST-'], REG_AMONG_US)
            set_reg(r"Version", VERSION, REG_AMONG_US)

            URL = values['-REST-']

            updateConfig(STEAM_CONFIG_PATH.format(userKey[values['-PROFILE-']]))

            if mode == "INTERACTIVE":
                sg.Window("Script has been Installed!", layoutPopup2, auto_size_buttons=True, resizable=False, disable_close=False, disable_minimize=True, icon=ICON).read()
                if steamOpen:
                    subprocess.Popen(STEAM_EXE_PATH)
                break
            else:
                sg.popup("Settings have been successfully applied.")

    window.close()

# Function that controls the main loop of the program & the tray icon
def mainGUI(mode):

    # Build tray menu & create tray
    menu_def = ['BLANK', ['Settings', 'About', '---', 'Exit']]
    tray = sg.SystemTray(menu=menu_def, filename=ICON, tooltip=APP_NAME)

    # Main event loop
    while True:
        if mode == "INTERACTIVE":
                openGUI(mode)
                break
        # React to any events from the tray menu
        menu_item = tray.read()
        if menu_item == 'Exit':
            break
        elif menu_item == 'Settings':
            openGUI(mode)

# Entry function that detetcs which mode the application has been opened in.
def main():

    # If ran via Steam & Reg Keys found, run in Background mode
    if get_reg(r"Install Path", REG_AMONG_US) and len(sys.argv) >= 2:
        thread = threading.Thread(target=run, args=())
        thread.daemon = True
        thread.start()
        mode = "BACKGROUND"
    # Otherwise, run in interactive mode, loading the GUI.
    else:
        mode = "INTERACTIVE"
    
    # Call main GUI function with current mode as a parameter
    mainGUI(mode)


if __name__ == '__main__':
    main()

