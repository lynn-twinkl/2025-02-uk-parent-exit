import langid 
import openai
from typing import Optional
import streamlit as st

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

## -- DETECT LANGUAGE

def detect_language(text):
    try:
        lang, _ = langid.classify(text)
        return 'en' if lang == 'en' else 'non-en'
    except:
        return "unknown"

## -- TRANSLATE TEXT


# Example: Reuse your existing OpenAIWrapper for robust retry logic.
# from my_wrappers import OpenAIWrapper  # Hypothetical import if your wrapper is in a separate module.

def translate_text(
    text: str,
    skip_translation: bool = False,
    translator_model: Optional["OpenAIWrapper"] = None
) -> str:
    """
    Translate the provided text into English using the specified translator model. 
    If 'skip_translation' is True, it returns the original text without translation.
    
    If the text is already in English or gibberish, 
    the output should mirror the original text as per the system prompt instructions.
    
    Parameters:
        text (str): The text to translate.
        skip_translation (bool): Whether to skip translation entirely. Defaults to False.
        translator_model (OpenAIWrapper, optional): An instance of your OpenAIWrapper class 
            for robust, retriable OpenAI calls. If None, no translation is performed.
    
    Returns:
        str: The translated text (or original text if skip_translation is True).
    """
    # If skip translation is set or there's no translator provided, just return the original text.
    if skip_translation or translator_model is None:
        return text
    
    # Prepare a system prompt and user prompt. 
    # For instance, you could store this in translator_model or pass it here.
    system_prompt = (
        "You are an expert multilingual translator working at a subscription-based EDU publishing company."
    )
    user_prompt_template = """
Below you will find a survey response from our Exit Survey that is not in English.
Your goal is to read it carefully to identify the original language, 
and then translate it into English being as true to the original intent as possible.

## RULES:
1. Your output should ONLY contain the translated text. 
   Do NOT include any additional text, information, or explanations.
2. Do NOT wrap your answer in quotation marks.
3. If the text seems to be in English or you can't identify the language, or the text appears 
   to be gibberish, simply return the same exact text you received.

## TEXT FOR TRANSLATION:
{text}
"""

    user_prompt = user_prompt_template.format(text=text)
    
    # translator_model might already have a "system" prompt built in,
    # or we can combine them here. For example:
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    # Use the run() method with robust retry logic.
    # (Adjust depending on how your wrapper is structured)
    translated_text = translator_model.run(full_prompt)
    
    return translated_text

