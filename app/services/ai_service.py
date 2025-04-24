from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Pinecone
import pinecone
from typing import List, Dict, Optional
import torch
from PIL import Image
import clip
from transformers import CLIPProcessor, CLIPModel
from ..core.config import settings

class AIService:
    def __init__(self):
        # Initialize OpenAI
        self.llm = ChatOpenAI(
            model_name=settings.GPT_MODEL,
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize Pinecone
        pinecone.init(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENV
        )
        self.index = pinecone.Index(settings.PINECONE_INDEX_NAME)
        
        # Initialize CLIP
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(k=settings.CONVERSATION_MEMORY_K)
        
        # Initialize base prompt
        self.base_prompt = PromptTemplate(
            input_variables=["history", "input"],
            template="""You are an AI shopping assistant for an e-commerce website. You help customers find products, 
            answer questions about products, and make recommendations. Be helpful, friendly, and concise.

            Conversation history:
            {history}

            Human: {input}
            Assistant:"""
        )
        
        # Initialize conversation chain
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=self.base_prompt
        )

    async def get_response(self, query: str, context: Optional[Dict] = None) -> str:
        """Generate a response to a user query."""
        if context:
            # Augment the query with context
            query = f"Context: {context}\nQuery: {query}"
        
        response = await self.conversation.apredict(input=query)
        return response

    async def get_product_recommendations(self, query: str, n: int = 5) -> List[Dict]:
        """Get product recommendations based on text query."""
        # Get query embedding
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Search Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=n,
            include_metadata=True
        )
        
        return [result.metadata for result in results.matches]

    async def search_by_image(self, image: Image.Image, n: int = 5) -> List[Dict]:
        """Search for products using an image."""
        # Preprocess image
        image_input = self.clip_preprocess(image).unsqueeze(0).to(self.device)
        
        # Get image embedding
        with torch.no_grad():
            image_features = self.clip_model.encode_image(image_input)
            image_embedding = image_features.cpu().numpy().tolist()[0]
        
        # Search Pinecone
        results = self.index.query(
            vector=image_embedding,
            top_k=n,
            include_metadata=True
        )
        
        return [result.metadata for result in results.matches]

    async def hybrid_search(self, text_query: str, image: Optional[Image.Image] = None, n: int = 5) -> List[Dict]:
        """Perform hybrid search using both text and image if available."""
        # Get text embedding
        text_embedding = await self.embeddings.aembed_query(text_query)
        
        if image:
            # Get image embedding
            image_input = self.clip_preprocess(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_input)
                image_embedding = image_features.cpu().numpy().tolist()[0]
            
            # Combine embeddings (simple average for now)
            combined_embedding = [(t + i) / 2 for t, i in zip(text_embedding, image_embedding)]
        else:
            combined_embedding = text_embedding
        
        # Search Pinecone
        results = self.index.query(
            vector=combined_embedding,
            top_k=n,
            include_metadata=True
        )
        
        return [result.metadata for result in results.matches]

# Create singleton instance
ai_service = AIService() 