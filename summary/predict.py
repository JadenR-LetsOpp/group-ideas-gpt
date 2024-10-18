import pandas as pd
import logging
from .config import Config
import openai
import tiktoken
from .db import insert_or_update_progress

client = openai.Client(api_key=Config.OPENAI)

def generate_prompt(ideas, question, batch_num, total_batches):
    """Generate the clustering prompt for a batch of ideas."""
    return f"""
    Dit is batch {batch_num} van {total_batches}. Je krijgt een dataset met ID's en ideeën gebaseerd op de vraag: {question}. Hier zijn de ideeën: {' '.join(ideas)}.
    """

def cluster_ideas(ideas, apq_id, version, question):
    prompt = generate_prompt(ideas, question, 1, 1)
        
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": """
             Je bent een behulpzame assistent die de ideeën in unieke clusters moet groeperen. Dit zal je doen aan de hand van de volgende opdracht, zorg dat je je aan elke regel strict houdt.
             
                 **Opdracht:**
                1.	Groepeer ideeën in 3-7 clusters (inclusief 'Overig') op basis van thema's.
                2.	Geef elke cluster een korte, beschrijvende naam (max. 4 woorden, 40 karakters) in het Nederlands, met alleen de eerste letter van de titel in hoofdletter tenzij anders nodig.
                3.	Elk cluster moet minstens 3 ideeën bevatten.
                4.	Zet lege ideeën en ideeën zonder zinnige inhoud in het 'Overig' cluster, hier mogen alleen nutteloze ideeen in.
                5.	Gebruik de ID's om ideeën te groeperen, niet de inhoud van de ideeën.
                6.	Geef de output in het volgende format: Cluster X: <Clustertitel> - <ID1>, <ID2>, <ID3>
                7.	Minimaliseer het aantal clusters, maar zorg dat elk idee goed er bij past.
                8.	Gebruik interpretatie en gezond verstand bij vage ideeën.
                9.	Elke cluster moet uniek zijn en duidelijk verschillen van andere clusters.
                10.	Alleen nieuwe clusters toevoegen als het echt niet anders kan.
             """},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000,
        top_p=0.6,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    return response.choices[0].message.content
    

def gpt(df_ideas, apq_id, version, question):
    ideas = df_ideas['idea'].to_numpy()
    ids = df_ideas['id'].to_numpy()

    # Combine each idea with its corresponding ID
    numbered_ideas = [f"{id}. {idea}" for id, idea in zip(ids, ideas)]
    openai.api_key = Config.OPENAI

    # Cluster the ideas
    clusters = cluster_ideas(numbered_ideas, apq_id, version, question)

    return clusters

def createDataframe(text):
    logging.info(f"Text: {text}")
    try:
        # Split the text into separate clusters
        clusters = text.split('Cluster ')

        # Initializing an empty dataframe
        df_combined = pd.DataFrame(columns=['Match', 'Number'])

        # Skip the first split as it will be empty
        for cluster in clusters[1:]:
            try:
                # Split the cluster text into description and numbers
                parts = cluster.split(': ')
                description = parts[1].split(' - ')[0].strip()
                number_list = parts[1].split(' - ')[1].split(', ')

                for num_str in number_list:
                    try:
                        num = int(num_str.strip())
                        df_combined.loc[len(df_combined.index)] = [description, num]
                    except ValueError:
                        logging.error(f"Error converting '{num_str}' to integer.")
            except Exception as e:
                logging.error(f"Error processing cluster: {e}")

        return df_combined
    except Exception as e:
        logging.error(f"An error occurred in createDataframe: {e}")
        return pd.DataFrame(columns=['Match', 'Number']) 
        

def createTopic(df_ideas, apq_id, version, question):
    # Get the response from OpenAI as a string
    clusters_text = gpt(df_ideas, apq_id, version, question)
    
    # Convert the string response into a DataFrame
    df_clusters = createDataframe(clusters_text)

    # Group the DataFrame by 'Match' and aggregate the 'Number' column
    grouped_df = df_clusters.groupby('Match')['Number'].apply(lambda x: ', '.join(x.astype(str))).reset_index()

    return grouped_df