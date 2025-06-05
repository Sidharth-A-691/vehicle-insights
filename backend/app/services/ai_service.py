from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import BaseOutputParser
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, date
import logging

from utils.llms import model  

logger = logging.getLogger(__name__)

class VehicleInsightsOutputParser(BaseOutputParser):
    """Custom output parser for structured vehicle insights"""
    
    def parse(self, text: str) -> Dict[str, Any]:
        try:
            # Try to parse as JSON first
            if text.strip().startswith('{'):
                return json.loads(text)
            
            # If not JSON, create structured response from text
            return {
                "summary": text,
                "key_insights": [],
                "owner_advice": "",
                "reliability_score": 0,
                "value_assessment": "",
                "attention_items": []
            }
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM output as JSON, returning text summary")
            return {
                "summary": text,
                "key_insights": [],
                "owner_advice": "",
                "reliability_score": 0,
                "value_assessment": "",
                "attention_items": []
            }

class VehicleAIService:
    """Service for generating AI-powered vehicle insights and summaries"""
    
    def __init__(self):
        self.model = model
        self.output_parser = VehicleInsightsOutputParser()
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Setup LangChain prompt templates"""
        
        self.summary_prompt = PromptTemplate(
            input_variables=[
                "vehicle_data", "valuation_data", "history_data", 
                "recall_data", "specification_data"
            ],
            template="""
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

Please provide a comprehensive yet easy-to-understand analysis in the following JSON format:

{{
    "summary": "A friendly, conversational summary of the vehicle in 2-3 paragraphs that a non-technical person can easily understand",
    "key_insights": [
        "List 4-6 key points about this vehicle that the owner should know",
        "Focus on practical aspects like reliability, maintenance, costs, performance"
    ],
    "owner_advice": "Personalized advice for the current owner about maintaining, using, or understanding their vehicle",
    "reliability_assessment": {{
        "score": "Rate 1-10 based on history and known issues",
        "explanation": "Brief explanation of the reliability rating"
    }},
    "value_assessment": {{
        "current_market_position": "Whether the vehicle holds value well, depreciates quickly, etc.",
        "factors_affecting_value": "Key factors that impact this vehicle's value"
    }},
    "attention_items": [
        "List any immediate or upcoming items that need attention (MOT due, recalls, common issues to watch for)"
    ],
    "cost_insights": {{
        "typical_maintenance": "What to expect for maintenance costs",
        "insurance_notes": "Notes about insurance costs/group",
        "fuel_efficiency": "Practical fuel economy information"
    }},
    "technical_highlights": [
        "2-3 key technical features explained in simple terms"
    ]
}}

GUIDELINES:
- Use friendly, conversational language that anyone can understand
- Avoid technical jargon - if you must use technical terms, explain them simply
- Focus on practical implications rather than technical specifications
- Be honest about any potential issues but remain constructive
- Provide actionable advice the owner can use
- Consider the vehicle's age, mileage, and condition in your assessment
- If there are any safety recalls or critical issues, highlight them prominently
- Make the summary helpful for someone who owns this specific vehicle

