"""
ELK Logger - Centralized logging to Elasticsearch

Logs all pipeline events:
- Collection events (Phase 1)
- Annotation events (Phase 2)
- Analysis events (Phase 3)
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

try:
    from elasticsearch import Elasticsearch
except ImportError:
    Elasticsearch = None


@dataclass
class CollectionEvent:
    """Event from Phase 1: Data Collection"""
    timestamp: str
    event_type: str = "collection"
    model_name: str = ""
    prompt_id: str = ""
    prompt_text: str = ""
    response_text: str = ""
    latency_ms: float = 0
    token_count: int = 0
    status: str = "success"  # success, error, timeout
    error_message: Optional[str] = None


@dataclass
class AnnotationEvent:
    """Event from Phase 2: Response Annotation"""
    timestamp: str
    event_type: str = "annotation"
    response_id: str = ""
    response_behavior: str = ""  # aligned_refusal, safe_compliance, etc
    compliance_level: str = ""  # compliant, attempting_refusal, non_compliant
    harmfulness_level: str = ""  # low, medium, high, critical
    annotator_id: str = "automatic"


@dataclass
class AnalysisEvent:
    """Event from Phase 3: Analysis & Reporting"""
    timestamp: str
    event_type: str = "analysis"
    run_id: str = ""
    total_responses: int = 0
    avg_latency_ms: float = 0
    models_tested: list = None
    safety_score: float = 0
    compliance_rate: float = 0


class ELKLogger:
    """
    Centralized logger for Elasticsearch
    
    Usage:
        logger = ELKLogger(es_host="localhost:9200")
        logger.log_collection_event({...})
        logger.log_annotation_event({...})
        logger.log_analysis_event({...})
    """

    def __init__(
        self,
        es_host: str = "localhost:9200",
        index_prefix: str = "wmdp",
        enabled: bool = True
    ):
        """
        Initialize ELK Logger
        
        Args:
            es_host: Elasticsearch host (default: localhost:9200)
            index_prefix: Index prefix for logs (default: wmdp)
            enabled: Enable/disable logging (for testing)
        """
        self.es_host = es_host
        self.index_prefix = index_prefix
        self.enabled = enabled
        self.es_client = None
        self.logger = logging.getLogger(__name__)
        
        if enabled:
            if Elasticsearch is None:
                self.logger.warning("⚠️ elasticsearch package not installed. Install with: pip install elasticsearch")
                self.enabled = False
            else:
                try:
                    self.es_client = Elasticsearch(
                        hosts=[es_host],
                        request_timeout=10,
                        max_retries=3,
                        retry_on_timeout=True
                    )
                    # Test connection
                    info = self.es_client.info()
                    self.logger.info(f"✅ Connected to Elasticsearch: {info['version']['number']}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not connect to Elasticsearch: {e}")
                    self.enabled = False

    def log_collection_event(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Log a collection phase event with annotations included
        
        Args:
            event: CollectionEvent data (can include response_behavior, compliance_level, harmfulness_level)
            
        Returns:
            Document ID if successful, None otherwise
        """
        if not self.enabled or not self.es_client:
            self.logger.debug("ELK Logger disabled or not connected")
            return None
        
        try:
            index_name = f"{self.index_prefix}-collection-{datetime.now().strftime('%Y.%m.%d')}"
            
            doc = {
                "timestamp": event.get("timestamp", datetime.now().isoformat()),
                "@timestamp": event.get("timestamp", datetime.now().isoformat()),
                "event_type": "collection",
                "model_name": event.get("model_name", ""),
                "prompt_id": event.get("prompt_id", ""),
                "prompt_text": event.get("prompt_text", ""),
                "response_text": event.get("response_text", ""),
                "latency_ms": float(event.get("latency_ms", 0)),
                "token_count": int(event.get("token_count", 0)),
                "status": event.get("status", "success"),
                # Include annotations directly
                "response_behavior": event.get("response_behavior", "unknown"),
                "compliance_level": event.get("compliance_level", "unknown"),
                "harmfulness_level": event.get("harmfulness_level", "unknown"),
                "prompt_category": event.get("prompt_category", ""),
                "prompt_risk_level": event.get("prompt_risk_level", ""),
            }
            
            result = self.es_client.index(index=index_name, document=doc)
            doc_id = result.get("_id", "")
            
            self.logger.debug(f"📊 Logged collection event: {doc_id}")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"❌ Error logging collection event: {e}")
            return None

    def log_annotation_event(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Log an annotation phase event
        
        Args:
            event: AnnotationEvent data
            
        Returns:
            Document ID if successful, None otherwise
        """
        if not self.enabled or not self.es_client:
            return None
        
        try:
            index_name = f"{self.index_prefix}-annotation-{datetime.now().strftime('%Y.%m.%d')}"
            
            doc = {
                "timestamp": event.get("timestamp", datetime.now().isoformat()),
                "event_type": "annotation",
                "response_id": event.get("response_id", ""),
                "response_behavior": event.get("response_behavior", ""),
                "compliance_level": event.get("compliance_level", ""),
                "harmfulness_level": event.get("harmfulness_level", ""),
                "annotator_id": event.get("annotator_id", "automatic"),
            }
            
            result = self.es_client.index(index=index_name, document=doc)
            doc_id = result.get("_id", "")
            
            self.logger.debug(f"📊 Logged annotation event: {doc_id}")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"❌ Error logging annotation event: {e}")
            return None

    def log_analysis_event(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Log an analysis phase event
        
        Args:
            event: AnalysisEvent data
            
        Returns:
            Document ID if successful, None otherwise
        """
        if not self.enabled or not self.es_client:
            return None
        
        try:
            index_name = f"{self.index_prefix}-analysis-{datetime.now().strftime('%Y.%m.%d')}"
            
            doc = {
                "timestamp": event.get("timestamp", datetime.now().isoformat()),
                "event_type": "analysis",
                "run_id": event.get("run_id", ""),
                "total_responses": int(event.get("total_responses", 0)),
                "avg_latency_ms": float(event.get("avg_latency_ms", 0)),
                "models_tested": event.get("models_tested", []),
                "safety_score": float(event.get("safety_score", 0)),
                "compliance_rate": float(event.get("compliance_rate", 0)),
            }
            
            result = self.es_client.index(index=index_name, document=doc)
            doc_id = result.get("_id", "")
            
            self.logger.debug(f"📊 Logged analysis event: {doc_id}")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"❌ Error logging analysis event: {e}")
            return None

    def query_events(
        self,
        event_type: str = "collection",
        limit: int = 100,
        days_back: int = 7
    ) -> list:
        """
        Query events from Elasticsearch
        
        Args:
            event_type: 'collection', 'annotation', or 'analysis'
            limit: Number of results to return
            days_back: Days of history to query
            
        Returns:
            List of events
        """
        if not self.enabled or not self.es_client:
            return []
        
        try:
            index_pattern = f"{self.index_prefix}-{event_type}-*"
            
            query = {
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": f"now-{days_back}d/d"
                        }
                    }
                },
                "size": limit,
                "sort": [{"timestamp": {"order": "desc"}}]
            }
            
            results = self.es_client.search(index=index_pattern, body=query)
            
            events = []
            for hit in results.get("hits", {}).get("hits", []):
                events.append(hit["_source"])
            
            self.logger.debug(f"📊 Retrieved {len(events)} {event_type} events")
            return events
            
        except Exception as e:
            self.logger.error(f"❌ Error querying events: {e}")
            return []

    def get_stats(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Get summary statistics from logs
        
        Args:
            days_back: Days of history to analyze
            
        Returns:
            Statistics dictionary
        """
        if not self.enabled or not self.es_client:
            return {}
        
        try:
            stats = {
                "total_collections": 0,
                "total_annotations": 0,
                "total_analyses": 0,
                "avg_latency_ms": 0,
                "error_count": 0,
                "models_used": [],
                "safety_score_avg": 0,
            }
            
            # Get collection stats
            collection_events = self.query_events("collection", limit=1000, days_back=days_back)
            stats["total_collections"] = len(collection_events)
            if collection_events:
                latencies = [e.get("latency_ms", 0) for e in collection_events]
                stats["avg_latency_ms"] = sum(latencies) / len(latencies) if latencies else 0
                stats["error_count"] = len([e for e in collection_events if e.get("status") == "error"])
                models = set([e.get("model_name") for e in collection_events if e.get("model_name")])
                stats["models_used"] = list(models)
            
            # Get annotation stats
            annotation_events = self.query_events("annotation", limit=1000, days_back=days_back)
            stats["total_annotations"] = len(annotation_events)
            
            # Get analysis stats
            analysis_events = self.query_events("analysis", limit=100, days_back=days_back)
            stats["total_analyses"] = len(analysis_events)
            if analysis_events:
                scores = [e.get("safety_score", 0) for e in analysis_events]
                stats["safety_score_avg"] = sum(scores) / len(scores) if scores else 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ Error getting stats: {e}")
            return {}

    def health_check(self) -> bool:
        """Check if Elasticsearch is accessible"""
        if not self.enabled:
            return False
        
        try:
            if self.es_client:
                self.es_client.info()
                return True
        except Exception:
            pass
        return False


# Singleton instance
_elk_logger = None


def get_elk_logger(es_host: str = "localhost:9200", enabled: bool = True) -> ELKLogger:
    """Get or create ELK logger singleton"""
    global _elk_logger
    if _elk_logger is None:
        _elk_logger = ELKLogger(es_host=es_host, enabled=enabled)
    return _elk_logger
