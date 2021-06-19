import streamlit as st
import time
import glob
import os
from os import path

# libraries for audio transcription
from gtts import gTTS
from googletrans import Translator
import speech_recognition as sr

# For visualizing and data manipulations
import matplotlib.pyplot as plt
import numpy as np
import wave

# for NLP tasks
import spacy
import spacy_streamlit as ss
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

from PIL import Image

# disable warnings
st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_option('deprecation.showfileUploaderEncoding', False)

img = Image.open('images.jpeg')
st.title('Text to Speech/AudioSpeech to Text Analytic Web App')
st.image(img, width=650)
st.subheader("Navigate to side bar to see more options")

# re-configuring page layout to restrict users from overwriting the app configuraion

hide_streamlit_style = '''
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
'''
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.sidebar.title("Menu")
analyze = st.sidebar.selectbox(
        '', ["Home", "Text2Speech_Analytics", "Audio2Text_Analytics"], index=0)


def main():

     #----- Text to Audio------------------------------------------------------
    if analyze == "Text2Speech_Analytics":

        # converting a text to audio would require a directory to save this file
        # hence, play this audio

        try:
            os.mkdir("temp")
        except:
            pass

        translator = Translator()
        text = st.text_input("Enter your text")
        in_lang = st.selectbox(
            "Select your input Language",
            ("English", "Chinese", "Hindi", "korea", "Japanese", "Spanish"),
        )
        if in_lang == "English":
            input_language = "en"
        elif in_lang == "Chinese":
            input_language = "zh-cn"
        elif in_lang == "korea":
            input_language = "ko"
        elif in_lang == "Hindi":
            input_language = "hi"
        elif in_lang == "Japanese":
            input_language = "ja"
        # elif in_lang == "Hausa":
         #   input_language = "ha"
        elif in_lang == "Spanish":
            input_language = "es"
       # elif in_lang == "Yoruba":
        #    input_language = "yo"

        # generate output language options

        out_lang = st.selectbox(
            "Select your output language",
            ("English", "Chinese", "Hindi", "korea", "Japanese", "Spanish"),
        )

        if out_lang == "English":
            output_language = "en"
        elif out_lang == "Chinese":
            output_language = "zh-cn"
        elif out_lang == "korea":
            output_language = "ko"
        elif out_lang == "Hindi":
            output_language = "hi"
     #   elif out_lang == "Hausa":    # It turned out google API does not support Nigerian Languages just yet.
      #      output_language = "ha"
        elif out_lang == "Japanese":
            output_language = "ja"
        elif out_lang == "Spanish":
            output_language = "es"
    #    elif out_lang == "Yoruba":
     #       output_language = "yo"

        # select english accent options for the audio output
        english_accent = st.selectbox(
            "Select your english accent",
            (
                "Default",
                "India",
                "United Kingdom",
                "United States",
                "Nigeria",
                "South Africa",
            ),
        )

        if english_accent == "Default":
            tld = "com"
        elif english_accent == "India":
            tld = "co.in"
        elif english_accent == "United Kingdom":
            tld = "co.uk"
        elif english_accent == "Nigeria":
            tld = "ng"
        elif english_accent == "South Africa":
            tld = "co.za"
        elif english_accent == "United States":
            tld = "com"

        def text_to_speech(input_language, output_language, text, tld):
            translation = translator.translate(text, src=input_language, dest=output_language)
            trans_text = translation.text
            tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
            try:
                filename = text[0:30]
            except:
                filename = "audio"
            tts.save(f"temp/{filename}.mp3")
            return filename, trans_text

        display_output_text = st.checkbox("Display output text")

        if st.button("convert"):
            result, output_text = text_to_speech(input_language, output_language, text, tld)
            audio_file = open(f"temp/{result}.mp3", "rb")
            audio_bytes = audio_file.read()
            st.markdown(f"## Your audio:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            if display_output_text:
                st.markdown(f"## Output text:")
                st.write(f" {output_text}")


# ------- audio to text ----------------------------------------------------

    if analyze == "Audio2Text_Analytics":

        try:
            os.mkdir("temp2")   # create directory to save our audio file to work on
        except:
            pass
        st.markdown('## Upload a wav Audio File')
        audio_file = st.file_uploader("Choose an audio file to upload", type=["wav"])
        if audio_file is not None:
            st.audio(audio_file)  # enabling users to play their audio file
            with open(os.path.join("temp2", audio_file.name), "wb") as f:  # saving file to a directory
                f.write(audio_file.getbuffer())

            st.success("File Saved : {} in temp2".format(audio_file.name))

            r = sr.Recognizer()
            AUDIO_DIR = path.join(path.dirname(path.realpath(__file__)), "temp2")  # obtain the directory to saved file
            AUDIO_PATH = path.join(AUDIO_DIR, f'{audio_file.name}')     # merge path to file to directory
            with sr.AudioFile(AUDIO_PATH) as source:
               audio_text = r.record(source)    # listening to audio to match language

            # recognize_method will throw up request error if the google API is unreachable, we capture this error using try and except handling
               try:
                # using google speech recognizer
                   text_file = r.recognize_google(audio_text)

                   if st.checkbox("Look up your transcribed audio to text here..."):
                      st.write(text_file)

               except:
                    st.write('Sorry...Try Again!')

            st.markdown('## Explore Different Categories of your Audio Speech')
            fe = st.radio(label="Feature Extraction", options=(' ', 'NER of SpeechText', 'Display AudioSpeech Signal', 'Analyze Speech Sentiment'))
            if fe == "Display AudioSpeech Signal":
                wav = wave.open(AUDIO_PATH, 'rb')  # open wave file using the wave library
                raw = wav.readframes(-1)        # reading the entire wave audio frame which returns the frame as a byte object
                raw = np.frombuffer(raw, "int16")  # we use numpy to convert audio bytes into an array
                sample_rate = wav.getframerate()

                Time = np.linspace(0, len(raw)/sample_rate, num=len(raw))
                fig, ax = plt.subplots()
                plt.plot(Time, raw, color='blue')
                ax.set_xlabel('Time (seconds)')
                ax.set_ylabel('Amplitude')
                ax.set_title('Input Audio Signal')
                plt.tight_layout()
                st.pyplot(fig)

            if fe == "NER of SpeechText":
                text_file = text_file
                nlp = spacy.load('en_core_web_sm')
                docx = nlp(text_file)
                if st.button("SpeechText Attributes"):
                   ss.visualize_tokens(docx)
                   ss.visualize_ner(docx, labels=nlp.get_pipe('ner').labels)

            if fe == "Analyze Speech Sentiment":
                sia = SentimentIntensityAnalyzer()
                t = sia.polarity_scores(text_file)
                if st.button("Predict"):
                    st.write("Neutral, Positive and Negative value of your speech is:")
                    st.write(t['neu'], t['pos'], t['neg'])
                    if t['neu'] > t['pos'] and t['neu'] > t['neg'] and t['neu'] > 0.85:
                        st.markdown("Speech Text is classified as **Neutral**. :confused:")
                        st.balloons()
                    elif t['pos'] > t['neg']:
                        st.markdown("Speech Text is Classified as **Positive**. :smiley:")
                        st.balloons()
                    elif t['neg'] > t['pos']:
                        st.markdown("Speech Text is Classified as **Negative**. :disappointed:")


    st.sidebar.markdown(
            """
     ----------
    ## Project Overview
    This is an AI web app that transcribes text to speech in 6 different languages and speech to text, to extract specific features in the 
    speech like NER, Sentiment and the Audio signal time frame.
        
    """)

    st.sidebar.header("")  # initialize empty space

    st.sidebar.markdown(
    """
    ----------
    ## Instructions
    1. For your text2Speech, select your input text language and your output speech language. Then use the convert button. 
    2. Upload your wav audio file to begin your speech2text analyses
    3. If your file does not upload, make sure it's a mono-channel file, i.e having only one audio source.
    4. If your file isn't wav formated, do not worry, [click here](https://www.movavi.com/support/how-to/how-to-convert-music-to-wav.html) 
       and head over to "Online Converter" to upload your mp3 file.
    5. if you are getting "Sorry...Run Again" message when you upload file, try running again when you have a stable
       network 
    
    """)

     # preview app demo
    demo = st.sidebar.checkbox('App Demo')
    if demo == 1:
       st.sidebar.video('https://res.cloudinary.com/dfgg73dvr/video/upload/v1624127072/ezgif.com-gif-maker_k56lry.mp4', format='mp4')

    st.sidebar.header("")

    st.sidebar.markdown(
    """
    -----------
    # Let's connect
    
    [![Jude Leonard Ndu](https://img.shields.io/badge/Author-@JudeLeonard-gray.svg?colorA=gray&colorB=dodgergreen&logo=github)](https://www.github.com/judeleonard/)
    
    [![Jude Ndu](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logoColor=white)](https://www.linkedin.com/in/jude-ndu-78ab38175/)
    
    [![Jude Leonard](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=gray)](https://www.twitter.judeleonard13/)
    """)

     #----- deleting files from directories so we don't overload the app------
    def remove_wav_files(n):
        wav_files = glob.glob("temp2/*wav")
        if len(wav_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in wav_files:
                if os.stat(f).st_mtime < now - n_days:
                   os.remove(f)
                   print("Deleted", f)

    def remove_mp3_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                   os.remove(f)
                   print("Deleted", f)


    remove_mp3_files(7)   # remove mp3 files from directory

    remove_wav_files(7)   # remove wav files from directory




if __name__ == '__main__':
    main()