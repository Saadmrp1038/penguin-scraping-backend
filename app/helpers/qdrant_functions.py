from qdrant_client import models
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from app.schemas.weburlscrape import webUrlTrain
import logging
from app.core.qdrant import qdrantClient
from app.core.openai import openaiClient
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from fastapi import HTTPException

#################################################################################################
#   Helper function to get the chunks for any text
#   input: string, output: array of semantically similar chunks
#   used method: percentile -> default value for breakpoint = 95%
#################################################################################################
def create_semantic_chunks(text_content):
    semantic_chunker = SemanticChunker(OpenAIEmbeddings(model="text-embedding-3-large"), breakpoint_threshold_type="percentile")
    semantic_chunks = semantic_chunker.create_documents([text_content])
    return semantic_chunks

#################################################################################################
#   Helper function to get the vector embedding for any text
#   input: string, output: multidimensional array representing embedding
#################################################################################################
def create_embedding(txt):
    embedding_model = "text-embedding-3-large"
    str_embedding = openaiClient.embeddings.create(input= txt, model=embedding_model)
    return str_embedding.data[0].embedding

#################################################################################################
#   Helper function to generate the summary for a question - answer_chunk pair. The summary is then prepended
#   input: semantic chunks and the original question, output: array of strings
#################################################################################################
def generate_summary(semantic_chunks, question):  
    summaries = []  # New list to store summaries
    for semantic_chunk in semantic_chunks:   
        prompt = f"Question: {question}\nAnswer: {semantic_chunk.page_content}"
        prompt += "\nPlease provide a brief summary about this question and answer within 1 sentence."

        response = openaiClient.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
        ],
        )
        raw_response = response.choices[0].message.content
        summaries.append(raw_response)  # Store summary in the list
    
    return summaries  

#################################################################################################
#   Helper function to generate the summary for a content. The summary is then prepended
#   input: semantic chunks, output: array of strings
#################################################################################################
def generate_summary_empty(semantic_chunks):  
    summaries = []  # New list to store summaries
    for semantic_chunk in semantic_chunks:   
        
        prompt = "\nPlease provide a brief summary about the following content within 1 sentence."
        prompt += f"{semantic_chunk.page_content}"

        response = openaiClient.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
        ],
        )
        raw_response = response.choices[0].message.content
        summaries.append(raw_response)  # Store summary in the list
    
    return summaries  

#################################################################################################
#   Helper function to upload into qdrant cloud
#   input: question, semantic chunks, summaries and output: nothing
#################################################################################################
def upload_to_qdrant(topic: webUrlTrain, semantic_chunks, summaries, collection_name):
    embedding_model = "text-embedding-3-large"


    try:
        point_count = qdrantClient.count(collection_name)
        index = point_count.count
        summary_index = 0

        logger.info(f"Previous {point_count}")

        

        logger.info(f"Starting Qdrant upload for URL: {topic.url}")
        logger.info(f"Initial index: {index}")

        for semantic_chunk in semantic_chunks:
            payload = {
                "id": topic.id,
                "answer": semantic_chunk.page_content,
                "url": topic.url,
            }

            if not payload['answer']:
                logger.warning(f"Empty answer for chunk at index {index}. Skipping.")
                continue

            str_to_embed = summaries[summary_index] + "\n" + semantic_chunk.page_content
            # logger.info(f"Summary is: {summaries[summary_index]}")
            logger.info(f"Index no {index}")
            try:
                content_embedding = openaiClient.embeddings.create(input=str_to_embed, model=embedding_model)
            except Exception as e:
                logger.error(f"Error creating embedding: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Embedding creation failed: {str(e)}")

            try:
                response = qdrantClient.upsert(
                    collection_name,
                    points=[
                        {
                            "id": index,
                            "vector": {
                                "content": content_embedding.data[0].embedding
                            },
                            "payload": payload
                        }
                    ]
                )
                print(response)
            except Exception as e:
                logger.error(f"Error upserting to Qdrant: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Qdrant upsert failed: {str(e)}")

            print(collection_name)
            point_count = qdrantClient.count(collection_name)
            logger.info(f"After {point_count}")
            index += 1
            summary_index += 1
            

        # logger.info(f"Qdrant upload completed. Total chunks uploaded: {index - point_count.count}")
        return {"status": "success", "chunks_uploaded": len(semantic_chunks)}

    except Exception as e:
        logger.error(f"Unexpected error in upload_to_qdrant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Qdrant upload failed: {str(e)}")

#################################################################################################
#   Helper function to Get all the vector-point IDs for a particular UUID of a question
#   input: UUID and output: array of points
#################################################################################################
def get_points_by_uuid(collection_name, uuid):
    offset = None
    all_points = []
    
    while True:
        result = qdrantClient.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(key="id", match=models.MatchValue(value=uuid)),
                ]
            ),
            limit=20,  
            with_payload=False,
            with_vectors=False,
            offset=offset
        )
        
        points, next_offset = result
        all_points.extend(points)
        
        if next_offset is None:
            break
        
        offset = next_offset
    
    all_point_ids = []
    all_point_ids.extend([point.id for point in points])
    return all_point_ids


#################################################################################################
#   Helper function to DELETE all the vector-point IDs for a particular UUID of a question
#   input: UUID and output: array of points
#################################################################################################
def delete_points_by_uuid(collection_name, uuid):
    try:
        response = qdrantClient.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="id",
                            match=models.MatchValue(value=uuid),
                        ),
                    ],
                )
            ),
        )
        
        # print(response)
        return True
        
    
    except Exception as e:
        print(f"An error occurred while deleting points: {e}")
        return False