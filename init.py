from datetime import datetime, timedelta

PROMPT_PATH = ".\\assets\\prompts\\"
def load_prompt(name):
        with open(PROMPT_PATH + name, 'r', encoding='utf-8') as f:
            return f.read()
        
AKVA_MAY_USE_THIS        = load_prompt("akva_may_use_this.txt")
CHARACTER_PROMPT         = load_prompt("character_prompt.txt")
IMAGE_RESPONSE_PROMPT    = load_prompt("image_response_prompt.txt")
LORA_PROMPT              = load_prompt("lora_prompt.txt")
MODULE_CLASSIFIER_PROMPT = load_prompt("module_classifier_prompt.txt")
NEGATIVE_SD_PROMPT       = load_prompt("negative_sd_prompt.txt")
SELFIE_RESPONSE_PROMPT   = load_prompt("selfie_response_prompt.txt")
STABLE_DIFFUSION_PROMPT  = load_prompt("stable_diffusion_prompt.txt")
TEXT_RESPONSE_PROMPT     = load_prompt("text_response_prompt.txt")



    
DATE = datetime.now().strftime('%d %B %Y')
TIME = datetime.now().strftime('%H:%M:%S')
DAY = datetime.now().strftime("%A")
CURRENT_DATE = datetime.now()
NEXT_WEEK_DAY = CURRENT_DATE + timedelta(days=(7 - CURRENT_DATE.weekday()) % 7)
NEXT_WEEK_DATE = NEXT_WEEK_DAY.strftime("%d %B %Y")

EXAMPLE_DIALOG = ["User: Well, what are you doing at the moment?",
                  "Akva: I'm drawing a picture of you",  ]

