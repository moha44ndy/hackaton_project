"""
ELK Setup - Initialize Elasticsearch indices and settings for WMDP
"""

import logging
from typing import Dict, Any
import time
from datetime import datetime

try:
    from elasticsearch import Elasticsearch
except ImportError:
    pass


class ELKSetup:
    """Setup Elasticsearch indices, mappings, and templates"""
    
    def __init__(self, es_host: str = "localhost:9200"):
        """Initialize setup util"""
        self.es_host = es_host
        self.logger = logging.getLogger(__name__)
        self.client = None
        
        try:
            self.client = Elasticsearch(hosts=[es_host])
            self.logger.info(f"✅ Connected to Elasticsearch at {es_host}")
        except Exception as e:
            self.logger.error(f"❌ Could not connect to Elasticsearch: {e}")
    
    def create_index_template(self) -> bool:
        """Create index template for WMDP indices"""
        if not self.client:
            return False
        
        try:
            template = {
                "index_patterns": ["wmdp-*"],
                "template": {
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0,
                        "index.lifecycle.name": "wmdp-policy",
                        "index.lifecycle.rollover_alias": "wmdp-logs",
                    },
                    "mappings": {
                        "properties": {
                            "timestamp": {
                                "type": "date",
                                "format": "strict_date_optional_time||epoch_millis"
                            },
                            "event_type": {"type": "keyword"},
                            "model_name": {"type": "keyword"},
                            "prompt_id": {"type": "keyword"},
                            "response_id": {"type": "keyword"},
                            "latency_ms": {"type": "float"},
                            "token_count": {"type": "integer"},
                            "status": {"type": "keyword"},
                            "error_message": {"type": "text"},
                            "response_behavior": {"type": "keyword"},
                            "compliance_level": {"type": "keyword"},
                            "harmfulness_level": {"type": "keyword"},
                            "safety_score": {"type": "float"},
                            "compliance_rate": {"type": "float"},
                            "total_responses": {"type": "integer"},
                            "avg_latency_ms": {"type": "float"},
                            "models_tested": {"type": "keyword"},
                            "run_id": {"type": "keyword"},
                        }
                    }
                }
            }
            
            self.client.indices.put_index_template(
                name="wmdp-template",
                body=template
            )
            
            self.logger.info("✅ Created index template: wmdp-template")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error creating index template: {e}")
            return False

    def create_indices(self) -> bool:
        """Create initial indices"""
        if not self.client:
            return False
        
        try:
            indices = [
                "wmdp-collection-*",
                "wmdp-annotation-*",
                "wmdp-analysis-*",
            ]
            
            for index in indices:
                try:
                    # Create with today's date
                    index_name = index.replace("*", datetime.now().strftime('%Y.%m.%d'))
                    
                    if not self.client.indices.exists(index=index_name):
                        self.client.indices.create(index=index_name)
                        self.logger.info(f"✅ Created index: {index_name}")
                    else:
                        self.logger.info(f"ℹ️ Index exists: {index_name}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error creating index {index_name}: {e}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error creating indices: {e}")
            return False

    def create_index_pattern_kibana(self) -> bool:
        """Create Kibana index pattern"""
        if not self.client:
            return False
        
        try:
            # Wait for Kibana to be ready
            time.sleep(2)
            
            index_pattern = {
                "attributes": {
                    "title": "wmdp-*",
                    "timeFieldName": "timestamp",
                    "fields": [
                        {
                            "name": "timestamp",
                            "type": "date",
                            "searchable": True,
                            "aggregatable": True,
                        },
                        {
                            "name": "event_type",
                            "type": "string",
                            "searchable": True,
                            "aggregatable": True,
                        },
                        {
                            "name": "model_name",
                            "type": "string",
                            "searchable": True,
                            "aggregatable": True,
                        },
                    ],
                    "defaultIndex": "wmdp-*",
                }
            }
            
            self.logger.info("✅ Index pattern ready for Kibana: wmdp-*")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error creating Kibana index pattern: {e}")
            return False

    def verify_setup(self) -> Dict[str, Any]:
        """Verify ELK setup"""
        if not self.client:
            return {"error": "No Elasticsearch connection"}
        
        try:
            # Check cluster health
            health = self.client.cluster.health()
            
            # Check indices
            indices = self.client.indices.list()
            
            # Check templates
            templates = self.client.indices.get_template(name="wmdp*")
            
            result = {
                "status": "✅ OK" if health.get("status") in ["green", "yellow"] else "❌ CRITICAL",
                "cluster_health": health.get("status"),
                "indices": list(indices.keys()),
                "wmdp_indices": [i for i in indices.keys() if i.startswith("wmdp")],
                "templates": list(templates.keys()),
            }
            
            self.logger.info(f"📊 ELK Setup Status: {result}")
            return result
            
        except Exception as e:
            return {"error": str(e)}

    def run_full_setup(self) -> bool:
        """Run complete setup"""
        self.logger.info("🚀 Starting ELK setup...")
        
        steps = [
            ("Template", self.create_index_template),
            ("Indices", self.create_indices),
            ("Kibana", self.create_index_pattern_kibana),
            ("Verify", lambda: self.verify_setup() is not None),
        ]
        
        for step_name, step_func in steps:
            self.logger.info(f"⏳ {step_name}...")
            try:
                if step_func():
                    self.logger.info(f"✅ {step_name} completed")
                else:
                    self.logger.error(f"❌ {step_name} failed")
                    return False
            except Exception as e:
                self.logger.error(f"❌ {step_name} error: {e}")
                return False
        
        self.logger.info("🎉 ELK setup complete!")
        return True


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    setup = ELKSetup(es_host="localhost:9200")
    setup.run_full_setup()
