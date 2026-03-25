"""
AI Chatbot Service for CarbonSense v2
Natural language processing and conversational Q&A
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
import re
from datetime import datetime


@dataclass
class ChatMessage:
    """Represents a chat message"""
    content: str
    timestamp: str
    sender: str  # "user" or "bot"


@dataclass
class ChatIntent:
    """Detected user intent"""
    intent_type: str  # forecast, anomaly, simulation, esg, benchmark, csv_upload, status, help
    confidence: float
    entities: Dict[str, Any]
    relevant_services: List[str]


@dataclass
class ChatResponse:
    """Chatbot response"""
    message: str
    intent: str
    suggestions: List[str]
    service_calls: List[Dict[str, Any]]
    confidence: float


class AIConversationService:
    """Handle intelligent conversations about emissions data"""
    
    def __init__(self):
        """Initialize conversation service"""
        self.conversation_history = []
        self.current_context = {}
        self.max_history = 20
        
        # Intent patterns
        self.intent_patterns = {
            "forecast": [
                r"forecast|predict|trend|what.*happen|future|next.*month",
                r"emissions.*trend|growth|decline|projection"
            ],
            "anomaly": [
                r"anomaly|unusual|spike|unusual|outlier|strange|odd|weird",
                r"something.*wrong|abnormal|issue|problem|alert"
            ],
            "simulation": [
                r"scenario|what.*if|simulation|model|risk|monte carlo",
                r"probability|uncertainty|volatility|stress.*test"
            ],
            "esg": [
                r"esg|environmental|social|governance|score|rating",
                r"sustainability|green|responsible|impact"
            ],
            "benchmark": [
                r"benchmark|compare|industry|peer|average|standard",
                r"performance|compete|ranking|best.*practice"
            ],
            "csv": [
                r"upload|import|csv|data.*file|historical",
                r"load.*data|process.*file|batch"
            ],
            "status": [
                r"how.*|what.*status|tell.*about|explain",
                r"summary|overview|dashboard|health"
            ],
            "help": [
                r"help|guide|how.*use|tutorial|assist|support"
            ]
        }
        
        # Response templates
        self.response_templates = {
            "forecast": {
                "greeting": "I'll help you forecast emissions trends.",
                "actions": [
                    "Run LSTM forecast (12 months)",
                    "Scenario analysis (with reduction goals)",
                    "Ensemble forecast (most accurate)"
                ]
            },
            "anomaly": {
                "greeting": "Let me check for anomalies in your data.",
                "actions": [
                    "Detect unusual patterns",
                    "Analyze severity levels",
                    "Generate health summary"
                ]
            },
            "simulation": {
                "greeting": "I'll run a Monte Carlo simulation for risk analysis.",
                "actions": [
                    "Generate 10,000 possible scenarios",
                    "Calculate risk metrics (VaR, CVaR)",
                    "Assess volatility and trends"
                ]
            },
            "esg": {
                "greeting": "Let me calculate your ESG score.",
                "actions": [
                    "Score E (Environmental)",
                    "Score S (Social)",
                    "Score G (Governance)",
                    "Compare with industry benchmarks"
                ]
            },
            "benchmark": {
                "greeting": "I'll compare your performance with industry peers.",
                "actions": [
                    "Benchmark against industry average",
                    "Peer group analysis",
                    "Regional comparison"
                ]
            },
            "csv": {
                "greeting": "I'll help you upload and process CSV data.",
                "actions": [
                    "Validate CSV format",
                    "Parse and extract emissions data",
                    "Ready for analysis"
                ]
            },
            "status": {
                "greeting": "Here's what I can tell you about your data.",
                "actions": []
            }
        }
    
    def detect_intent(self, user_message: str) -> ChatIntent:
        """
        Detect user intent from message
        
        Args:
            user_message: User's natural language input
        
        Returns:
            ChatIntent with detected intent and entities
        """
        message_lower = user_message.lower().strip()
        
        # Extract entities
        entities = self._extract_entities(message_lower)
        
        # Score each intent
        intent_scores = {}
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
            intent_scores[intent_type] = score
        
        # Find best match
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[best_intent] / max(sum(intent_scores.values()), 1)
        
        # If no clear intent, default to help
        if confidence < 0.3:
            best_intent = "help"
            confidence = 0.3
        
        # Determine relevant services
        relevant_services = self._get_relevant_services(best_intent, entities)
        
        return ChatIntent(
            intent_type=best_intent,
            confidence=min(confidence, 1.0),
            entities=entities,
            relevant_services=relevant_services
        )
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract relevant entities from message"""
        entities = {}
        
        # Look for months
        months = re.findall(r'\d+\s*months?|\d+-month', message)
        if months:
            entities['months'] = months[0]
        
        # Look for percentages/reductions
        percentages = re.findall(r'(\d+)%', message)
        if percentages:
            entities['percentages'] = [int(p) for p in percentages]
        
        # Look for facilities/companies
        if 'facility' in message or 'facility' in message:
            entities['scope'] = 'facility'
        elif 'company' in message or 'organization' in message:
            entities['scope'] = 'organization'
        elif 'regional' in message or 'region' in message:
            entities['scope'] = 'regional'
        
        # Look for data source
        if 'historical' in message or 'past' in message:
            entities['data_type'] = 'historical'
        elif 'current' in message or 'recent' in message:
            entities['data_type'] = 'current'
        
        return entities
    
    def _get_relevant_services(self, intent: str, entities: Dict) -> List[str]:
        """Determine which services are relevant for this intent"""
        service_mapping = {
            "forecast": ["lstm_service", "benchmark_service"],
            "anomaly": ["anomaly_service", "esg_service"],
            "simulation": ["simulation_service", "lstm_service"],
            "esg": ["esg_service", "benchmark_service"],
            "benchmark": ["benchmark_service", "esg_service"],
            "csv": ["csv_service", "lstm_service"],
            "status": ["all_services"],
            "help": ["help_service"]
        }
        
        return service_mapping.get(intent, [])
    
    def generate_response(
        self,
        intent: ChatIntent,
        analysis_results: Optional[Dict[str, Any]] = None,
        db: Session = None
    ) -> ChatResponse:
        """
        Generate conversational response based on intent
        
        Args:
            intent: Detected user intent
            analysis_results: Results from service calls (optional)
        
        Returns:
            ChatResponse with message and suggestions
        """
        template = self.response_templates.get(intent.intent_type, {})
        greeting = template.get("greeting", "How can I help?")
        actions = template.get("actions", [])
        
        # Build message
        message = greeting
        
        if analysis_results:
            message += self._format_analysis_results(
                intent.intent_type,
                analysis_results
            )
        
        # Generate suggestions
        suggestions = self._generate_suggestions(intent)
        
        # Prepare service calls
        service_calls = self._prepare_service_calls(intent)
        
        response = ChatResponse(
            message=message,
            intent=intent.intent_type,
            suggestions=suggestions,
            service_calls=service_calls,
            confidence=intent.confidence
        )
        
        # Store conversation in database if session provided
        if db:
            self._store_conversation_turn(db, message, intent, response)
        
        return response
    
    def _format_analysis_results(
        self,
        intent_type: str,
        results: Dict[str, Any]
    ) -> str:
        """Format analysis results for display"""
        
        if intent_type == "forecast":
            return self._format_forecast(results)
        elif intent_type == "anomaly":
            return self._format_anomaly(results)
        elif intent_type == "simulation":
            return self._format_simulation(results)
        elif intent_type == "esg":
            return self._format_esg(results)
        elif intent_type == "benchmark":
            return self._format_benchmark(results)
        else:
            return ""
    
    def _format_forecast(self, results: Dict) -> str:
        """Format forecast results"""
        if not results or 'forecast' not in results:
            return ""
        
        forecast = results['forecast']
        if not forecast:
            return ""
        
        final = forecast[-1] if forecast else None
        if not final:
            return ""
        
        accuracy = results.get('accuracy_score', 'N/A')
        
        return f"\n\n📊 **Forecast Results:**\n" \
               f"- Final month projection: {final.get('predicted_co2', 'N/A')} kg\n" \
               f"- Confidence: {accuracy}\n" \
               f"- Trend: {final.get('trend', 'stable')}"
    
    def _format_anomaly(self, results: Dict) -> str:
        """Format anomaly detection results"""
        if not results:
            return ""
        
        anomalies = results.get('anomalies', [])
        count = len([a for a in anomalies if a.get('is_anomaly')])
        health = results.get('health_status', 'Unknown')
        
        return f"\n\n🚨 **Anomaly Analysis:**\n" \
               f"- Anomalies detected: {count}\n" \
               f"- System health: {health}\n" \
               f"- Recommendation: {results.get('recommendations', ['Monitor trends'])[0] if results.get('recommendations') else 'Monitor trends'}"
    
    def _format_simulation(self, results: Dict) -> str:
        """Format simulation results"""
        if not results or 'risk_metrics' not in results:
            return ""
        
        risk = results['risk_metrics']
        
        return f"\n\n🎲 **Risk Analysis:**\n" \
               f"- Value at Risk (95%): {risk.get('value_at_risk_95', 'N/A')} kg\n" \
               f"- Risk Level: {risk.get('risk_level', 'Unknown')}\n" \
               f"- Volatility (Std Dev): {results.get('aggregated_results', [{}])[-1].get('std_dev', 'N/A')}"
    
    def _format_esg(self, results: Dict) -> str:
        """Format ESG results"""
        if not results or 'esg_data' not in results:
            return ""
        
        esg = results['esg_data']
        
        return f"\n\n🌍 **ESG Score:**\n" \
               f"- Environmental: {esg.get('environmental_score', 'N/A')}/100\n" \
               f"- Social: {esg.get('social_score', 'N/A')}/100\n" \
               f"- Governance: {esg.get('governance_score', 'N/A')}/100\n" \
               f"- Overall: {esg.get('overall_score', 'N/A')} ({esg.get('grade', 'N/A')})"
    
    def _format_benchmark(self, results: Dict) -> str:
        """Format benchmark results"""
        if not results or 'benchmark_data' not in results:
            return ""
        
        bench = results['benchmark_data']
        
        return f"\n\n📈 **Benchmark Comparison:**\n" \
               f"- Your value: {bench.get('your_value', 'N/A')}\n" \
               f"- Industry average: {bench.get('industry_average', 'N/A')}\n" \
               f"- Percentile: {bench.get('industry_percentile', 'N/A')}th\n" \
               f"- Performance: {bench.get('performance_rating', 'N/A')}"
    
    def _generate_suggestions(self, intent: ChatIntent) -> List[str]:
        """Generate follow-up suggestions"""
        suggestions = []
        
        # Service-specific suggestions
        if intent.intent_type == "forecast":
            suggestions = [
                "💡 Run a scenario analysis with 25% reduction goal",
                "🔄 Compare with ensemble forecast",
                "📊 Generate Monte Carlo simulation for risk"
            ]
        elif intent.intent_type == "anomaly":
            suggestions = [
                "🔍 Investigate anomalies in more detail",
                "🎯 Set alerts for future anomalies",
                "⚠️ Check environmental controls"
            ]
        elif intent.intent_type == "simulation":
            suggestions = [
                "🎲 Run scenario with different volatility",
                "📉 Test reduction initiatives",
                "💰 Calculate cost Impact of scenarios"
            ]
        elif intent.intent_type == "esg":
            suggestions = [
                "🏆 Compare with peer group",
                "📋 View detailed breakdown",
                "🎯 Set ESG improvement targets"
            ]
        elif intent.intent_type == "benchmark":
            suggestions = [
                "🌍 Benchmark by region",
                "🏭 Compare with similar industries",
                "📊 Analyze gap to best-in-class"
            ]
        elif intent.intent_type == "csv":
            suggestions = [
                "📂 Validate CSV format",
                "📊 Preview data before import",
                "✅ Import and analyze"
            ]
        
        return suggestions
    
    def _prepare_service_calls(self, intent: ChatIntent) -> List[Dict[str, Any]]:
        """Prepare service calls based on intent"""
        calls = []
        
        service_mapping = {
            "forecast": {
                "service": "lstm_service",
                "endpoints": ["/api/v2/forecast/lstm", "/api/v2/forecast/ensemble"]
            },
            "anomaly": {
                "service": "anomaly_service",
                "endpoints": ["/api/v2/anomaly/detect", "/api/v2/anomaly/summary"]
            },
            "simulation": {
                "service": "simulation_service",
                "endpoints": ["/api/v2/simulation/run-monte-carlo"]
            },
            "esg": {
                "service": "esg_service",
                "endpoints": ["/api/v2/esg-score"]
            },
            "benchmark": {
                "service": "benchmark_service",
                "endpoints": ["/api/v2/benchmark", "/api/v2/benchmark/peer-group"]
            },
            "csv": {
                "service": "csv_service",
                "endpoints": ["/api/v2/csv/validate", "/api/v2/csv/import"]
            }
        }
        
        if intent.intent_type in service_mapping:
            mapping = service_mapping[intent.intent_type]
            calls.append({
                "service": mapping["service"],
                "endpoints": mapping["endpoints"],
                "priority": "high"
            })
        
        return calls
    
    def add_to_history(self, message: str, sender: str):
        """Add message to conversation history"""
        timestamp = datetime.now().isoformat()
        self.conversation_history.append(
            ChatMessage(
                content=message,
                timestamp=timestamp,
                sender=sender
            )
        )
        
        # Keep history size manageable
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get current conversation context"""
        return {
            "conversation_length": len(self.conversation_history),
            "last_intent": self.current_context.get("last_intent"),
            "data_source": self.current_context.get("data_source"),
            "analysis_type": self.current_context.get("analysis_type")
        }
    
    def reset_context(self):
        """Reset conversation context"""
        self.conversation_history = []
        self.current_context = {}


class ConversationManager:
    """Manage multiple conversations (future: multi-user support)"""
    
    def __init__(self):
        self.conversations = {}
        self.active_conversation = None
    
    def create_conversation(self, conversation_id: str) -> AIConversationService:
        """Create new conversation"""
        service = AIConversationService()
        self.conversations[conversation_id] = service
        self.active_conversation = conversation_id
        return service
    
    def get_conversation(self, conversation_id: str) -> Optional[AIConversationService]:
        """Get existing conversation"""
        return self.conversations.get(conversation_id)
    
    def delete_conversation(self, conversation_id: str):
        """Delete conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            if self.active_conversation == conversation_id:
                self.active_conversation = None
    
    def _store_conversation_turn(
        self, 
        db: Session, 
        message: str, 
        intent: ChatIntent, 
        response: ChatResponse
    ) -> None:
        """Store conversation turn in database"""
        try:
            from services.database_service import DatabaseService
            
            # Store interaction metadata
            conversation_data = {
                "timestamp": datetime.now().isoformat(),
                "intent_type": intent.intent_type,
                "intent_confidence": intent.confidence,
                "entities": intent.entities,
                "relevant_services": intent.relevant_services,
                "response_confidence": response.confidence,
                "suggestions": response.suggestions
            }
            
            # For now, store as a report to track conversations
            DatabaseService.store_report(
                db=db,
                report_type="chatbot_conversation",
                report_content=conversation_data,
                period_start=datetime.now().isoformat(),
                period_end=datetime.now().isoformat()
            )
        except Exception as e:
            print(f"Database storage error in chatbot conversation: {str(e)}")
