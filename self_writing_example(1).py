import time
import random

words = ["hello", "world", "self", "writing", "process", "continues"]

def self_writing_process():
    while True:
        sentence = " ".join(random.choices(words, k=5))
        print(f"Generated: {sentence}")
        time.sleep(1)  # Pause for 1 second before generating the next line

self_writing_process()