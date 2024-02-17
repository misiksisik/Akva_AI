from config.secrets import TELEGRAM_TOKEN, CALENDAR_CREDETIAL_PATH
LLAMA_CHAT_MODEL_PATH = "F:\Dev\Llama_model\llama-2-13b-chat.Q4_K_M.gguf"
RESPONSE_FOOTER = "\n\nUSER: {message}\nAkva:"
HYPERDB_MEMORY_PATH = ".\memories\Akva.pickle.gz"
SHORT_TERM_HISTORY_PATH = ".\memories\short_term_history.txt"
SD_CONFIG = {
    "model_id": "stabilityai/stable-diffusion-xl-base-1.0",
    "device" : "cuda",
    "num_inference_steps": 20,
    "guidance_scale": 7.5,

        }
SD_IMAGE_CONFIG = {
    "width": 512,
    "height" : 512,
    "image_name" : "image",
    "image_extension" : "png",
    "path" : ".\\images\\",
    "max_images" : 100
                    }



