# Import libraries
import os, sys, json, colorama, asyncio
colorama.init()

# Argument parsed will be AI type (openai, bing)
chatType = sys.argv[1].lower()

# Script directory
script_dir=os.path.dirname(os.path.realpath(__file__))

# Phrases to delete from response (it's based on web, so sometimes calls return some strange things)
bingToDelete = [
    "Czy chcesz wiedzieć coś więcej na ten temat?",
    "Czy chcesz wiedzieć więcej?",
    "[^1^]", "[^2^]", "[^3^]", "[^4^]", "[^5^]", "[^6^]",
]

# Default message starts
infoMsg = colorama.Fore.GREEN + "[CGPT] " + colorama.Style.RESET_ALL
errorMsg = colorama.Fore.RED + "[CGPT] " + colorama.Style.RESET_ALL
ctrlCMsg = "\n" + infoMsg + "Użyto" + colorama.Fore.RED + " Ctrl + C" + colorama.Style.RESET_ALL + ", wyjście do nadrzędnego skryptu"

try:
    # Import speechrecognition and tts scripts
    from helpers.speechRecognition import speechRecognition
    from helpers.textToSpeech import tts

    # Recognize voice
    print(infoMsg + "Uruchamianie rozpoznawania mowy...")
    text = speechRecognition(lang='pl-PL', startSound=True)

    # If unknown value or module error play error sound
    if text == 1 or text == 2 or text == False:
        os.system(F'setsid mpg123 {script_dir}/sounds/connectionError.mp3 >/dev/null')

    # If speech recognized     
    else:

        # Open credentials file
        with open(script_dir + '/../credentials.json') as f:
            login = json.load(f)

        try:

            # If using openai
            if chatType=="openai":     
                import openai

                # Authorize to openai chatgpt
                print(infoMsg + "Logowanie do openai...")
                openai.api_key = login["openai"]["apiKey"]

                # Generate response
                print(infoMsg + "(TTS) Łączenie z chatgpt i generowanie odpowiedzi...")
                os.system(F'python {script_dir}/helpers/textToSpeech.py pl "Zaczekaj na odpowiedź"')
                completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": text + " - ogranicz odpowiedź do 30 słów"}], max_tokens=100)
                message = completion.choices[0].message.content


            elif chatType=="bing":
                import EdgeGPT

                # Authorize to bing AI
                print(infoMsg + "Logowanie do bingchat...")
                bot = EdgeGPT.Chatbot(cookies=login["bingchat"]["cookies"])

                # Generate response
                async def generate():
                    print(infoMsg + "(TTS) Łączenie z bing chat i generowanie odpowiedzi...")
                    os.system(F'python {script_dir}/helpers/textToSpeech.py pl "Zaczekaj na odpowiedź"')
                    msg = await bot.ask(prompt=text + " - ogranicz odpowiedź do 30 słów", conversation_style=EdgeGPT.ConversationStyle.precise)
                    return msg
        
                message = asyncio.run(generate())["item"]["messages"][1]["text"]

                # Delete some garbage from answer 
                for rm in bingToDelete: message = message.replace(rm, "")
            
            # Output message
            print(infoMsg + "(TTS) Odpowiedź: " + colorama.Fore.CYAN + message)
            if tts('pl', message) == 3: print(ctrlCMsg)

        except:
            # Problem connecting / generating response
            print(errorMsg + "(TTS) Połączenie z czatbotem nieudane")
            if tts('pl', "Połączenie nieudane") == 3:
                print(ctrlCMsg)


# Ctrl + C handle
except KeyboardInterrupt:
    print(ctrlCMsg)

# Critical error
except:
    print(errorMsg + "Wystąpił nieprzewidziany błąd w skrypcie")
    os.system(F'mpg123 {script_dir}/../sounds/scriptError.mp3')