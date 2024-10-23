from .config import Config
import openai

client = openai.Client(api_key=Config.OPENAI)

def generate_prompt(ideas, question):
    return f"Je krijgt een dataset ideeën gebaseerd op de vraag: {question}. Hier zijn de ideeën: {' '.join(ideas)}."

def summarize_ideas(ideas, apq_id, question):
    prompt = generate_prompt(ideas, question)
        
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": """
             Je bent een behulpzame assistent die de ideeën samenvat op een overzichtelijke manier. Dit zal je doen aan de hand van de volgende opdracht, zorg dat je je aan elke regel strict houdt.
             
                 **Opdracht:**
                1. De samenvatting mag niet langer zijn dan 5 regels of 200 woorden. Het moet kort en bondig zijn. 
                2. Gebruik de ideeën die je hebt gekregen om de samenvatting te maken.
                3. Als ideeën zwaar verschillen van elkaar, geef dan aan dat er verschillende perspectieven zijn.
                4. Maak duidelijk wat de belangrijkste punten zijn.
                5. Maak van de verschillende perspectieven duidelijk hoeveel procent van de ideeën dit perspectief heeft.
             """},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500,
        top_p=0.6,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    return response.choices[0].message.content
    

def get_summary(df_ideas, apq_id, question):
    ideas = df_ideas['idea'].to_numpy()

    # Combine each idea with its corresponding ID
    openai.api_key = Config.OPENAI

    return summarize_ideas(ideas, apq_id, question)
