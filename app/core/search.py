from typing import List, Dict, Optional, Union
import pinecone
import openai
from dotenv import load_dotenv
import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class HybridSearch:
    def __init__(self):
        try:
            # Initialize Pinecone
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY not found in environment variables")
                
            index_name = os.getenv("PINECONE_INDEX_NAME", "commerce-agent")
            logger.info(f"Initializing Pinecone with index: {index_name}")
            
            # Initialize Pinecone with the new client
            self.pc = pinecone.Pinecone(api_key=api_key)
            self.index = self.pc.Index(index_name)
            logger.info("Pinecone initialized successfully")
            
            # Initialize OpenAI
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
            logger.info("OpenAI initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing search: {str(e)}")
            raise
        
        # Keywords for feature matching
        self.feature_mapping = {
            "laptops": {
                "battery": ["battery life", "battery", "long battery", "battery duration"],
                "gaming": ["gaming", "gamer", "gpu", "graphics", "rtx", "nvidia", "amd"],
                "business": ["business", "professional", "work", "office"],
                "student": ["student", "college", "school", "education"],
                "creative": ["creative", "design", "art", "video editing", "photo editing"],
                "build": ["durable", "premium", "lightweight", "slim", "military-grade"]
            },
            "smartphones": {
                "camera": ["camera", "photo", "photography", "video", "night mode", "portrait"],
                "battery": ["battery", "battery life", "long battery", "battery capacity"],
                "display": ["display", "screen", "refresh rate", "hz", "amoled", "oled"],
                "5g": ["5g", "5g connectivity", "5g network"],
                "security": ["fingerprint", "face recognition", "security", "biometric"]
            },
            "tablets": {
                "art": ["art", "drawing", "digital art", "stylus", "pen"],
                "productivity": ["productivity", "work", "keyboard", "office"],
                "entertainment": ["entertainment", "media", "streaming", "gaming"],
                "battery": ["battery", "battery life", "long battery"],
                "display": ["display", "screen", "promotion", "hdr", "true tone"]
            },
            "audio": {
                "noise": ["noise cancelling", "noise cancellation", "quiet", "silence"],
                "battery": ["battery", "battery life", "long battery"],
                "sound": ["sound", "audio", "bass", "spatial", "hifi", "audiophile"],
                "comfort": ["comfort", "comfortable", "ergonomic", "lightweight"],
                "sports": ["sports", "workout", "running", "exercise", "gym"]
            }
        }

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text query"""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def _extract_exact_features(self, query: str, category: str) -> Dict[str, float]:
        """Extract exact features from query using regex patterns"""
        features = {}
        if category in self.feature_mapping:
            for feature_type, keywords in self.feature_mapping[category].items():
                for keyword in keywords:
                    if keyword in query.lower():
                        features[feature_type] = 1.0
        return features

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Hybrid search combining semantic and exact feature matching
        
        Args:
            query: Natural language search query
            category: Filter by product category
            min_price: Minimum price filter
            max_price: Maximum price filter
            top_k: Number of results to return
            
        Returns:
            List of matching products with scores
        """
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Match exact features if category specified
        exact_features = self._extract_exact_features(query, category) if category else {}
        
        # Build filter conditions
        filter_conditions = {}
        if category:
            filter_conditions["category"] = {"$eq": category}
        if min_price is not None:
            filter_conditions["price"] = {"$gte": min_price}
        if max_price is not None:
            if "price" in filter_conditions:
                filter_conditions["price"]["$lte"] = max_price
            else:
                filter_conditions["price"] = {"$lte": max_price}
        
        # Search Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k * 2,  # Get extra results for filtering
            include_metadata=True,
            namespace="products",
            filter=filter_conditions if filter_conditions else None
        )
        
        # Apply feature matching if needed
        if exact_features:
            filtered_results = []
            for match in results.matches:
                product = match.metadata
                
                if category and product["category"] != category:
                    continue
                
                if min_price is not None and product["price"] < min_price:
                    continue
                if max_price is not None and product["price"] > max_price:
                    continue

                # Calculate feature match boost
                feature_score = 0.0
                product_features = " ".join(product["features"]).lower()
                for feature_type, weight in exact_features.items():
                    if any(keyword in product_features for keyword in self.feature_mapping[category][feature_type]):
                        feature_score += weight

                # Combine scores
                combined_score = match.score * (1 + feature_score)
                
                filtered_results.append({
                    "id": match.id,
                    "score": combined_score,
                    "metadata": product
                })
            
            filtered_results.sort(key=lambda x: x["score"], reverse=True)
            results.matches = filtered_results[:top_k]
        else:
            results.matches = results.matches[:top_k]
        
        return [{
            "id": match.id,
            "score": match.score,
            "metadata": match.metadata
        } for match in results.matches]

    def recommend_similar(
        self,
        product_id: str,
        category: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Find similar products based on a reference product
        
        Args:
            product_id: ID of the reference product
            category: Filter by product category
            top_k: Number of recommendations to return
            
        Returns:
            List of similar products with scores
        """
        # Get reference product
        ref_product = self.index.fetch(ids=[product_id], namespace="products")
        if not ref_product.vectors:
            return []
        
        # Search using product's embedding
        ref_vector = ref_product.vectors[product_id].values
        filter_conditions = {"id": {"$ne": product_id}}
        if category:
            filter_conditions["category"] = {"$eq": category}
        
        results = self.index.query(
            vector=ref_vector,
            top_k=top_k + 1,
            include_metadata=True,
            namespace="products",
            filter=filter_conditions
        )
        
        similar_products = []
        for match in results.matches:
            if match.id == product_id:
                continue
            if category and match.metadata["category"] != category:
                continue
            similar_products.append({
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            })
        
        return similar_products[:top_k]

    def get_product(self, product_id: str) -> Optional[dict]:
        """
        Get a product by its ID
        """
        try:
            # Fetch the vector and metadata for the product
            response = self.index.fetch(ids=[product_id], namespace="products")
            if not response.vectors or product_id not in response.vectors:
                return None
            return response.vectors[product_id].metadata
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {str(e)}")
            return None 