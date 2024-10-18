import pandas as pd
import spacy
import re

nlp = spacy.load('nl_core_news_lg-3.6.0')

def anonymize_text_data(df, text_column):
   
    patterns = {
        # Exclude names that are the first word of a sentence or follow certain punctuations
        'naam': r'(?<!^)(?<!\. |\? |\! )\b([A-Z][a-z]+ [A-Z][a-z]+)\b',
        # Organization pattern, excluding those at the start of a sentence or after certain punctuations
        'organisatie': r'(?<!^)(?<!\. |\? |\! )\b([A-Z][a-z]+(?: [A-Z][a-z]+)+|[A-Z]{2,})\b',
        # Jaartallen
        'jaartal': r'\b(\d{4})\b',
        # Dutch street names pattern, including various suffixes such as laan, plantsoen, weg, plein, hof
        'straat': r'\b([A-Z][a-z]+(?:straat|laan|plantsoen|weg|plein|hof) \d+)\b',
        # Pattern for international phone numbers
        'telefoon nummer': r'\b(\(?\+?[0-9]{1,4}\)?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}(?:[-.\s]?\d{1,4})?)\b',
        # Pattern for websites including .be, .nl, and .de
        'website': r'\b(\S+\.(?:com|org|net|edu|gov|be|nl|de)|https?://\S+)\b'
    }

    def anonymize_text(text):
        text = text.strip()
        if (len(text) < 4):
          return 'Niet labelbaar'
      
        start_text = text
        # Replace line beginnings with a placeholder to avoid matching names and organizations at the start
        text = re.sub(r'^', 'LINE_START ', text)
        for key, pattern in patterns.items():
            placeholder = f"<{key}>"
            text = re.sub(pattern, placeholder, text)
        # Remove the placeholder after processing
        text = text.replace('LINE_START ', '')

        doc = nlp(text)
        # Iterate over the entities
       
        for ent in doc.ents:
            # Replace entities of type 'PER' or 'ORG' with a placeholder
            if ent.label_ in ['', '', '', '', '']:
                text = text.replace(ent.text, f"<{ent.label_}>")
        return text

    # Apply the anonymization function to the text column
    df[text_column] = df[text_column].apply(anonymize_text)

    return df