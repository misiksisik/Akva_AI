#telegram knihovny
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes
import asyncio
#llm model knihovna
from llama_cpp import Llama
import os
#hyperDb
from hyperdb.hyperdb import *
#stickers
from emotion_ai.sticker_bot import get_bot_emotion
#bark (TTS)
from voice.tts import tts
#Short_term_memory
from short_term_memory.short_term_memory import *
#config
from config.config import *
#modules
from modules.my_calendar import get_calendar_events
from init import *


from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler, DiffusionPipeline
from io import BytesIO
from compel import Compel, ReturnedEmbeddingsType


import torch

def generate_prompt_header(short_memory, message, prompt=CHARACTER_PROMPT):
    #short_term
    memory_content = "\n".join(short_memory.memory)
    memory_content = str(short_memory)
    memory_content = memory_content.replace("<START TRANSCRIPT>", "")

    #hyperdb
    similar_documents = hyperdb_memory.query(message, top_k=2)
    prompt += f"\nPast conversations:\n"    
    if similar_documents:
        responses = [response for response, _ in similar_documents]
        for response in responses:
            prompt += f"- {response}\n"
    prompt += ("\nCurrent conversation:\n"
                f"{memory_content}\n")
    return prompt

def create_completion(prompt):
    return llm.create_completion(prompt, suffix=None, max_tokens=258, temperature=0.85, top_p=0.1,
                        logprobs=None, echo=False, stop=["USER:"], frequency_penalty=0.0,
                        presence_penalty=0.0, repeat_penalty=1.1, top_k=40, stream=False, tfs_z=1.0,
                        mirostat_mode=0, mirostat_tau=5.0, mirostat_eta=0.1, model=None,
                        stopping_criteria=None, logits_processor=None)

def add_response_to_memory(message, short_memory, response):
    short_memory.forget()
    hyperdb_memory.add_documents([{"USER:": message}])
    hyperdb_memory.add_documents([{"Akva:": response}])
    hyperdb_memory.save(HYPERDB_MEMORY_PATH)

def fix_response(response):
    response = response['choices'][0]['text'].split('(END)')[0].strip()
    response = response.replace("Please note that Akva's responses are based on her personality and may not always be direct answers to the user's questions.", "")
    response = response.replace("Please keep in mind that Akva's responses are based on her personality and may not always be direct answers to the user's questions.", "")
    response = response.replace("Please respond as Akva.", "")
    response = response.replace("Please respond with the next message as Akva.", "")
    response = response.replace("Please respond with the next message as USER.", "")
    response = response.replace("Please respond with your next message.", "")
    return response

def generate_image_response(message, short_memory, image_prompt):
    prompt = CHARACTER_PROMPT
    prompt += AKVA_MAY_USE_THIS
    prompt += generate_prompt_header(short_memory, message, prompt)
    prompt += image_prompt
    prompt += RESPONSE_FOOTER.format(message=message)


    print (prompt)
    response = create_completion(prompt)
    response = fix_response(response)
    
    add_response_to_memory(message, short_memory, response)
    
    return response


#generace odpovědi
def generate_response(message, short_memory, calendar, prompt=CHARACTER_PROMPT):
    prompt += AKVA_MAY_USE_THIS
    prompt +=( f" Current date: {DATE}\n"
               f" Current time: {TIME}\n"
               f" Current day: {DAY}\n"
               f" Calendar Events:\n{calendar}")
    prompt += generate_prompt_header(short_memory, message, prompt)
    prompt += TEXT_RESPONSE_PROMPT
    prompt += RESPONSE_FOOTER.format(message=message)

    print (prompt)

    response = create_completion(prompt)
    response = fix_response(response)

    add_response_to_memory(message, short_memory, response)

    return response
    


def module_classifier (message):
    messsage_and_days = f"""{message}
            Today's date: {DATE}
            Current time: {TIME}
            Today is {DAY}
            Next week starts on: {NEXT_WEEK_DATE}
            """
    prompt=MODULE_CLASSIFIER_PROMPT.replace("{formated_message_days}", messsage_and_days)
               
    print ("Here is prompt: " , prompt)
    response = create_completion(prompt)

    generated_module = response['choices'][0]['text'].split('(END)')[0].strip()
    return generated_module


def run_telebot():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    #přidaní handleru
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    application.add_handler(message_handler)
    #start telegram bota
    print('Bot is Online!')
    application.run_polling()


