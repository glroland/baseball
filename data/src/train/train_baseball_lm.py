""" CLI Utility for training a baseball small language model."""
import sys
import logging
from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported
#from unsloth.chat_templates import get_chat_template
#from transformers import TextStreamer
#from transformers import TextStreamer

logger = logging.getLogger(__name__)

LOG_FILENAME = "train_baseball_lm.log"
TRAIN_MAX_SEQ_LENGTH = 2048 # Choose any! We auto support RoPE Scaling internally!
TRAIN_DTYPE = None # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+
TRAIN_LOAD_IN_4BIT = True # Use 4bit quantization to reduce memory usage. Can be False.
TRAIN_FOUNDATIONAL_MODEL = "unsloth/Phi-3.5-mini-instruct"
OUTPUT_DIR = "../"
TRAINING_DATA = OUTPUT_DIR + "augmentoolkit/original/output/plain_qa_list.jsonl"
MODEL_DIR = OUTPUT_DIR + "lora_model"

class ColorOutputFormatter(logging.Formatter):
    """ Add colors to stdout logging output to simplify text.  Thank you to:
        https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    """

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = '%(name)-13s: %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: grey + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def main():
    """ Entry point for CLI
    """
    # Default to not set
    logging.getLogger().setLevel(logging.NOTSET)

    # Log info and higher to the console
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(ColorOutputFormatter())
    logging.getLogger().addHandler(console)

    # Log debug and higher to a file
    file_handler = logging.FileHandler(LOG_FILENAME, 'w+')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = TRAIN_FOUNDATIONAL_MODEL,
        max_seq_length = TRAIN_MAX_SEQ_LENGTH,
        dtype = TRAIN_DTYPE,
        load_in_4bit = TRAIN_LOAD_IN_4BIT,
        # token = "hf_...", # use one if using gated models like meta-llama/Llama-2-7b-hf
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r = 16, # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj",],
        lora_alpha = 16,
        lora_dropout = 0, # Supports any, but = 0 is optimized
        bias = "none",    # Supports any, but = "none" is optimized
        # [NEW] "unsloth" uses 30% less VRAM, fits 2x larger batch sizes!
        use_gradient_checkpointing = "unsloth", # True or "unsloth" for very long context
        random_state = 3407,
        use_rslora = False,  # We support rank stabilized LoRA
        loftq_config = None, # And LoftQ
    )

    tokenizer = get_chat_template(
        tokenizer,
        chat_template = "phi-3", # Supports zephyr, chatml, mistral, llama, alpaca, vicuna, vicuna_old, unsloth
        mapping = {"role" : "from", "content" : "value", "user" : "human", "assistant" : "gpt"}, # ShareGPT style
    )

    def formatting_prompts_func(examples):
        convos = examples["conversations"]
        texts = [tokenizer.apply_chat_template(convo, tokenize = False, add_generation_prompt = False) for convo in convos]
        return { "text" : texts, }

    dataset = load_dataset("json", data_files=TRAINING_DATA, split = "train")
    dataset = dataset.map(formatting_prompts_func, batched = True,)

    unsloth_template = \
        "{{ bos_token }}"\
        "{{ 'You are a helpful assistant to the user\n' }}"\
        "{% for message in messages %}"\
            "{% if message['role'] == 'user' %}"\
                "{{ '>>> User: ' + message['content'] + '\n' }}"\
            "{% elif message['role'] == 'assistant' %}"\
                "{{ '>>> Assistant: ' + message['content'] + eos_token + '\n' }}"\
            "{% endif %}"\
        "{% endfor %}"\
        "{% if add_generation_prompt %}"\
            "{{ '>>> Assistant: ' }}"\
        "{% endif %}"
    unsloth_eos_token = "eos_token"

#    if False:
#        tokenizer = get_chat_template(
#            tokenizer,
#            chat_template = (unsloth_template, unsloth_eos_token,), # You must provide a template and EOS token
#            mapping = {"role" : "from", "content" : "value", "user" : "human", "assistant" : "gpt"}, # ShareGPT style
#            map_eos_token = True, # Maps <|im_end|> to </s> instead
#        )

    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = TRAIN_MAX_SEQ_LENGTH,
        dataset_num_proc = 2,
        packing = False, # Can make training 5x faster for short sequences.
        args = TrainingArguments(
            per_device_train_batch_size = 2,
            gradient_accumulation_steps = 4,
            warmup_steps = 5,
            max_steps = 60,
            learning_rate = 2e-4,
            fp16 = not is_bfloat16_supported(),
            bf16 = is_bfloat16_supported(),
            logging_steps = 1,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = "outputs",
            report_to = "none", # Use this for WandB etc
        ),
    )

    #@title Show current memory stats
    gpu_stats = torch.cuda.get_device_properties(0)
    start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
    max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
    print(f"GPU = {gpu_stats.name}. Max memory = {max_memory} GB.")
    print(f"{start_gpu_memory} GB of memory reserved.")

    trainer_stats = trainer.train()

    #@title Show final memory and time stats
    used_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
    used_memory_for_lora = round(used_memory - start_gpu_memory, 3)
    used_percentage = round(used_memory         /max_memory*100, 3)
    lora_percentage = round(used_memory_for_lora/max_memory*100, 3)
    print(f"{trainer_stats.metrics['train_runtime']} seconds used for training.")
    print(f"{round(trainer_stats.metrics['train_runtime']/60, 2)} minutes used for training.")
    print(f"Peak reserved memory = {used_memory} GB.")
    print(f"Peak reserved memory for training = {used_memory_for_lora} GB.")
    print(f"Peak reserved memory % of max memory = {used_percentage} %.")
    print(f"Peak reserved memory for training % of max memory = {lora_percentage} %.")

