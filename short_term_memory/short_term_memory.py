from transformers import LlamaForCausalLM, LlamaTokenizer
import os



TOKENIZER = LlamaTokenizer.from_pretrained(".\\short_term_memory\\tokenizer.model")


class short_term_memory:
    def __init__(self, max_tokens, history_path):
        self.memory = []
        self.max_tokens = max_tokens
        self.history_path = history_path
        self.load_memory()
    def __str__(self):
        return "\n".join(self.memory)
    
    def add_memory(self, new_memory):
        #pro debug
        #print(f"\n{self.memory}")
        if not "<START TRANSCRIPT>" in self.memory:
            self.memory.append('<START TRANSCRIPT>')
        self.memory.append(new_memory)  # Append the new message to the memory list
        self.save_memory()  # Save the updated memory to the file
        self.forget()  # Check and remove old messages if necessary
    
    def save_memory(self):
        with open(self.history_path, 'w', encoding='utf-8') as f:
            for message in self.memory:
                f.write(message + '\n')
                
    def forget(self, tokenizer=TOKENIZER):
        current_tokens_len = len(tokenizer.tokenize("\n".join(self.memory)))
        #print(f"\ncurrent_tokens_len: {current_tokens_len}")
        while current_tokens_len > self.max_tokens:
            prompt_lines = "\n".join(self.memory).split('\n')
            oldest_msg_index = len(prompt_lines) - prompt_lines[::-1].index('<START TRANSCRIPT>')
            prompt_lines.pop(oldest_msg_index)
            self.memory = prompt_lines
            current_tokens_len = len(tokenizer.tokenize("\n".join(self.memory)))
    
    def load_memory(self):
        if not os.path.exists(self.history_path):
            return
        with open(self.history_path, 'r', encoding='utf-8') as f:
            history_lines = f.readlines()
            history_lines = [line.strip() for line in history_lines]
            self.memory.extend(history_lines)
        self.forget()
    def clear_memory(self):
        self.memory = []









