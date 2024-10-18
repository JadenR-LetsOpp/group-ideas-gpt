import azure.functions as func
import logging
from .db import get_ideas,group_in_db, insert_or_update_progress,delete_group_ideas
from .predict import createTopic
from .anonymize_data import anonymize_text_data

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    version = req.params.get('version')
    apq_id = req.params.get('apq_id')
    
    if not version:
        try:
            req_body = req.get_json()   
        except ValueError:
            pass
        else:
            version = req_body.get('version')
            apq_id = req_body.get('apq_id')

    if version and apq_id:
        logging.info(f"Version: {version}")
        logging.info(f"Apq_id: {apq_id}")
        insert_or_update_progress(apq_id,version,1)
        df_ideas,question = get_ideas(apq_id)
        
        df_ideas_anonymized = anonymize_text_data(df_ideas, 'idea')
        groupIdeaTitledf=createTopic(df_ideas_anonymized, apq_id,version,question)
        logging.info(f"question: {question}")

        logging.info(f"GroupIdeaTitledf: {groupIdeaTitledf}")
        
        if groupIdeaTitledf.empty:
            #101 is the code for None
            insert_or_update_progress(apq_id,version,'101')
            return func.HttpResponse(f"None",status_code=200)
        

        else:
            #100 is the code for Done
            insert_or_update_progress(apq_id,version,'100')
            delete_group_ideas(apq_id, version)
            group_in_db(groupIdeaTitledf,apq_id,version)    
            return func.HttpResponse(f"Done",status_code=200)
      
    else:
        return func.HttpResponse(
             "No version or apq_id found",
             status_code=200
        )