import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification
from typing import List, Dict, Tuple, Optional
import numpy as np
from pathlib import Path

from .config import settings
from .models import Intent, Language

class BERTNLPModel:
    """BERT-style NLP model for intent classification and NER"""
    
    def __init__(self, model_dir: str = None):
        self.model_dir = Path(model_dir or settings.model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load or initialize models
        self.tokenizer = None
        self.intent_model = None
        self.ner_model = None
        self.load_models()
    
    def load_models(self):
        """Modellarni yuklash yoki yaratish"""
        try:
            # Load pretrained tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.bert_model_name,
                cache_dir=self.model_dir / "cache"
            )
            
            # Load intent classification model
            intent_path = self.model_dir / settings.intent_model_path
            if intent_path.exists():
                self.intent_model = AutoModelForSequenceClassification.from_pretrained(
                    str(intent_path)
                ).to(self.device)
            else:
                # Create new model
                self.intent_model = AutoModelForSequenceClassification.from_pretrained(
                    settings.bert_model_name,
                    num_labels=len(settings.intents)
                ).to(self.device)
            
            # Load NER model
            ner_path = self.model_dir / settings.ner_model_path
            if ner_path.exists():
                self.ner_model = AutoModelForTokenClassification.from_pretrained(
                    str(ner_path)
                ).to(self.device)
            else:
                # Create new model
                self.ner_model = AutoModelForTokenClassification.from_pretrained(
                    settings.bert_model_name,
                    num_labels=len(settings.slot_types)
                ).to(self.device)
            
            # Set models to evaluation mode
            self.intent_model.eval()
            self.ner_model.eval()
            
        except Exception as e:
            raise Exception(f"Failed to load models: {e}")
    
    def predict_intent(self, text: str) -> Tuple[Intent, float]:
        """
        Intentni aniqlash
        
        Args:
            text: Kiruvchi matn
            
        Returns:
            Tuple: (intent, confidence)
        """
        if not self.tokenizer or not self.intent_model:
            raise Exception("Model not loaded")
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            max_length=settings.max_length,
            truncation=True,
            padding=True
        ).to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.intent_model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
        # Get highest probability
        probs = predictions.cpu().numpy()[0]
        intent_idx = np.argmax(probs)
        confidence = float(probs[intent_idx])
        
        intent_name = settings.intents[intent_idx]
        return Intent(intent_name), confidence
    
    def extract_slots(self, text: str) -> List[Dict[str, any]]:
        """
        Slotlarni ajratib olish (NER)
        
        Args:
            text: Kiruvchi matn
            
        Returns:
            List: Slotlar ro'yxati
        """
        if not self.tokenizer or not self.ner_model:
            raise Exception("Model not loaded")
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            max_length=settings.max_length,
            truncation=True,
            padding=True,
            return_offsets_mapping=True
        ).to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.ner_model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)
        
        # Convert to human readable format
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        offsets = inputs["offset_mapping"][0].cpu().numpy()
        predictions = predictions[0].cpu().numpy()
        
        slots = []
        current_slot = None
        
        for i, (token, offset, pred) in enumerate(zip(tokens, offsets, predictions)):
            # Skip special tokens
            if token in [self.tokenizer.cls_token, self.tokenizer.sep_token, self.tokenizer.pad_token]:
                continue
            
            slot_type = settings.slot_types[pred]
            
            # Check if we have a slot
            if slot_type.startswith('B-'):
                # Start new slot
                if current_slot:
                    slots.append(current_slot)
                
                slot_name = slot_type[2:]
                current_slot = {
                    'type': slot_name,
                    'value': token,
                    'start': int(offset[0]),
                    'end': int(offset[1]),
                    'confidence': 0.8  # Placeholder
                }
            elif slot_type.startswith('I-') and current_slot:
                # Continue current slot
                slot_name = slot_type[2:]
                if slot_name == current_slot['type']:
                    current_slot['value'] += ' ' + token
                    current_slot['end'] = int(offset[1])
            else:
                # Outside or slot changed
                if current_slot:
                    slots.append(current_slot)
                    current_slot = None
        
        # Add last slot if exists
        if current_slot:
            slots.append(current_slot)
        
        # Clean up slot values
        for slot in slots:
            slot['value'] = slot['value'].replace(' ##', '')
        
        return slots
    
    def save_models(self):
        """Modellarni saqlash"""
        if self.intent_model:
            intent_path = self.model_dir / settings.intent_model_path
            self.intent_model.save_pretrained(str(intent_path))
        
        if self.ner_model:
            ner_path = self.model_dir / settings.ner_model_path
            self.ner_model.save_pretrained(str(ner_path))
        
        if self.tokenizer:
            self.tokenizer.save_pretrained(str(self.model_dir / "tokenizer"))