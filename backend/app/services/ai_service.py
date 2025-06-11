from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import StrOutputParser 
from langchain_core.runnables import RunnablePassthrough 
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, date, timezone 
import logging

from utils.llms import model 
from models import OwnershipChangeType, VehicleStatusType, InsuranceClaimType


logger = logging.getLogger(__name__)

class VehicleInsightsOutputParser(StrOutputParser): 
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
    def __init__(self):
        self.model = model 
        self.output_parser = VehicleInsightsOutputParser()
        self._setup_chain() 
    
    def _setup_chain(self):
        prompt_template_str = """
You are an expert automotive consultant analyzing THIS SPECIFIC VEHICLE'S actual history and data. 
Your job is to tell the owner what has actually happened to THEIR car and what it means for them.

FOCUS ON THE ACTUAL DATA - don't give generic advice, but specific insights based on what this car has actually experienced.

VEHICLE INFORMATION:
{vehicle_data}

VALUATION DATA:
{valuation_data}

VEHICLE HISTORY (MOT, Service, etc.):
{history_data}

RECALL INFORMATION:
{recall_data}

TECHNICAL SPECIFICATIONS:
{specification_data}

OWNERSHIP HISTORY:
{ownership_history_data}

THEFT RECORDS:
{theft_data}

INSURANCE CLAIMS:
{insurance_data}

MILEAGE RECORDS (often corroborates MOT/Service):
{mileage_history_data}

FINANCE RECORDS:
{finance_data}

AUCTION RECORDS:
{auction_data}

CRITICAL INSTRUCTIONS:
- Base your analysis on the ACTUAL data provided, not generic knowledge about this car model.
- Reference specific dates, mileage readings, recall numbers, actual events, financial details, theft statuses, and ownership changes.
- If there are MOT records, mention what actually happened (pass/fail/advisories) and when.
- If there are recalls, explain what was actually done and when, and what's still outstanding.
- If there are valuation records, reference the actual values and how they've changed.
- If there is ownership history, comment on the number of owners and types of ownership changes.
- If there are theft records, clearly state the status (e.g., stolen, recovered).
- If there are insurance claims, note the type, fault, and if it was a total loss.
- If there are finance records, indicate if finance is outstanding and the type.
- If there are auction records, mention if sold and the price relative to guide.
- Use specific mileage figures, dates, and events from all provided history sections.
- Make connections between different data points (e.g., how mileage relates to value changes, how an insurance claim might relate to an MOT advisory).

Provide your analysis *strictly* in the following JSON format. Do not add any text before or after the JSON object.

{{
    "summary": "A detailed analysis of THIS SPECIFIC VEHICLE based on its actual history, focusing on what has actually happened to it. Reference specific events, dates, mileage, recalls, ownership changes, finance status, theft incidents, and insurance claims from the data. Make it conversational but data-driven in 2-3 paragraphs. Highlight any major events like theft, total loss claims, or outstanding finance.",
    "key_insights": [
        "List 4-5 key insights about what this SPECIFIC vehicle has been through. Reference actual dates, mileage, MOT results, recall completions, service history, ownership changes, theft incidents (with status), insurance claims (total loss, fault), finance status (outstanding, type), auction results. Focus on practical aspects like reliability, maintenance, costs, performance, security, and financial encumbrances. Each insight should be based on the actual data provided."
    ],
    "owner_advice": "Specific advice based on what this car has actually experienced - reference the actual MOT history, completed/outstanding recalls, mileage patterns, service records, ownership history, finance (e.g. if outstanding, or coming to an end), theft history (e.g. security advice if stolen previously), insurance claim history (e.g. potential impact on future insurance).",
    "reliability_assessment": {{
        "score": "Rate 1-10 based on the ACTUAL history of this specific vehicle (MOT passes/fails, recalls completed, advisory notes, insurance claim patterns for non-cosmetic issues etc.).",
        "explanation": "Explain the score based on the actual events in this car's history, including MOTs, recalls, and frequent non-cosmetic insurance claims."
    }},
    "value_assessment": {{
        "current_market_position": "Based on the ACTUAL valuation data provided, how has this car's value changed over time? Reference specific figures and dates. Consider impact of finance status, theft history, total loss claims, and auction results if available.",
        "factors_affecting_value": "What factors from this car's ACTUAL history affect its value (mileage increases, condition grades, MOT history, recall status, ownership changes, finance outstanding, theft history, insurance total loss claims, auction sales data, etc.)."
    }},
    "attention_items": [
        "List specific items based on the actual data: exact MOT due dates, outstanding recall numbers with descriptions, specific advisory notes from MOT history, details of any outstanding finance (type, company), active theft status, upcoming finance agreement end dates. Be precise with dates, recall numbers, and descriptions."
    ],
    "cost_insights": {{
        "typical_maintenance": "Based on this car's actual service history and MOT records, what maintenance patterns are evident? Mention any finance payments if data is available.",
        "insurance_notes": "Reference the actual insurance group from the data. Comment on potential implications based on the car's specific features, history, theft records, and past claims.",
        "fuel_efficiency": "Use the actual CO2 emissions and fuel consumption figures from the data, not generic estimates."
    }}
}}

EXAMPLES OF GOOD DATA-SPECIFIC INSIGHTS:
- "Your car passed its MOT on [actual date] at [actual mileage] with only minor advisories about [specific advisory notes]."
- "The recall [actual recall number] for [actual issue] was completed on [actual date]."
- "This vehicle has outstanding finance with [Finance Company] of type [Finance Type], which started on [Date]."
- "A theft was reported on [Date]; the vehicle status is currently [Stolen/Recovered]."
- "An insurance claim for [Claim Type] was made on [Date], noted as [Fault/Non-Fault] and [was/was not] a total loss."
- "The vehicle was sold at auction on [Date] for £[Hammer Price] by [Auction House]."
- "There have been [Number] previous owners; the last change was from [Previous Owner Type] to [New Owner Type] on [Date]."

AVOID GENERIC STATEMENTS LIKE:
- "Peugeot 508s are generally reliable" (talk about THIS car's reliability based on its history).
- "Sports cars typically have higher insurance" (use the actual insurance group and claim history).
"""
        self.prompt = ChatPromptTemplate.from_template(prompt_template_str)
        self.chain = self.prompt | self.model | self.output_parser
    
    def generate_vehicle_insights(self, vehicle_data_dict: Dict[str, Any]) -> Dict[str, Any]:
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
        
        def format_section(data_item: Optional[Any], title: str) -> str:
            if data_item is None or (isinstance(data_item, list) and not data_item):
                return f"{title}: No data available"
            
            if isinstance(data_item, list): 
                formatted_items = []
                for i, item in enumerate(data_item):
                    if isinstance(item, dict):
                        item_str = self._dict_to_readable_string(item)
                        formatted_items.append(f"Record {i+1}: {item_str}")
                
                if not formatted_items:
                     return f"{title}: No records found or data in unexpected format"
                return f"{title}:\n" + "\n".join(formatted_items)
            elif isinstance(data_item, dict): 
                return f"{title}:\n{self._dict_to_readable_string(data_item)}"
            else:
                return f"{title}: Data in unexpected format ({type(data_item)})"

        basic_info = vehicle_data_from_service.get('basic', {})
        history_records = vehicle_data_from_service.get('history', [])
        recall_records = vehicle_data_from_service.get('recalls', [])
        valuation_records = vehicle_data_from_service.get('valuations', [])
        ownership_records = vehicle_data_from_service.get('ownership_history', [])
        theft_records = vehicle_data_from_service.get('theft_records', [])
        insurance_records = vehicle_data_from_service.get('insurance_claims', [])
        mileage_records = vehicle_data_from_service.get('mileage_records', [])
        finance_records = vehicle_data_from_service.get('finance_records', [])
        auction_records = vehicle_data_from_service.get('auction_records', [])

        latest_mileage_record = max(mileage_records, key=lambda x: x.get('reading_date', date.min), default={})
        latest_mot_mileage = max([h.get('mileage', 0) for h in history_records if h.get('event_type', '').lower() == 'mot'], default=0)
        current_mileage = latest_mileage_record.get('mileage', latest_mot_mileage) or 'Unknown'

        outstanding_finance_info = "No"
        if finance_records:
            outstanding = [f for f in finance_records if f.get('outstanding_finance')]
            if outstanding:
                outstanding_finance_info = f"Yes, {len(outstanding)} record(s) indicate outstanding finance. Last type: {outstanding[-1].get('finance_type', 'N/A')} with {outstanding[-1].get('finance_company', 'N/A')}"

        theft_status_info = "No theft records"
        if theft_records:
            latest_theft = theft_records[-1] # Assuming sorted by date
            theft_status_info = f"Theft reported on {latest_theft.get('theft_date')}, current status: {latest_theft.get('current_status', 'Unknown')}"
            if latest_theft.get('recovery_date'):
                theft_status_info += f", recovered on {latest_theft.get('recovery_date')}"


        context_summary = f"""
VEHICLE CONTEXT SUMMARY:
- Vehicle: {basic_info.get('year', 'Unknown')} {basic_info.get('make', 'Unknown')} {basic_info.get('model', 'Unknown')}
- Current Mileage: {current_mileage} miles
- MOT Status: {basic_info.get('mot_status', 'Unknown')} (Expires: {basic_info.get('mot_expiry_date', 'Unknown')})
- Tax Status: {basic_info.get('tax_status', 'Unknown')} (Due: {basic_info.get('tax_due_date', 'Unknown')})
- Total History Records (MOT/Service): {len(history_records)}
- Total Recalls: {len(recall_records)} ({len([r for r in recall_records if r.get('recall_status') == 'Completed'])} completed)
- Valuation Records: {len(valuation_records)}
- Ownership Changes: {len(ownership_records)}
- Theft Incidents: {len(theft_records)} ({theft_status_info})
- Insurance Claims: {len(insurance_records)}
- Finance Records: {len(finance_records)} (Outstanding Finance: {outstanding_finance_info})
- Auction Records: {len(auction_records)}
        """

        return {
            "vehicle_data": context_summary + "\n" + format_section(basic_info, "Basic Vehicle Information"),
            "valuation_data": format_section(valuation_records, "Valuation History"),
            "history_data": format_section(history_records, "Vehicle History & MOT Records"),
            "recall_data": format_section(recall_records, "Recall Information"),
            "specification_data": format_section(vehicle_data_from_service.get('specifications'), "Technical Specifications"),
            "ownership_history_data": format_section(ownership_records, "Ownership History"),
            "theft_data": format_section(theft_records, "Theft Records"),
            "insurance_data": format_section(insurance_records, "Insurance Claims"),
            "mileage_history_data": format_section(mileage_records, "Mileage History"),
            "finance_data": format_section(finance_records, "Finance Records"),
            "auction_data": format_section(auction_records, "Auction Records")
        }
    
    def _dict_to_readable_string(self, data_dict: Dict[str, Any]) -> str:
        if not data_dict:
            return "No information available for this item."
        
        priority_fields = {
            'event_date', 'recall_date', 'valuation_date', 'change_date', 'theft_date', 'claim_date', 'reading_date', 'finance_start_date', 'auction_date',
            'event_type', 'recall_title', 'change_type', 'current_status', 'claim_type', 'finance_type', 'sold',
            'pass_fail', 'recall_status', 'outstanding_finance', 'total_loss',
            'mileage', 'mileage_at_change', 'mileage_at_incident', 'mileage_at_valuation', 'mileage_at_auction',
            'retail_value', 'hammer_price', 'claim_amount', 'settlement_amount', 'sale_price',
            'safety_issue', 'fault_claim', 'discrepancy_flag',
            'completion_date', 'recovery_date', 'settlement_date', 'finance_end_date',
            'advisory_notes', 'recall_description', 'theft_circumstances', 'description',
            'condition_grade', 'recovery_condition',
            'previous_owner_type', 'new_owner_type', 'seller_type',
            'finance_company', 'insurer', 'auction_house',
            'source'
        }
        
        important_parts = []
        other_parts = []
        
        for key, value in data_dict.items():
            if value is not None and str(value).strip() != "": 
                readable_key = key.replace('_', ' ').title()
                
                if isinstance(value, (date, datetime)):
                    value_str = value.strftime('%Y-%m-%d')
                elif isinstance(value, (OwnershipChangeType, VehicleStatusType, InsuranceClaimType)):
                    value_str = value.value
                else:
                    value_str = str(value) 
                
                field_info = f"{readable_key}: {value_str}"
                
                if key in priority_fields:
                    important_parts.append(field_info)
                else:
                    other_parts.append(field_info)
        
        all_parts = important_parts + other_parts
        return " | ".join(all_parts) if all_parts else "Item details not available."
    
    def _get_fallback_insights(self, vehicle_data_dict: Dict[str, Any]) -> Dict[str, Any]:
        basic_info = vehicle_data_dict.get('basic', {}) 
        
        return {
            "summary": f"This is a {basic_info.get('year', 'Unknown year')} {basic_info.get('make', 'Unknown make')} {basic_info.get('model', 'Unknown model')}. " +
                      "We encountered an issue generating detailed AI insights at this time. Basic vehicle data is still available.",
            "key_insights": [
                "Vehicle information was retrieved from records.",
                "Detailed AI-powered analysis is temporarily unavailable.",
                "Please refer to the 'detailed_data' section for raw vehicle information."
            ],
            "owner_advice": "Consult the detailed vehicle data sections for specific information regarding your vehicle including ownership, finance, theft, and insurance. For AI insights, please try again later.",
            "reliability_assessment": {
                "score": "N/A",
                "explanation": "AI reliability assessment is currently unavailable."
            },
            "value_assessment": {
                "current_market_position": "AI value assessment is currently unavailable. See 'detailed_data' for any valuation records.",
                "factors_affecting_value": "Standard factors like age, mileage, condition, service history, ownership, finance, theft and claims typically affect value."
            },
            "attention_items": ["Check 'detailed_data' for MOT/Tax due dates and any recall, finance, or theft information."],
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
        basic_info = vehicle_data_dict.get('basic', {})
        history_records = vehicle_data_dict.get('history', [])
        mileage_records = vehicle_data_dict.get('mileage_records', [])
        finance_records = vehicle_data_dict.get('finance_records', [])
        theft_records = vehicle_data_dict.get('theft_records', [])
        insurance_claims = vehicle_data_dict.get('insurance_claims', [])
        auction_records = vehicle_data_dict.get('auction_records', [])
        ownership_history = vehicle_data_dict.get('ownership_history', [])
        
        latest_mileage = None
        if mileage_records:
            latest_mileage_record = max(mileage_records, key=lambda x: x.get('reading_date', date.min), default={})
            latest_mileage = latest_mileage_record.get('mileage')
        elif history_records:
            latest_history_mileage = max([h.get('mileage') for h in history_records if h.get('mileage') is not None], default=None)
            latest_mileage = latest_history_mileage

        hash_input = {
            'basic': {
                'vin': basic_info.get('vin'),
                'vrm': basic_info.get('vrm'),
                'year': basic_info.get('year'),
                'mileage': latest_mileage, 
                'mot_status': basic_info.get('mot_status'),
                'mot_expiry_date': str(basic_info.get('mot_expiry_date')),
                'vehicle_status': basic_info.get('vehicle_status'),
            },
            'history_count': len(history_records),
            'valuations_count': len(vehicle_data_dict.get('valuations', [])),
            'recalls_count': len(vehicle_data_dict.get('recalls', [])),
            'last_recall_status': vehicle_data_dict.get('recalls', [{}])[-1].get('recall_status') if vehicle_data_dict.get('recalls') else None,
            'ownership_changes_count': len(ownership_history),
            'theft_records_count': len(theft_records),
            'last_theft_status': theft_records[-1].get('current_status') if theft_records else None,
            'insurance_claims_count': len(insurance_claims),
            'last_claim_total_loss': insurance_claims[-1].get('total_loss') if insurance_claims else None,
            'mileage_records_count': len(mileage_records),
            'finance_records_count': len(finance_records),
            'last_finance_outstanding': finance_records[-1].get('outstanding_finance') if finance_records else None,
            'auction_records_count': len(auction_records),
            'last_auction_sold': auction_records[-1].get('sold') if auction_records else None,
            'db_updated_at': str(basic_info.get('updated_at')) 
        }
        
        serialized_hash_input = json.dumps(hash_input, sort_keys=True, default=str).encode('utf-8')
        return hashlib.sha256(serialized_hash_input).hexdigest()
    
    def should_regenerate_insights(self, cached_summary_model: Any, current_vehicle_data_dict: Dict[str, Any]) -> bool:
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
        if cache_age.days > 30: # Consider reducing this if data changes frequently
            logger.info(f"Cached insights are older than 30 days ({cache_age.days} days). Regeneration needed.")
            return True
        
        logger.info("Cached insights are fresh and data hash matches. No regeneration needed.")
        return False