Remember: This is for someone who wants to understand THEIR car better, not someone looking to buy a car.
"""
        )
    
    def generate_vehicle_insights(self, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive AI insights for a vehicle
        
        Args:
            vehicle_data: Complete vehicle data including all related information
            
        Returns:
            Dictionary containing AI-generated insights and summary
        """
        try:
            # Prepare data for the prompt
            formatted_data = self._format_data_for_prompt(vehicle_data)
            
            # Create the chain
            chain = LLMChain(
                llm=self.model,
                prompt=self.summary_prompt,
                output_parser=self.output_parser
            )
            
            # Generate insights
            logger.info(f"Generating insights for vehicle: {vehicle_data.get('basic', {}).get('vrm', 'Unknown')}")
            
            result = chain.run(**formatted_data)
            
            # Ensure we have a proper structure
            if isinstance(result, str):
                result = self.output_parser.parse(result)
            
            # Add metadata
            result['generated_at'] = datetime.utcnow().isoformat()
            result['model_version'] = 'azure-openai-gpt-4'
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating vehicle insights: {str(e)}")
            return self._get_fallback_insights(vehicle_data)
    
    def _format_data_for_prompt(self, vehicle_data: Dict[str, Any]) -> Dict[str, str]:
        """Format vehicle data for the prompt template"""
        
        def format_section(data, title):
            if not data:
                return f"{title}: No data available"
            
            if isinstance(data, list):
                if not data:
                    return f"{title}: No records found"
                formatted_items = []
                for item in data:
                    formatted_items.append(self._dict_to_readable_string(item))
                return f"{title}:\n" + "\n".join(formatted_items)
            else:
                return f"{title}:\n{self._dict_to_readable_string(data)}"
        
        return {
            "vehicle_data": format_section(vehicle_data.get('basic', {}), "Basic Vehicle Information"),
            "valuation_data": format_section(vehicle_data.get('valuations', []), "Valuation History"),
            "history_data": format_section(vehicle_data.get('history', []), "Vehicle History"),
            "recall_data": format_section(vehicle_data.get('recalls', []), "Recall Information"),
            "specification_data": format_section(vehicle_data.get('specifications', {}), "Technical Specifications")
        }
    
    def _dict_to_readable_string(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to human-readable string"""
        if not data:
            return "No information available"
        
        readable_parts = []
        for key, value in data.items():
            if value is not None and value != "":
                # Convert snake_case to readable format
                readable_key = key.replace('_', ' ').title()
                
                # Format dates
                if isinstance(value, (date, datetime)):
                    value = value.strftime('%Y-%m-%d')
                
                readable_parts.append(f"{readable_key}: {value}")
        
        return " | ".join(readable_parts)
    
    def _get_fallback_insights(self, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback insights when AI generation fails"""
        basic_info = vehicle_data.get('basic', {})
        
        return {
            "summary": f"This is a {basic_info.get('year', 'Unknown')} {basic_info.get('make', 'Unknown')} {basic_info.get('model', 'Unknown')}. " +
                      "We encountered an issue generating detailed insights, but the basic vehicle information is available below.",
            "key_insights": [
                "Vehicle information has been retrieved from official records",
                "Detailed AI analysis is temporarily unavailable",
                "All technical data and history records are still accessible"
            ],
            "owner_advice": "Please refer to the detailed vehicle data below for specific information about your vehicle.",
            "reliability_assessment": {
                "score": "N/A",
                "explanation": "Unable to generate reliability assessment at this time"
            },
            "value_assessment": {
                "current_market_position": "Valuation data available in detailed information",
                "factors_affecting_value": "Age, mileage, condition, and service history"
            },
            "attention_items": ["Check detailed data for MOT and tax due dates"],
            "cost_insights": {
                "typical_maintenance": "Refer to service history for maintenance patterns",
                "insurance_notes": f"Insurance group: {basic_info.get('insurance_group', 'Not available')}",
                "fuel_efficiency": f"Fuel type: {basic_info.get('fuel_type', 'Not specified')}"
            },
            "technical_highlights": [
                f"Engine: {basic_info.get('engine_size', 'Unknown')}L {basic_info.get('fuel_type', 'Unknown')}",
                f"Transmission: {basic_info.get('transmission', 'Unknown')}",
                f"Body type: {basic_info.get('body_type', 'Unknown')}"
            ],
            "generated_at": datetime.utcnow().isoformat(),
            "model_version": "fallback",
            "error": True
        }
    
    def calculate_data_hash(self, vehicle_data: Dict[str, Any]) -> str:
        """Calculate hash of vehicle data to detect changes"""
        # Create a simplified version of the data for hashing
        hash_data = {
            'basic': vehicle_data.get('basic', {}),
            'history_count': len(vehicle_data.get('history', [])),
            'valuations_count': len(vehicle_data.get('valuations', [])),
            'recalls_count': len(vehicle_data.get('recalls', [])),
            'last_updated': vehicle_data.get('basic', {}).get('updated_at')
        }
        
        return hashlib.sha256(
            json.dumps(hash_data, sort_keys=True, default=str).encode()
        ).hexdigest()
    
    def should_regenerate_insights(self, cached_summary: Any, current_data: Dict[str, Any]) -> bool:
        """Determine if insights should be regenerated based on data changes"""
        if not cached_summary:
            return True
        
        # Check if data hash has changed
        current_hash = self.calculate_data_hash(current_data)
        cached_hash = getattr(cached_summary, 'data_hash', None)
        
        if current_hash != cached_hash:
            return True
        
        # Check if cached insights are older than 30 days
        if hasattr(cached_summary, 'generated_at'):
            cache_age = datetime.utcnow() - cached_summary.generated_at
            if cache_age.days > 30:
                return True
        
        return False