async def send_message_with_retry(context, update, chat_id, text, retries=3, delay=1):
    for _ in range(retries):
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
            return True  # Message sent successfully
        except Exception as e:
            print(f"Failed to send message: {e}")
            await asyncio.sleep(delay) 
    return False  

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    #Print pro debug
    #print(f'User: {message}')
    #print(f"\n {short_memory} ")
    #module classifier
    module = module_classifier(message)
    print(module)

    if (selfie :="Selfie" in module) or "Image" in module:
        generated_response = generate_image_response(message, short_memory, SELFIE_RESPONSE_PROMPT if selfie else IMAGE_RESPONSE_PROMPT)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An Image is being send...")
        
        image_io = generate_image(message, LORA_PROMPT if selfie else generated_response)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_io) 
            
        await context.bot.send_message(chat_id=update.effective_chat.id, text=generated_response)

        short_memory.add_memory(f"USER: {message}")
        short_memory.add_memory(f"Akva: {generated_response}")
        return

    #žádost o odpověd
    
    elif "Calendar" in module:
        print("Calendar")
        if "%" in module:
            print("date no specified")
            calendar = ""
        else:
            calendar = get_calendar_events(module)
            print(calendar)
    
    else:
        print("No Calendar")
        calendar = ""   
    generated_response = generate_response(message, short_memory, calendar)
    if "<END TRANSCRIPT>" in generated_response:
            generated_response = generated_response.replace("<END TRANSCRIPT>", "")
    
    #short_term_memory
    short_memory.add_memory(f"USER: {message}")
    short_memory.add_memory(f"Akva: {generated_response}")


            #TTS
                #generated_audio_path = text_to_speech_generator.generate(generated_response)




            #pro debug
    print(f"Generated Response: {generated_response}")
    if generated_response:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=generated_response)
        #await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(generated_audio_path, 'rb'))
        if sticker := get_bot_emotion(generated_response):
            await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=sticker)

    else:
        #pro debug, když generace textu nefunguje
         await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm sorry, but I couldn't generate a response.")
        
        
#SD model pro generování "selfies"
def generate_image(message, prompt):
    #výběr pipeline
    pipe = DiffusionPipeline.from_pretrained(SD_CONFIG["model_id"], torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
    pipe = pipe.to(SD_CONFIG["device"])
    
    #https://github.com/damian0815/compel ---> použití knihovny --> zmenšení mnozšství použitých tokenů
    compel = Compel(tokenizer=[pipe.tokenizer, pipe.tokenizer_2] , text_encoder=[pipe.text_encoder, pipe.text_encoder_2], returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED, requires_pooled=[False, True])
    
    #instrukce pro SD
    generated_response = message  + prompt + STABLE_DIFFUSION_PROMPT
    generated_response, pooled = compel(generated_response)
    
    #generace obrázků
    #\\ZKONTROLOVAT VELIKOST OBRÁZKU JESTLI FUNGUJE 512X512
    image = pipe(prompt_embeds = generated_response, pooled_prompt_embeds=pooled, num_inference_steps = SD_CONFIG["num_inference_steps"], negative_prompt = NEGATIVE_SD_PROMPT, guidance_scale = SD_CONFIG["guidance_scale"]).images[0]
    
    if not os.path.exists(SD_IMAGE_CONFIG["path"]):
        os.makedirs(SD_IMAGE_CONFIG["path"])
    i = 0
    while (name:=SD_IMAGE_CONFIG["image_name"] + str(i) + "." + SD_IMAGE_CONFIG["image_extension"]) in os.listdir(SD_IMAGE_CONFIG["path"]):
        i += 1
        if i > SD_IMAGE_CONFIG["max_images"]:
            print("Couldn't save image")
            return image_to_bytesio(image)
    
    image.save(SD_IMAGE_CONFIG["path"] + name, SD_IMAGE_CONFIG["image_extension"], quality=85)
    return image_to_bytesio(image)

def image_to_bytesio(image):
    image_io = BytesIO()
    image.save(image_io, format=SD_IMAGE_CONFIG["image_extension"]) 
    image_io.seek(0)
    return image_io

if __name__ == '__main__':
    #zavolání telebot funkce
    llm = Llama(model_path=LLAMA_CHAT_MODEL_PATH, verbose=False, n_gpu_layers=8000, n_threads=10, n_ctx=2048)
    short_memory = short_term_memory(max_tokens=128, history_path=SHORT_TERM_HISTORY_PATH)
    #smazání krátkodové paměti při startu
    short_memory.clear_memory()
    if os.path.exists(HYPERDB_MEMORY_PATH):
        try:
            hyperdb_memory = HyperDB()
            hyperdb_memory.load(HYPERDB_MEMORY_PATH)
            print("Database loaded successfully.")
        except Exception as e:
            #vytvoření nové databáze v případě, že existuje, ale je prázdná
            print(f"Error loading database: {e}")
            hyperdb_memory = HyperDB(EXAMPLE_DIALOG)
            print("New database created.")
 
    else:
        #vytváření nove databáze v případě, že neexistuje
        hyperdb_memory = HyperDB(EXAMPLE_DIALOG)
        print("New database created.")

    
    #tts modul
    #text_to_speech_generator = tts()
    run_telebot()