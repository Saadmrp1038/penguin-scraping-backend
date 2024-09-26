from fastapi import APIRouter, HTTPException
from app.core.scrapy_utils import run_scrapy_spider
import os
import json
import logging
router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.schemas.weburlscrape import webUrlTrain
from app.helpers.qdrant_functions import create_semantic_chunks, upload_to_qdrant, generate_summary_empty

@router.post("/scrape/")
async def scrape(url_item: webUrlTrain):
    try:
        logger.info(f"Received payload: {url_item}")
        output_file = run_scrapy_spider(url_item.url)
        if not os.path.exists(output_file):
            raise FileNotFoundError(f"Output file not found: {output_file}")
        
        with open(output_file, 'r') as f:
            data = json.load(f)
        os.remove(output_file)
        
        if len(data) == 0:
            raise ValueError("No data found in the scraped content")
        
        semantic_chunks = create_semantic_chunks(data[0]['content'])
        logger.info("Semantic chunking done")
        summaries = generate_summary_empty(semantic_chunks)
        logger.info("Summary generation done")
        
        upload_result = upload_to_qdrant(url_item, semantic_chunks, summaries, "admin_trainer")
        logger.info(f"Qdrant Upload done. Result: {upload_result}")
        
        return {"detail": f'Training job with ID {url_item.id} added to vector DB successfully', "upload_result": upload_result}
    except FileNotFoundError as e:
        logger.error(f"File not found error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File not found: {str(e)}")
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException as e:
        # Re-raise HTTP exceptions from upload_to_qdrant
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in scrape function: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
