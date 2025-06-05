from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import StrOutputParser 
from langchain_core.runnables import RunnablePassthrough 
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, date, timezone 
import logging

from utils.llms import model 

logger = logging.getLogger(__name__)

class VehicleInsightsOutputParser(StrOutputParser): 
    """Custom output parser for structured vehicle insights.
    If LLM returns a parsable JSON string, it loads it. Otherwise, provides a fallback structure.
    """
    
    def parse(self, text: str) -> Dict[str, Any]:
        try:
            
            clean_text = text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            
            return json.loads(clean_text.strip())
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM output as JSON: {e}. Output: '{text[:500]}...'")
            
            return {
                "summary": "Error: AI could not generate a structured summary. The raw output was: " + text,
                "key_insights": [],
                "owner_advice": "",
                "reliability_assessment": {"score": "N/A", "explanation": "Data parsing error"},
                "value_assessment": {"current_market_position": "N/A", "factors_affecting_value": "Data parsing error"},
                "attention_items": ["Data parsing error"],
                "cost_insights": {"typical_maintenance": "N/A", "insurance_notes": "N/A", "fuel_efficiency": "N/A"},
                "technical_highlights": [],
                "error_parsing": True 
            }

class VehicleAIService:
    """Service for generating AI-powered vehicle insights and summaries using Langchain Expression Language."""
    
    def __init__(self):
        self.model = model 
        self.output_parser = VehicleInsightsOutputParser()
        self._setup_chain() 
    
    def _setup_chain(self):
        
        prompt_template_str = """
You are an expert automotive consultant helping a car owner understand their vehicle better. 
Your role is to translate technical automotive data into clear, actionable insights for someone 
who may not have extensive car knowledge.

VEHICLE INFORMATION:
{vehicle_data}

VALUATION DATA:
{valuation_data}

VEHICLE HISTORY:
{history_data}

RECALL INFORMATION:
{recall_data}

TECHNICAL SPECIFICATIONS:
{specification_data}

Please provide a comprehensive yet easy-to-understand analysis *strictly* in the following JSON format.
Do not add any text before or after the JSON object.

{{
    "summary": "A friendly, conversational summary of the vehicle in 2-3 paragraphs that a non-technical person can easily understand.",
    "key_insights": [
        "List 4-6 key points about this vehicle that the owner should know. Focus on practical aspects like reliability, maintenance, costs, performance."
    ],
    "owner_advice": "Personalized advice for the current owner about maintaining, using, or understanding their vehicle.",
    "reliability_assessment": {{
        "score": "Rate 1-10 based on history and known issues. Use 'N/A' if not determinable.",
        "explanation": "Brief explanation of the reliability rating."
    }},
    "value_assessment": {{
        "current_market_position": "Whether the vehicle holds value well, depreciates quickly, etc.",
        "factors_affecting_value": "Key factors that impact this vehicle's value."
    }},
    "attention_items": [
        "List any immediate or upcoming items that need attention (e.g., 'MOT due by YYYY-MM-DD', 'Outstanding safety recall XXXXX', 'Common issue: Check XYZ'). Be specific."
    ],
    "cost_insights": {{
        "typical_maintenance": "What to expect for maintenance costs (e.g., 'Average', 'Higher than average for its class').",
        "insurance_notes": "Notes about insurance costs/group (e.g., 'Insurance group X, typically moderate.').",
        "fuel_efficiency": "Practical fuel economy information (e.g., 'Expect around XX MPG combined. Good for city driving.')."
    }},
    "technical_highlights": [
        "List 2-3 key technical features explained in simple terms (e.g., ' turbocharged engine for good acceleration', ' advanced safety system with automatic braking')."
    ]
}}

GUIDELINES:
- Use friendly, conversational language.
- Avoid jargon or explain technical terms simply.
- Focus on practical implications.
- Be honest but constructive about issues.
- Provide actionable advice.
- Consider vehicle's age, mileage, and condition.
- Highlight safety recalls or critical issues prominently in 'attention_items' and 'summary'.
- This is for a vehicle owner, not a buyer.
- Ensure the entire output is a single, valid JSON object.
"""
        self.prompt = ChatPromptTemplate.from_template(prompt_template_str)
        
        self.chain = self.prompt | self.model | self.output_parser
    
    def generate_vehicle_insights(self, vehicle_data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive AI insights for a vehicle.
        
        Args:
            vehicle_data_dict: Complete vehicle data including all related information,
                               as structured by VehicleService._vehicle_to_dict.
                               
        Returns:
            Dictionary containing AI-generated insights.
        """
        try:
            formatted_prompt_inputs = self._format_data_for_prompt(vehicle_data_dict)
            
            logger.info(f"Generating insights for vehicle: {vehicle_data_dict.get('basic', {}).get('vrm', 'Unknown VIN/VRM')}")
            
            ai_response_dict = self.chain.invoke(formatted_prompt_inputs)
            
            ai_response_dict['generated_at'] = datetime.now(timezone.utc).isoformat()
            ai_response_dict['model_version'] = self.model.azure_deployment if hasattr(self.model, 'azure_deployment') else 'azure-openai' 
            ai_response_dict['error'] = ai_response_dict.get('error_parsing', False) 

            return ai_response_dict
            
        except Exception as e:
            logger.error(f"Error generating vehicle insights: {str(e)}", exc_info=True)
            return self._get_fallback_insights(vehicle_data_dict) 
    
    def _format_data_for_prompt(self, vehicle_data_from_service: Dict[str, Any]) -> Dict[str, str]:
        """
        Format vehicle data (received from VehicleService._vehicle_to_dict) for the prompt template.
        The keys in the returned dictionary must match the input_variables of the prompt.
        """
        
        def format_section(data_item: Optional[Any], title: str) -> str:
            if data_item is None or (isinstance(data_item, list) and not data_item):
                return f"{title}: No data available"
            
            if isinstance(data_item, list): 
                formatted_items = [self._dict_to_readable_string(item) for item in data_item if isinstance(item, dict)]
                if not formatted_items:
                     return f"{title}: No records found or data in unexpected format"
                return f"{title}:\n" + "\n- ".join(formatted_items)
            elif isinstance(data_item, dict): 
                return f"{title}:\n{self._dict_to_readable_string(data_item)}"
            else:
                return f"{title}: Data in unexpected format"

        return {
            "vehicle_data": format_section(vehicle_data_from_service.get('basic'), "Basic Vehicle Information"),
            "valuation_data": format_section(vehicle_data_from_service.get('valuations'), "Valuation History"),
            "history_data": format_section(vehicle_data_from_service.get('history'), "Vehicle History"),
            "recall_data": format_section(vehicle_data_from_service.get('recalls'), "Recall Information"),
            "specification_data": format_section(vehicle_data_from_service.get('specifications'), "Technical Specifications")
        }
    
    def _dict_to_readable_string(self, data_dict: Dict[str, Any]) -> str:
        """Convert a single dictionary item to a human-readable string for the prompt."""
        if not data_dict:
            return "No information available for this item."
        
        readable_parts = []
        for key, value in data_dict.items():
            if value is not None and str(value).strip() != "": 
                readable_key = key.replace('_', ' ').title()
                
                if isinstance(value, (date, datetime)):
                    value_str = value.strftime('%Y-%m-%d')
                else:
                    value_str = str(value) 
                
                readable_parts.append(f"{readable_key}: {value_str}")
        
        return " | ".join(readable_parts) if readable_parts else "Item details not available."
    
    def _get_fallback_insights(self, vehicle_data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback insights when AI generation fails or encounters an error."""
        basic_info = vehicle_data_dict.get('basic', {}) 
        
        return {
            "summary": f"This is a {basic_info.get('year', 'Unknown year')} {basic_info.get('make', 'Unknown make')} {basic_info.get('model', 'Unknown model')}. " +
                      "We encountered an issue generating detailed AI insights at this time. Basic vehicle data is still available.",
            "key_insights": [
                "Vehicle information was retrieved from records.",
                "Detailed AI-powered analysis is temporarily unavailable.",
                "Please refer to the 'detailed_data' section for raw vehicle information."
            ],
            "owner_advice": "Consult the detailed vehicle data sections for specific information regarding your vehicle. For AI insights, please try again later.",
            "reliability_assessment": {
                "score": "N/A",
                "explanation": "AI reliability assessment is currently unavailable."
            },
            "value_assessment": {
                "current_market_position": "AI value assessment is currently unavailable. See 'detailed_data' for any valuation records.",
                "factors_affecting_value": "Standard factors like age, mileage, condition, and service history typically affect value."
            },
            "attention_items": ["Check 'detailed_data' for MOT/Tax due dates and any recall information."],
            "cost_insights": {
                "typical_maintenance": "AI cost insights are unavailable. Refer to service history in 'detailed_data'.",
                "insurance_notes": f"Insurance group: {basic_info.get('insurance_group', 'N/A')}. Check 'detailed_data'.",
                "fuel_efficiency": f"Fuel type: {basic_info.get('fuel_type', 'N/A')}. CO2 emissions: {basic_info.get('co2_emissions', 'N/A')} g/km. Check 'detailed_data'."
            },
            "technical_highlights": [
                f"Engine: {basic_info.get('engine_size', 'N/A')}L {basic_info.get('fuel_type', 'N/A')}",
                f"Transmission: {basic_info.get('transmission', 'N/A')}",
                f"Body Type: {basic_info.get('body_type', 'N/A')}"
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model_version": "fallback_system",
            "error": True 
        }
    
    def calculate_data_hash(self, vehicle_data_dict: Dict[str, Any]) -> str:
        """
        Calculate a SHA256 hash of key parts of the vehicle data to detect changes.
        The input vehicle_data_dict is expected to be the output from VehicleService._vehicle_to_dict.
        """
        hash_input = {
            'basic': {
                'vin': vehicle_data_dict.get('basic', {}).get('vin'),
                'vrm': vehicle_data_dict.get('basic', {}).get('vrm'),
                'year': vehicle_data_dict.get('basic', {}).get('year'),
                'mileage': vehicle_data_dict.get('history', [{}])[-1].get('mileage') if vehicle_data_dict.get('history') else None, 
                'mot_status': vehicle_data_dict.get('basic', {}).get('mot_status'),
                'mot_expiry_date': str(vehicle_data_dict.get('basic', {}).get('mot_expiry_date')),
            },
            'history_count': len(vehicle_data_dict.get('history', [])),
            'valuations_count': len(vehicle_data_dict.get('valuations', [])),
            'recalls_count': len(vehicle_data_dict.get('recalls', [])),
            'last_recall_status': vehicle_data_dict.get('recalls', [{}])[-1].get('recall_status') if vehicle_data_dict.get('recalls') else None,
            'db_updated_at': str(vehicle_data_dict.get('basic', {}).get('updated_at')) 
        }
        
        serialized_hash_input = json.dumps(hash_input, sort_keys=True, default=str).encode('utf-8')
        return hashlib.sha256(serialized_hash_input).hexdigest()
    
    def should_regenerate_insights(self, cached_summary_model: Any, current_vehicle_data_dict: Dict[str, Any]) -> bool:
        """
        Determine if insights should be regenerated.
        'cached_summary_model' is the SQLAlchemy model instance of VehicleAISummary.
        'current_vehicle_data_dict' is the fresh data from VehicleService._vehicle_to_dict.
        """
        if not cached_summary_model:
            logger.info("No cached summary found, regeneration needed.")
            return True
        
        if not hasattr(cached_summary_model, 'data_hash') or not hasattr(cached_summary_model, 'generated_at'):
            logger.info("Cached summary is missing 'data_hash' or 'generated_at', regeneration needed.")
            return True 

        current_data_hash = self.calculate_data_hash(current_vehicle_data_dict)
        cached_data_hash = cached_summary_model.data_hash
        
        if current_data_hash != cached_data_hash:
            logger.info(f"Data hash mismatch. Current: {current_data_hash}, Cached: {cached_data_hash}. Regeneration needed.")
            return True
        
        generated_at_utc = cached_summary_model.generated_at
        if generated_at_utc.tzinfo is None: 
            generated_at_utc = generated_at_utc.replace(tzinfo=timezone.utc)

        cache_age = datetime.now(timezone.utc) - generated_at_utc
        if cache_age.days > 30:
            logger.info(f"Cached insights are older than 30 days ({cache_age.days} days). Regeneration needed.")
            return True
        
        logger.info("Cached insights are fresh and data hash matches. No regeneration needed.")
        return False