#    tokenizer = get_chat_template(
#        tokenizer,
#        chat_template = "phi-3", # Supports zephyr, chatml, mistral, llama, alpaca, vicuna, vicuna_old, unsloth
#        mapping = {"role" : "from", "content" : "value", "user" : "human", "assistant" : "gpt"}, # ShareGPT style
#    )

#    FastLanguageModel.for_inference(model) # Enable native 2x faster inference

#    messages = [
#        {"from": "human", "value": "Continue the fibonnaci sequence: 1, 1, 2, 3, 5, 8,"},
#    ]
#    inputs = tokenizer.apply_chat_template(
#        messages,
#        tokenize = True,
#        add_generation_prompt = True, # Must add for generation
#        return_tensors = "pt",
#    ).to("cuda")

#    outputs = model.generate(input_ids = inputs, max_new_tokens = 64, use_cache = True)
#    tokenizer.batch_decode(outputs)

#    FastLanguageModel.for_inference(model) # Enable native 2x faster inference

#    messages = [
#        {"from": "human", "value": "Continue the fibonnaci sequence: 1, 1, 2, 3, 5, 8,"},
#    ]
#    inputs = tokenizer.apply_chat_template(
#        messages,
#        tokenize = True,
#        add_generation_prompt = True, # Must add for generation
#        return_tensors = "pt",
#    ).to("cuda")

#    text_streamer = TextStreamer(tokenizer, skip_prompt = True)
#    _ = model.generate(input_ids = inputs, streamer = text_streamer, max_new_tokens = 128, use_cache = True)

    model.save_pretrained(MODEL_DIR) # Local saving
    tokenizer.save_pretrained(MODEL_DIR)
#    # model.push_to_hub("your_name/lora_model", token = "...") # Online saving
#    # tokenizer.push_to_hub("your_name/lora_model", token = "...") # Online saving

#    if False:
#        from unsloth import FastLanguageModel
#        model, tokenizer = FastLanguageModel.from_pretrained(
#            model_name = "lora_model", # YOUR MODEL YOU USED FOR TRAINING
#            max_seq_length = max_seq_length,
#            dtype = dtype,
#            load_in_4bit = load_in_4bit,
#        )
#        FastLanguageModel.for_inference(model) # Enable native 2x faster inference

#        messages = [
#            {"from": "human", "value": "What is a famous tall tower in Paris?"},
#        ]
#        inputs = tokenizer.apply_chat_template(
#            messages,
#            tokenize = True,
#            add_generation_prompt = True, # Must add for generation
#            return_tensors = "pt",
#        ).to("cuda")

#        text_streamer = TextStreamer(tokenizer, skip_prompt = True)
#        _ = model.generate(input_ids = inputs, streamer = text_streamer, max_new_tokens = 128, use_cache = True)

#    if False:
#        # I highly do NOT suggest - use Unsloth if possible
#        from peft import AutoPeftModelForCausalLM
#        from transformers import AutoTokenizer
#        model = AutoPeftModelForCausalLM.from_pretrained(
#            "lora_model", # YOUR MODEL YOU USED FOR TRAINING
#            load_in_4bit = load_in_4bit,
#        )
#        tokenizer = AutoTokenizer.from_pretrained("lora_model")

#    # Merge to 16bit
#    if False: model.save_pretrained_merged("model", tokenizer, save_method = "merged_16bit",)
#    if False: model.push_to_hub_merged("hf/model", tokenizer, save_method = "merged_16bit", token = "")

#    # Merge to 4bit
#    if False: model.save_pretrained_merged("model", tokenizer, save_method = "merged_4bit",)
#    if False: model.push_to_hub_merged("hf/model", tokenizer, save_method = "merged_4bit", token = "")

#    # Just LoRA adapters
#    if False: model.save_pretrained_merged("model", tokenizer, save_method = "lora",)
#    if False: model.push_to_hub_merged("hf/model", tokenizer, save_method = "lora", token = "")

#    # Save to 8bit Q8_0
#    if False: model.save_pretrained_gguf("model", tokenizer,)
#    # Remember to go to https://huggingface.co/settings/tokens for a token!
#    # And change hf to your username!
#    if False: model.push_to_hub_gguf("hf/model", tokenizer, token = "")

#    # Save to 16bit GGUF
#    if False: model.save_pretrained_gguf("model", tokenizer, quantization_method = "f16")
#    if False: model.push_to_hub_gguf("hf/model", tokenizer, quantization_method = "f16", token = "")

#    # Save to q4_k_m GGUF
#CRASHINGWSL    model.save_pretrained_gguf("model", tokenizer, quantization_method = "q4_k_m")
#    if False: model.push_to_hub_gguf("hf/model", tokenizer, quantization_method = "q4_k_m", token = "")

#    # Save to multiple GGUF options - much faster if you want multiple!
#    if False:
#        model.push_to_hub_gguf(
#            "hf/model", # Change hf to your username!
#            tokenizer,
#            quantization_method = ["q4_k_m", "q8_0", "q5_k_m",],
#            token = "", # Get a token at https://huggingface.co/settings/tokens
#        )


if __name__ == '__main__':
    main()
