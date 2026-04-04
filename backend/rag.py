import faiss
import numpy as np
from google import genai
from rank_bm25 import BM25Okapi

def chunk_text(texts: str, chunk_size: int=100, overlap: int =25 ) -> list:
    words = texts.split()
    chunks = []
    for i in range (0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks    
         
         
def get_embeddings(texts:list[str]) -> np.ndarray:
    
    client = genai.Client()
    
    response = client.models.embed_content(
        model = 'gemini-embedding-001',
        contents = texts
    )    
    
    vectors = [item.values for item in response.embeddings]     
    return np.array(vectors).astype('float32')

def find_relevant_resume_sections(resume_text: str, job_description: str, top_k: int = 4) -> str:
    resume_chunks = chunk_text(resume_text)
    
    if not resume_chunks:
        return ""
    
    num_chunks = len(resume_chunks)
    
    chunk_embeddings = get_embeddings(resume_chunks)
    jd_embedding = get_embeddings([job_description])
    
    dimension = chunk_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    
    index.add(chunk_embeddings)
        
    distances, faiss_indices = index.search(jd_embedding, num_chunks)
    vector_ranked_indices = faiss_indices[0]
    
    tokenized_chunks = [chunk.lower().split() for chunk in resume_chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    
    tokenized_query = job_description.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    bm25_ranked_indices = np.argsort(bm25_scores)[::-1]
    
    rrf_scores = {i: 0.0 for i in range(num_chunks)}
    k = 60 
    
    for rank,chunk_idx in enumerate(vector_ranked_indices):
        rrf_scores[chunk_idx] += 1.0 / (k + rank)
    
    for rank, chunk_idx in enumerate(bm25_ranked_indices):
        rrf_scores[chunk_idx] += 1.0 / (k + rank)
        
    final_ranked_indices = sorted(rrf_scores, key=rrf_scores.get, reverse=True)
    
    top_indices = final_ranked_indices[:top_k]    
    
    top_indices.sort()

    relevant_text = "\n...\n".join([resume_chunks[i] for i in top_indices])
    return relevant_text

    