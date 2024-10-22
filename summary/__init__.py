import azure.functions as func
import logging
from .db import get_ideas, insert_in_db
from .predict import get_summary
from .anonymize_data import anonymize_text_data

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    apq_id = req.params.get('apq_id')

    if apq_id:
        df_ideas,question = get_ideas(apq_id)
        
        df_ideas_anonymized = anonymize_text_data(df_ideas, 'idea')
        summary = get_summary(df_ideas_anonymized, apq_id,question)
        
        if not summary:
            #101 is the code for None
            return func.HttpResponse(f"None",status_code=200)
        

        else:
            #100 is the code for Done
            insert_in_db(summary, apq_id)    
            return func.HttpResponse(f"Done",status_code=200)
      
    else:
        return func.HttpResponse(
             "No version or apq_id found",
             status_code=200
        )