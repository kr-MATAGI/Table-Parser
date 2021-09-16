### Hugging Face - transformer
from transformers import AutoTokenizer, AutoModelForMaskedLM

# Tokenizer
tokenizer = AutoTokenizer.from_pretrained("klue/roberta-base")