
import random
import os
from transformers import pipeline

emotion_classifier = pipeline(model="SamLowe/roberta-base-go_emotions")

def get_bot_emotion(generated_response):
    try:

        bot_emotion = emotion_classifier(generated_response) 
        max_label = bot_emotion[0]['label'].strip().lower() 
        
        print(max_label)
        print(f"Max Label: {max_label}")

        stickers_folder = ".\\assets\\stickers\\"
        sticker_files = os.listdir(stickers_folder)
        print("Sticker Files:", sticker_files)


        matching_stickers = [os.path.join(stickers_folder, sticker) for sticker in sticker_files if max_label in sticker.lower()]

        if matching_stickers:
            # Choose a random sticker from the matching stickers
            sticker_path = random.choice(matching_stickers)
        else:
            sticker_path = None

        return sticker_path

    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    sticker_path = get_bot_emotion("I am so angry")
    if sticker_path:
        print(f"Sticker Path: {sticker_path}")
    else:
        print("No matching sticker found.")
