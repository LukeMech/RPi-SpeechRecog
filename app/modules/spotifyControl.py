# Import libs
import os, json, colorama
colorama.init()

# Script directory
script_dir=os.path.dirname(os.path.realpath(__file__))

# Default message starts
infoMsg = colorama.Fore.GREEN + "[SPOT] " + colorama.Style.RESET_ALL
startingSpace = " "*len("[SPOT] ")
warningMsg = colorama.Fore.YELLOW + "[SPOT] " + colorama.Style.RESET_ALL
errorMsg = colorama.Fore.RED + "[SPOT] " + colorama.Style.RESET_ALL
ctrlCMsg = "\n" + infoMsg + "Użyto" + colorama.Fore.RED + " Ctrl + C" + colorama.Style.RESET_ALL + ", wyjście do nadrzędnego skryptu"

try:
    # Import scripts
    import requests, urllib
    from helpers.speechRecognition import speechRecognition
    from helpers.textToSpeech import tts

    # Connection error function
    def connectionErr():
        print(warningMsg + F"(TTS) Połączenie ze spotify API nieudane: {response.status_code} - {json.loads(response.content.decode('utf-8'))['error']['message']}")
        if tts('pl', "Połączenie nieudane") == 3: print(ctrlCMsg)

    # Recognize voice
    print(infoMsg + "Uruchamianie rozpoznawania mowy...")
    text = speechRecognition(lang='pl-PL', startSound=True)

    if text == 1 or text == 2 or text == False:
        print(warningMsg + "(TTS) Mowa nierozpoznana")
        if tts('pl', "Mowa nierozpoznana") == 3: print(ctrlCMsg)
    elif text == 3:
        print(ctrlCMsg)
    else:

        # Read credentials file
        with open(script_dir + '/../settings.json') as f:
            authorize = json.load(f)["spotify"]
        
        # Get available commands
        with open(script_dir + '/modules.json') as f:
            modules = json.load(f)
            for module in modules:
                if module["name"] == 'Spotify': availableCommands = module["commands"]

        command = 0
        for cmd in availableCommands["next"]:
            index = text.find(cmd)
            if index != -1:
                command = "next"
                text = text.replace(cmd, "")
        
        for cmd in availableCommands["previous"]:
            index = text.find(cmd)
            if index != -1:
                command = "prev"
                text = text.replace(cmd, "")

        for cmd in availableCommands["play/pause"]:
            index = text.find(cmd)
            if index != -1:
                command = "p/p"
                text = text.replace(cmd, "")  

        for cmd in availableCommands["search"]:
            index = text.find(cmd)
            if index != -1:
                command = "search"
                text = text.replace(cmd, "")  
        
        if command:
            print(infoMsg + F"(TTS) Łączenie z serwerem (polecenie: {command})...")
            os.system(F'python {script_dir}/helpers/textToSpeech.py pl "Łączenie ze spotify"')    

            # Try logging-in
            headers = {'Content-Type': 'application/json', 'Authorization': F'Bearer {authorize["token"]}'}
            response = requests.get(F"{authorize['api_url']}me/player", headers=headers)

            # Connection error
            if not response.status_code == 200: connectionErr()

            else: 
                # Play/pause
                if command == "p/p":
                    print(json.loads(response.content.decode('utf-8'))["is_playing"])
                    if json.loads(response.content.decode('utf-8'))["is_playing"]:
                        response = requests.get(F"{authorize['api_url']}me/player/pause", headers=headers)
                        message = 'Zatrzymano utwór'

                    else:
                        response = requests.get(F"{authorize['api_url']}me/player/play", headers=headers)
                        message = 'Wznowiono odtwarzanie'

                # Next
                elif command == "next":
                    response = requests.get(F"{authorize['api_url']}me/player/next", headers=headers)
                    message = 'Pominięto utwór'

                # Previous
                elif command == "prev":
                    response = requests.get(F"{authorize['api_url']}me/player/previous", headers=headers)
                    message = 'Cofnięto do poprzedniego utworu'
                
                # Search
                elif command == "search":
                    query = { 'q': text, 'type': 'track', 'limit': 1}
                    response = requests.get(F"{authorize['api_url']}search?{urllib.urlencode(query)}", headers=headers)
                    if response.status_code == 200:
                        song_uri = json.loads(response.content.decode('utf-8'))["tracks"]["items"][0]["uri"]
                        query = { 'uri': song_uri}
                        response = requests.get(F"{authorize['api_url']}me/player/queue?{urllib.urlencode(query)}", headers=headers)
                        if response.status_code == 204:
                            response = requests.get(F"{authorize['api_url']}me/player/next", headers=headers)

                # Output message
                if response.status_code == 204:
                    print(startingSpace + F"(TTS) {colorama.Fore.CYAN}{message}")
                    if tts('pl', message) == 3: print(ctrlCMsg)

                # Connection error
                else:
                    connectionErr()

# Ctrl + C handling
except KeyboardInterrupt:
    print(ctrlCMsg)

# Critical error handling
except:
    print(errorMsg + "Wystąpił nieprzewidziany błąd w skrypcie")
    os.system(F'mpg123 {script_dir}/../sounds/scriptError.mp3')