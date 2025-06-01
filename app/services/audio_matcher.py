import json
import logging
from typing import Dict, List, Optional, Union, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.config.settings import Config
from app.models.enums import MatchingMethod, ResponseStatus, ConfidenceScore, AudioFileName
from app.models.schemas import QueryResponse, DetailedScores, HybridScores, ComparisonInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioMatcher:
    def __init__(self, audio_base_path: str = "audio_base.json"):
        """
        Initialize the audio matcher
        
        Args:
            audio_base_path: Path to the JSON file with the audio database
        """
        self.model = None
        self.audio_descriptions = {}
        self.embeddings = {}
        self.individual_embeddings = {}
        self.combined_embeddings = {}
        self.threshold = Config.SIMILARITY_THRESHOLD
        
        self._load_model()
        self._load_audio_base(audio_base_path)
        self._precompute_embeddings()
    
    def _load_model(self):
        try:
            logger.info(f"Loading model {Config.MODEL_NAME}...")
            self.model = SentenceTransformer(Config.MODEL_NAME)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def _load_audio_base(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.audio_descriptions = json.load(f)
            logger.info(f"Loaded {len(self.audio_descriptions)} audios")
        except FileNotFoundError:
            logger.error(f"File {path} not found")
            self._create_default_audio_base(path)
        except Exception as e:
            logger.error(f"Error loading audio database: {e}")
            raise
    
    def _create_default_audio_base(self, path: str):
        default_base = {
            "example.ogg": [
                "example question",
                "test query"
            ]
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_base, f, indent=2, ensure_ascii=False)
        self.audio_descriptions = default_base
        logger.info("Created default base file")
    
    def _precompute_embeddings(self):
        logger.info("Precomputing embeddings...")
        
        for audio_file, descriptions in self.audio_descriptions.items():
            individual_embs = []
            for desc in descriptions:
                emb = self.model.encode(desc)
                individual_embs.append(emb)
            
            self.individual_embeddings[audio_file] = individual_embs
            
            combined_text = " ".join(descriptions)
            combined_emb = self.model.encode(combined_text)
            self.combined_embeddings[audio_file] = combined_emb
            
            if Config.DEBUG_MODE:
                logger.debug(f"Embeddings calculados para {audio_file}: {len(individual_embs)} individuales + 1 combinado")
        
        logger.info(f"Embeddings precomputados para {len(self.individual_embeddings)} audios")
     
    def find_best_match(self, query: str, method: Union[MatchingMethod, str] = MatchingMethod.HYBRID) -> Dict[str, any]:
        try:
            if isinstance(method, str):
                try:
                    method = MatchingMethod(method)
                except ValueError:
                    raise ValueError(f"Unknown method: {method}. Valid options: {[m.value for m in MatchingMethod]}")
            
            if not query.strip():
                return self._create_error_response(
                    "Empty query provided. Please provide a non-empty query.", 
                    method, 
                    confidence=0.0
                )
            
            query_embedding = self.model.encode(query)
            
            match method:
                case MatchingMethod.INDIVIDUAL:
                    result = self._match_individual(query_embedding, query)
                case MatchingMethod.COMBINED:
                    result = self._match_combined(query_embedding, query)
                case MatchingMethod.HYBRID:
                    result = self._match_hybrid(query_embedding, query)
                case MatchingMethod.MAX:
                    result = self._match_max(query_embedding, query)
                case _:
                    raise ValueError(f"Método no implementado: {method}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en find_best_match: {e}")
            return self._create_error_response(
                f"Error interno del sistema: {str(e)}",
                method if isinstance(method, MatchingMethod) else MatchingMethod.HYBRID,
                error=str(e)
            )

    def _match_individual(self, query_embedding: np.ndarray, query: str) -> Dict[str, any]:
        best_match: Optional[AudioFileName] = None
        best_score: ConfidenceScore = 0.0
        scores: Dict[str, float] = {}
        detailed_scores: Dict[str, DetailedScores] = {}
        
        for audio_file, embeddings_list in self.individual_embeddings.items():
            similarities: List[float] = []
            for emb in embeddings_list:
                sim = cosine_similarity([query_embedding], [emb])[0][0]
                similarities.append(float(sim))
            
            max_sim = max(similarities) if similarities else 0.0
            scores[audio_file] = max_sim
            
            detailed_scores[audio_file] = {
                "individual_scores": similarities,
                "descriptions": self.audio_descriptions[audio_file],
                "max_score": max_sim
            }
            
            if max_sim > best_score:
                best_score = max_sim
                best_match = audio_file
        
        return self._format_response(best_match, best_score, scores, detailed_scores, MatchingMethod.INDIVIDUAL)
    
    def _match_combined(self, query_embedding: np.ndarray, query: str) -> Dict[str, any]:
        best_match: Optional[AudioFileName] = None
        best_score: ConfidenceScore = 0.0
        scores: Dict[str, float] = {}
        
        for audio_file, audio_embedding in self.combined_embeddings.items():
            similarity = cosine_similarity([query_embedding], [audio_embedding])[0][0]
            scores[audio_file] = float(similarity)
            
            if similarity > best_score:
                best_score = similarity
                best_match = audio_file
        
        return self._format_response(best_match, best_score, scores, None, MatchingMethod.COMBINED)
    
    def _match_hybrid(self, query_embedding: np.ndarray, query: str) -> Dict[str, any]:
        individual_result = self._match_individual(query_embedding, query)
        combined_result = self._match_combined(query_embedding, query)
        
        weight_individual = 0.7
        weight_combined = 0.3
        
        ind_scores = individual_result.get("all_scores", {}) or {}
        comb_scores = combined_result.get("all_scores", {}) or {}
        
        hybrid_scores: Dict[str, float] = {}
        for audio_file in self.audio_descriptions.keys():
            ind_score = float(ind_scores.get(audio_file, 0))
            comb_score = float(comb_scores.get(audio_file, 0))
            
            hybrid_score = (weight_individual * ind_score) + (weight_combined * comb_score)
            hybrid_scores[audio_file] = float(hybrid_score)
        
        hybrid_detailed_scores: HybridScores = {
            "individual_scores": ind_scores,
            "combined_scores": comb_scores,
            "weights": {"individual": weight_individual, "combined": weight_combined}
        }
        
        if not hybrid_scores:
            return self._format_response(None, 0.0, {}, hybrid_detailed_scores, MatchingMethod.HYBRID)
        
        best_match_item = max(hybrid_scores.items(), key=lambda x: float(x[1]))
        best_audio, best_score = best_match_item
        
        return self._format_response(best_audio, float(best_score), hybrid_scores, hybrid_detailed_scores, MatchingMethod.HYBRID)
    
    def _match_max(self, query_embedding: np.ndarray, query: str) -> Dict[str, any]:
        """Toma el máximo entre método individual y combinado"""
        individual_result = self._match_individual(query_embedding, query)
        combined_result = self._match_combined(query_embedding, query)
        
        ind_best = float(individual_result.get("confidence", 0))
        comb_best = float(combined_result.get("confidence", 0))
        
        ind_response = individual_result.get("response")
        comb_response = combined_result.get("response")
        
        if ind_response == Config.NO_MATCH_RESPONSE and comb_response != Config.NO_MATCH_RESPONSE:
            result = combined_result.copy()
            result["method"] = MatchingMethod.MAX.value
            result["method_used"] = "combined_was_only_valid"
            result["compared_with"] = {"individual_score": ind_best}
            return result
        elif comb_response == Config.NO_MATCH_RESPONSE and ind_response != Config.NO_MATCH_RESPONSE:
            result = individual_result.copy()
            result["method"] = MatchingMethod.MAX.value
            result["method_used"] = "individual_was_only_valid"
            result["compared_with"] = {"combined_score": comb_best}
            return result
        
        if ind_best >= comb_best:
            result = individual_result.copy()
            result["method"] = MatchingMethod.MAX.value
            result["method_used"] = "individual_was_better"
            result["compared_with"] = {"combined_score": comb_best}
        else:
            result = combined_result.copy()
            result["method"] = MatchingMethod.MAX.value
            result["method_used"] = "combined_was_better"
            result["compared_with"] = {"individual_score": ind_best}
        
        return result
    
    def _create_error_response(self, message: str, method: MatchingMethod, confidence: float = 0.0, error: Optional[str] = None) -> Dict[str, any]:
        return {
            "response": Config.ERROR_RESPONSE,
            "confidence": confidence,
            "method": method.value,
            "message": message,
            "status": ResponseStatus.ERROR.value,
            "error": error,
            "best_candidate": None,
            "all_scores": None,
            "detailed_scores": None,
            "method_used": None,
            "compared_with": None
        }
    
    def _format_response(self, 
                        best_match: Optional[AudioFileName], 
                        best_score: ConfidenceScore, 
                        scores: Dict[str, float], 
                        detailed_scores: Optional[Dict], 
                        method: Union[MatchingMethod, str]) -> Dict[str, any]:
        method_str = method.value if isinstance(method, MatchingMethod) else method
        
        if best_score >= self.threshold and best_match:
            status = ResponseStatus.SUCCESS
            response_value = best_match
            message = f"Match encontrado con confianza {best_score:.3f} usando método {method_str}"
            best_candidate = None
        else:
            status = ResponseStatus.NO_MATCH
            response_value = Config.NO_MATCH_RESPONSE
            message = f"No hay match suficientemente bueno. Mejor score: {best_score:.3f} con método {method_str}"
            best_candidate = best_match
        
        response = {
            "response": response_value,
            "confidence": float(best_score),
            "method": method_str,
            "message": message,
            "status": status.value,
            "best_candidate": best_candidate,
            "all_scores": scores if Config.DEBUG_MODE else None,
            "detailed_scores": detailed_scores if Config.DEBUG_MODE and detailed_scores else None,
            "method_used": None,
            "compared_with": None,
            "error": None
        }
        
        return response
    
    def add_audio(self, audio_file: AudioFileName, descriptions: List[str]) -> bool:
        try:
            self.audio_descriptions[audio_file] = descriptions
            
            individual_embs = []
            for desc in descriptions:
                emb = self.model.encode(desc)
                individual_embs.append(emb)
            
            self.individual_embeddings[audio_file] = individual_embs
            
            combined_text = " ".join(descriptions)
            combined_emb = self.model.encode(combined_text)
            self.combined_embeddings[audio_file] = combined_emb
            
            self.embeddings[audio_file] = combined_emb
            
            logger.info(f"Audio added: {audio_file} with {len(descriptions)} descriptions")
            return True
        except Exception as e:
            logger.error(f"Error adding audio: {e}")
            return False
    
    def update_threshold(self, new_threshold: float):
        if 0.0 <= new_threshold <= 1.0:
            self.threshold = new_threshold
            logger.info(f"Threshold updated to {new_threshold}")
            return True
        return False
    
    def get_stats(self) -> Dict:
        return {
            "total_audios": len(self.audio_descriptions),
            "model": Config.MODEL_NAME,
            "current_threshold": self.threshold,
            "available_audios": list(self.audio_descriptions.keys())
        }