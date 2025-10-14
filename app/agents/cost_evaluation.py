"""
Cost Evaluation Agent for Renewable Energy Projects
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from enum import Enum

from app.agents.communication import BaseAgent, AgentMessage, MessagePriority
from app.core.logging import agent_logger

logger = logging.getLogger(__name__)

class ProjectPhase(Enum):
    """Project development phases"""
    DEVELOPMENT = "development"
    CONSTRUCTION = "construction"
    OPERATION = "operation"
    DECOMMISSIONING = "decommissioning"

class CostCategory(Enum):
    """Cost categories"""
    CAPITAL_EXPENDITURE = "capex"
    OPERATIONAL_EXPENDITURE = "opex"
    FINANCING_COSTS = "financing"
    REGULATORY_COSTS = "regulatory"
    INSURANCE_COSTS = "insurance"
    MAINTENANCE_COSTS = "maintenance"

@dataclass
class CostBreakdown:
    """Detailed cost breakdown"""
    category: CostCategory
    amount_usd: float
    percentage_of_total: float
    description: str
    phase: ProjectPhase
    recurring: bool = False

@dataclass
class FinancialMetrics:
    """Financial performance metrics"""
    net_present_value_usd: float
    internal_rate_of_return: float
    payback_period_years: float
    levelized_cost_of_energy_usd_mwh: float
    return_on_investment: float
    net_annual_cash_flow_usd: float

@dataclass
class ProjectEconomics:
    """Complete project economics analysis"""
    total_capex_usd: float
    total_opex_usd: float
    annual_revenue_usd: float
    net_annual_cash_flow_usd: float
    project_lifetime_years: int
    discount_rate: float
    cost_breakdown: List[CostBreakdown]
    financial_metrics: FinancialMetrics
    sensitivity_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]

class CostEvaluationAgent(BaseAgent):
    """Agent responsible for evaluating project costs and financial viability"""
    
    def __init__(self, communication_manager):
        super().__init__("cost_evaluation", communication_manager)
        
        # Define capabilities
        self.capabilities.add_capability("capex_estimation")
        self.capabilities.add_capability("opex_estimation")
        self.capabilities.add_capability("financial_modeling")
        self.capabilities.add_capability("sensitivity_analysis")
        self.capabilities.add_capability("risk_assessment")
        
        # Register message handlers
        self.register_handler("evaluate_project_costs", self._handle_evaluate_costs)
        self.register_handler("calculate_financial_metrics", self._handle_calculate_metrics)
        self.register_handler("perform_sensitivity_analysis", self._handle_sensitivity_analysis)
        self.register_handler("assess_project_risks", self._handle_risk_assessment)
        self.register_handler("compare_project_options", self._handle_compare_options)
        
        # Cost databases (in real implementation, these would be external databases)
        self.solar_costs = {
            "panel_cost_per_w": 0.5,
            "inverter_cost_per_w": 0.15,
            "mounting_cost_per_w": 0.10,
            "installation_cost_per_w": 0.25,
            "grid_connection_cost_per_mw": 50000,
            "permitting_cost_per_mw": 10000,
            "engineering_cost_per_mw": 15000
        }
        
        self.wind_costs = {
            "turbine_cost_per_mw": 1200000,
            "foundation_cost_per_mw": 200000,
            "electrical_cost_per_mw": 150000,
            "installation_cost_per_mw": 200000,
            "grid_connection_cost_per_mw": 100000,
            "permitting_cost_per_mw": 50000,
            "engineering_cost_per_mw": 75000
        }
        
        self.hydro_costs = {
            "turbine_cost_per_mw": 2000000,
            "civil_works_cost_per_mw": 3000000,
            "electrical_cost_per_mw": 300000,
            "installation_cost_per_mw": 500000,
            "grid_connection_cost_per_mw": 150000,
            "permitting_cost_per_mw": 100000,
            "engineering_cost_per_mw": 200000
        }
    
    async def evaluate_project_costs(self, project_data: Dict[str, Any]) -> ProjectEconomics:
        """Evaluate comprehensive project costs and economics"""
        try:
            project_type = project_data.get("project_type", "solar")
            capacity_mw = project_data.get("capacity_mw", 100)
            location_data = project_data.get("location", {})
            resource_data = project_data.get("resource_data", {})
            financial_params = project_data.get("financial_params", {})
            
            # Calculate CAPEX
            capex_breakdown = await self._calculate_capex(project_type, capacity_mw, location_data)
            total_capex = sum(cost.amount_usd for cost in capex_breakdown)
            
            # Calculate OPEX
            opex_breakdown = await self._calculate_opex(project_type, capacity_mw, resource_data)
            total_opex = sum(cost.amount_usd for cost in opex_breakdown)
            
            # Calculate annual revenue
            annual_revenue = await self._calculate_annual_revenue(
                project_type, capacity_mw, resource_data, financial_params
            )
            
            # Calculate financial metrics
            financial_metrics = await self._calculate_financial_metrics(
                total_capex, total_opex, annual_revenue, financial_params
            )
            
            # Perform sensitivity analysis
            sensitivity_analysis = await self._perform_sensitivity_analysis(
                project_type, capacity_mw, financial_params
            )
            
            # Assess project risks
            risk_assessment = await self._assess_project_risks(
                project_type, location_data, resource_data, financial_params
            )
            
            # Calculate net annual cash flow
            net_annual_cash_flow = annual_revenue - total_opex
            
            # Log decision
            agent_logger.log_agent_decision(
                self.agent_id,
                f"Project cost evaluation completed for {project_type} project",
                f"NPV: ${financial_metrics.net_present_value_usd:,.0f}, IRR: {financial_metrics.internal_rate_of_return:.1%}"
            )
            
            return ProjectEconomics(
                total_capex_usd=total_capex,
                total_opex_usd=total_opex,
                annual_revenue_usd=annual_revenue,
                net_annual_cash_flow_usd=net_annual_cash_flow,
                project_lifetime_years=financial_params.get("project_lifetime", 25),
                discount_rate=financial_params.get("discount_rate", 0.08),
                cost_breakdown=capex_breakdown + opex_breakdown,
                financial_metrics=financial_metrics,
                sensitivity_analysis=sensitivity_analysis,
                risk_assessment=risk_assessment
            )
            
        except Exception as e:
            logger.error(f"Error evaluating project costs: {e}")
            agent_logger.log_agent_error(self.agent_id, str(e), project_data)
            raise
    
    async def _calculate_capex(self, project_type: str, capacity_mw: float, 
                              location_data: Dict[str, Any]) -> List[CostBreakdown]:
        """Calculate capital expenditure breakdown"""
        capex_breakdown = []
        
        if project_type == "solar":
            costs = self.solar_costs
            capacity_w = capacity_mw * 1000000
            
            # Solar panel costs
            panel_cost = capacity_w * costs["panel_cost_per_w"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.CAPITAL_EXPENDITURE,
                amount_usd=panel_cost,
                percentage_of_total=0,
                description="Solar panels and modules",
                phase=ProjectPhase.CONSTRUCTION
            ))
            
            # Inverter costs
            inverter_cost = capacity_w * costs["inverter_cost_per_w"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.CAPITAL_EXPENDITURE,
                amount_usd=inverter_cost,
                percentage_of_total=0,
                description="Inverters and power electronics",
                phase=ProjectPhase.CONSTRUCTION
            ))
            
            # Mounting and installation
            mounting_cost = capacity_w * costs["mounting_cost_per_w"]
            installation_cost = capacity_w * costs["installation_cost_per_w"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.CAPITAL_EXPENDITURE,
                amount_usd=mounting_cost + installation_cost,
                percentage_of_total=0,
                description="Mounting systems and installation",
                phase=ProjectPhase.CONSTRUCTION
            ))
            
            # Grid connection
            grid_cost = capacity_mw * costs["grid_connection_cost_per_mw"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.CAPITAL_EXPENDITURE,
                amount_usd=grid_cost,
                percentage_of_total=0,
                description="Grid connection and interconnection",
                phase=ProjectPhase.CONSTRUCTION
            ))
            
            # Permitting and engineering
            permitting_cost = capacity_mw * costs["permitting_cost_per_mw"]
            engineering_cost = capacity_mw * costs["engineering_cost_per_mw"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.REGULATORY_COSTS,
                amount_usd=permitting_cost + engineering_cost,
                percentage_of_total=0,
                description="Permitting, engineering, and project development",
                phase=ProjectPhase.DEVELOPMENT
            ))
            
        elif project_type == "wind":
            costs = self.wind_costs
            
            # Wind turbine costs
            turbine_cost = capacity_mw * costs["turbine_cost_per_mw"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.CAPITAL_EXPENDITURE,
                amount_usd=turbine_cost,
                percentage_of_total=0,
                description="Wind turbines and generators",
                phase=ProjectPhase.CONSTRUCTION
            ))
            
            # Foundation costs
            foundation_cost = capacity_mw * costs["foundation_cost_per_mw"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.CAPITAL_EXPENDITURE,
                amount_usd=foundation_cost,
                percentage_of_total=0,
                description="Turbine foundations and civil works",
                phase=ProjectPhase.CONSTRUCTION
            ))
            
            # Electrical and installation
            electrical_cost = capacity_mw * costs["electrical_cost_per_mw"]
            installation_cost = capacity_mw * costs["installation_cost_per_mw"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.CAPITAL_EXPENDITURE,
                amount_usd=electrical_cost + installation_cost,
                percentage_of_total=0,
                description="Electrical systems and installation",
                phase=ProjectPhase.CONSTRUCTION
            ))
            
            # Grid connection
            grid_cost = capacity_mw * costs["grid_connection_cost_per_mw"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.CAPITAL_EXPENDITURE,
                amount_usd=grid_cost,
                percentage_of_total=0,
                description="Grid connection and substation",
                phase=ProjectPhase.CONSTRUCTION
            ))
            
            # Permitting and engineering
            permitting_cost = capacity_mw * costs["permitting_cost_per_mw"]
            engineering_cost = capacity_mw * costs["engineering_cost_per_mw"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.REGULATORY_COSTS,
                amount_usd=permitting_cost + engineering_cost,
                percentage_of_total=0,
                description="Permitting, engineering, and project development",
                phase=ProjectPhase.DEVELOPMENT
            ))
            
        elif project_type == "hydro":
            costs = self.hydro_costs
            
            # Turbine costs
            turbine_cost = capacity_mw * costs["turbine_cost_per_mw"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.CAPITAL_EXPENDITURE,
                amount_usd=turbine_cost,
                percentage_of_total=0,
                description="Hydroelectric turbines and generators",
                phase=ProjectPhase.CONSTRUCTION
            ))
            
            # Civil works
            civil_cost = capacity_mw * costs["civil_works_cost_per_mw"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.CAPITAL_EXPENDITURE,
                amount_usd=civil_cost,
                percentage_of_total=0,
                description="Dams, penstocks, and civil infrastructure",
                phase=ProjectPhase.CONSTRUCTION
            ))
            
            # Electrical and installation
            electrical_cost = capacity_mw * costs["electrical_cost_per_mw"]
            installation_cost = capacity_mw * costs["installation_cost_per_mw"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.CAPITAL_EXPENDITURE,
                amount_usd=electrical_cost + installation_cost,
                percentage_of_total=0,
                description="Electrical systems and installation",
                phase=ProjectPhase.CONSTRUCTION
            ))
            
            # Grid connection
            grid_cost = capacity_mw * costs["grid_connection_cost_per_mw"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.CAPITAL_EXPENDITURE,
                amount_usd=grid_cost,
                percentage_of_total=0,
                description="Grid connection and substation",
                phase=ProjectPhase.CONSTRUCTION
            ))
            
            # Permitting and engineering
            permitting_cost = capacity_mw * costs["permitting_cost_per_mw"]
            engineering_cost = capacity_mw * costs["engineering_cost_per_mw"]
            capex_breakdown.append(CostBreakdown(
                category=CostCategory.REGULATORY_COSTS,
                amount_usd=permitting_cost + engineering_cost,
                percentage_of_total=0,
                description="Permitting, engineering, and environmental studies",
                phase=ProjectPhase.DEVELOPMENT
            ))
        
        # Add location-specific adjustments
        location_multiplier = self._get_location_cost_multiplier(location_data)
        for cost in capex_breakdown:
            cost.amount_usd *= location_multiplier
        
        # Calculate percentages
        total_capex = sum(cost.amount_usd for cost in capex_breakdown)
        for cost in capex_breakdown:
            cost.percentage_of_total = (cost.amount_usd / total_capex) * 100
        
        return capex_breakdown
    
    async def _calculate_opex(self, project_type: str, capacity_mw: float,
                           resource_data: Dict[str, Any]) -> List[CostBreakdown]:
        """Calculate operational expenditure breakdown"""
        opex_breakdown = []
        
        # Base OPEX per MW per year
        base_opex_per_mw = {
            "solar": 15000,
            "wind": 25000,
            "hydro": 20000
        }.get(project_type, 20000)
        
        # Operations and maintenance
        oam_cost = capacity_mw * base_opex_per_mw
        opex_breakdown.append(CostBreakdown(
            category=CostCategory.OPERATIONAL_EXPENDITURE,
            amount_usd=oam_cost,
            percentage_of_total=0,
            description="Operations and maintenance",
            phase=ProjectPhase.OPERATION,
            recurring=True
        ))
        
        # Insurance costs
        insurance_rate = 0.002  # 0.2% of project value per year
        project_value = capacity_mw * 1000000  # Rough estimate
        insurance_cost = project_value * insurance_rate
        opex_breakdown.append(CostBreakdown(
            category=CostCategory.INSURANCE_COSTS,
            amount_usd=insurance_cost,
            percentage_of_total=0,
            description="Property and liability insurance",
            phase=ProjectPhase.OPERATION,
            recurring=True
        ))
        
        # Land lease (if applicable)
        land_cost_per_mw = 2000  # $2,000 per MW per year
        land_cost = capacity_mw * land_cost_per_mw
        opex_breakdown.append(CostBreakdown(
            category=CostCategory.OPERATIONAL_EXPENDITURE,
            amount_usd=land_cost,
            percentage_of_total=0,
            description="Land lease payments",
            phase=ProjectPhase.OPERATION,
            recurring=True
        ))
        
        # Administrative costs
        admin_cost = capacity_mw * 5000  # $5,000 per MW per year
        opex_breakdown.append(CostBreakdown(
            category=CostCategory.OPERATIONAL_EXPENDITURE,
            amount_usd=admin_cost,
            percentage_of_total=0,
            description="Administrative and management costs",
            phase=ProjectPhase.OPERATION,
            recurring=True
        ))
        
        # Calculate percentages
        total_opex = sum(cost.amount_usd for cost in opex_breakdown)
        for cost in opex_breakdown:
            cost.percentage_of_total = (cost.amount_usd / total_opex) * 100
        
        return opex_breakdown
    
    async def _calculate_annual_revenue(self, project_type: str, capacity_mw: float,
                                     resource_data: Dict[str, Any],
                                     financial_params: Dict[str, Any]) -> float:
        """Calculate annual revenue from energy sales"""
        # Get energy generation data
        annual_generation_gwh = resource_data.get("annual_generation_gwh", 0)
        
        # Get electricity price
        electricity_price_usd_mwh = financial_params.get("electricity_price_usd_mwh", 50)
        
        # Calculate base revenue
        base_revenue = annual_generation_gwh * electricity_price_usd_mwh
        
        # Apply renewable energy credits (if applicable)
        rec_price_usd_mwh = financial_params.get("rec_price_usd_mwh", 0)
        rec_revenue = annual_generation_gwh * rec_price_usd_mwh
        
        # Apply capacity payments (if applicable)
        capacity_price_usd_mw = financial_params.get("capacity_price_usd_mw", 0)
        capacity_revenue = capacity_mw * capacity_price_usd_mw
        
        total_revenue = base_revenue + rec_revenue + capacity_revenue
        
        return total_revenue
    
    async def _calculate_financial_metrics(self, total_capex: float, total_opex: float,
                                        annual_revenue: float,
                                        financial_params: Dict[str, Any]) -> FinancialMetrics:
        """Calculate key financial metrics"""
        project_lifetime = financial_params.get("project_lifetime", 25)
        discount_rate = financial_params.get("discount_rate", 0.08)
        
        # Calculate annual cash flow
        annual_cash_flow = annual_revenue - total_opex
        
        # Calculate NPV
        npv = -total_capex
        for year in range(1, project_lifetime + 1):
            npv += annual_cash_flow / ((1 + discount_rate) ** year)
        
        # Calculate IRR (simplified)
        irr = self._calculate_irr(total_capex, annual_cash_flow, project_lifetime)
        
        # Calculate payback period
        payback_period = total_capex / annual_cash_flow
        
        # Calculate LCOE
        lcoe = self._calculate_lcoe(total_capex, total_opex, annual_revenue, project_lifetime, discount_rate)
        
        # Calculate ROI
        total_revenue_lifetime = annual_revenue * project_lifetime
        roi = (total_revenue_lifetime - total_capex - total_opex * project_lifetime) / total_capex
        
        return FinancialMetrics(
            net_present_value_usd=npv,
            internal_rate_of_return=irr,
            payback_period_years=payback_period,
            levelized_cost_of_energy_usd_mwh=lcoe,
            return_on_investment=roi,
            net_annual_cash_flow_usd=annual_cash_flow
        )
    
    def _calculate_irr(self, initial_investment: float, annual_cash_flow: float,
                      project_lifetime: int) -> float:
        """Calculate Internal Rate of Return (simplified)"""
        # Use Newton-Raphson method for IRR calculation
        rate = 0.1  # Initial guess
        
        for _ in range(100):  # Maximum iterations
            npv = -initial_investment
            npv_derivative = 0
            
            for year in range(1, project_lifetime + 1):
                npv += annual_cash_flow / ((1 + rate) ** year)
                npv_derivative -= year * annual_cash_flow / ((1 + rate) ** (year + 1))
            
            if abs(npv) < 1e-6:
                break
            
            rate = rate - npv / npv_derivative
        
        return max(0, min(1, rate))  # Clamp between 0 and 100%
    
    def _calculate_lcoe(self, total_capex: float, total_opex: float,
                       annual_revenue: float, project_lifetime: int,
                       discount_rate: float) -> float:
        """Calculate Levelized Cost of Energy"""
        # Calculate total discounted costs
        total_discounted_costs = total_capex
        for year in range(1, project_lifetime + 1):
            total_discounted_costs += total_opex / ((1 + discount_rate) ** year)
        
        # Calculate total discounted energy generation
        annual_generation_gwh = annual_revenue / 50  # Assume $50/MWh average price
        total_discounted_generation = 0
        for year in range(1, project_lifetime + 1):
            total_discounted_generation += annual_generation_gwh / ((1 + discount_rate) ** year)
        
        # Calculate LCOE
        if total_discounted_generation > 0:
            lcoe = total_discounted_costs / total_discounted_generation
        else:
            lcoe = 0
        
        return lcoe
    
    def _get_location_cost_multiplier(self, location_data: Dict[str, Any]) -> float:
        """Get location-specific cost multiplier"""
        # Remote locations typically cost more
        distance_to_city = location_data.get("distance_to_city_km", 50)
        
        if distance_to_city > 100:
            return 1.3
        elif distance_to_city > 50:
            return 1.15
        else:
            return 1.0
    
    async def _perform_sensitivity_analysis(self, project_type: str, capacity_mw: float,
                                           financial_params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform sensitivity analysis on key variables"""
        base_params = financial_params.copy()
        
        # Variables to test
        variables = {
            "electricity_price": [0.8, 0.9, 1.0, 1.1, 1.2],
            "discount_rate": [0.06, 0.07, 0.08, 0.09, 0.10],
            "capacity_factor": [0.8, 0.9, 1.0, 1.1, 1.2]
        }
        
        sensitivity_results = {}
        
        for variable, values in variables.items():
            results = []
            for multiplier in values:
                test_params = base_params.copy()
                if variable == "electricity_price":
                    test_params["electricity_price_usd_mwh"] *= multiplier
                elif variable == "discount_rate":
                    test_params["discount_rate"] *= multiplier
                elif variable == "capacity_factor":
                    # Adjust generation accordingly
                    test_params["annual_generation_gwh"] *= multiplier
                
                # Calculate NPV for this scenario
                # This is a simplified calculation
                npv = self._calculate_simple_npv(test_params)
                results.append({"multiplier": multiplier, "npv": npv})
            
            sensitivity_results[variable] = results
        
        return sensitivity_results
    
    def _calculate_simple_npv(self, financial_params: Dict[str, Any]) -> float:
        """Calculate simplified NPV for sensitivity analysis"""
        total_capex = 100000000  # $100M base case
        annual_revenue = financial_params.get("annual_generation_gwh", 200) * financial_params.get("electricity_price_usd_mwh", 50)
        annual_opex = 5000000  # $5M per year
        discount_rate = financial_params.get("discount_rate", 0.08)
        project_lifetime = 25
        
        npv = -total_capex
        for year in range(1, project_lifetime + 1):
            npv += (annual_revenue - annual_opex) / ((1 + discount_rate) ** year)
        
        return npv
    
    async def _assess_project_risks(self, project_type: str, location_data: Dict[str, Any],
                                   resource_data: Dict[str, Any],
                                   financial_params: Dict[str, Any]) -> Dict[str, Any]:
        """Assess project risks and their potential impact"""
        risks = {}
        
        # Resource risk
        capacity_factor = resource_data.get("capacity_factor", 0.3)
        if capacity_factor < 0.25:
            risks["resource_risk"] = {
                "level": "high",
                "description": "Low resource availability may impact project economics",
                "mitigation": "Consider alternative sites or technologies"
            }
        elif capacity_factor < 0.35:
            risks["resource_risk"] = {
                "level": "medium",
                "description": "Moderate resource availability",
                "mitigation": "Monitor resource data and consider conservative estimates"
            }
        else:
            risks["resource_risk"] = {
                "level": "low",
                "description": "Good resource availability",
                "mitigation": "Continue monitoring"
            }
        
        # Regulatory risk
        regulatory_score = location_data.get("regulatory_score", 0.7)
        if regulatory_score < 0.6:
            risks["regulatory_risk"] = {
                "level": "high",
                "description": "Complex regulatory environment",
                "mitigation": "Engage with regulators early and budget for delays"
            }
        else:
            risks["regulatory_risk"] = {
                "level": "low",
                "description": "Favorable regulatory environment",
                "mitigation": "Standard permitting process"
            }
        
        # Market risk
        electricity_price = financial_params.get("electricity_price_usd_mwh", 50)
        if electricity_price < 40:
            risks["market_risk"] = {
                "level": "high",
                "description": "Low electricity prices may impact revenue",
                "mitigation": "Consider power purchase agreements or hedging"
            }
        else:
            risks["market_risk"] = {
                "level": "low",
                "description": "Favorable electricity prices",
                "mitigation": "Monitor market trends"
            }
        
        # Technology risk
        if project_type in ["solar", "wind"]:
            risks["technology_risk"] = {
                "level": "low",
                "description": "Mature technology with proven track record",
                "mitigation": "Use established suppliers and warranties"
            }
        else:
            risks["technology_risk"] = {
                "level": "medium",
                "description": "Technology-specific risks",
                "mitigation": "Thorough due diligence and expert consultation"
            }
        
        return risks
    
    # Message handlers
    async def _handle_evaluate_costs(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle project cost evaluation requests"""
        project_data = message.content
        
        economics = await self.evaluate_project_costs(project_data)
        
        return {
            "project_economics": {
                "total_capex_usd": economics.total_capex_usd,
                "total_opex_usd": economics.total_opex_usd,
                "annual_revenue_usd": economics.annual_revenue_usd,
                "net_annual_cash_flow_usd": economics.net_annual_cash_flow_usd,
                "project_lifetime_years": economics.project_lifetime_years,
                "discount_rate": economics.discount_rate,
                "cost_breakdown": [
                    {
                        "category": cost.category.value,
                        "amount_usd": cost.amount_usd,
                        "percentage_of_total": cost.percentage_of_total,
                        "description": cost.description,
                        "phase": cost.phase.value,
                        "recurring": cost.recurring
                    }
                    for cost in economics.cost_breakdown
                ],
                "financial_metrics": {
                    "net_present_value_usd": economics.financial_metrics.net_present_value_usd,
                    "internal_rate_of_return": economics.financial_metrics.internal_rate_of_return,
                    "payback_period_years": economics.financial_metrics.payback_period_years,
                    "levelized_cost_of_energy_usd_mwh": economics.financial_metrics.levelized_cost_of_energy_usd_mwh,
                    "return_on_investment": economics.financial_metrics.return_on_investment,
                    "net_annual_cash_flow_usd": economics.financial_metrics.net_annual_cash_flow_usd
                },
                "sensitivity_analysis": economics.sensitivity_analysis,
                "risk_assessment": economics.risk_assessment
            }
        }
    
    async def _handle_calculate_metrics(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle financial metrics calculation requests"""
        financial_params = message.content
        
        metrics = await self._calculate_financial_metrics(
            financial_params["total_capex"],
            financial_params["total_opex"],
            financial_params["annual_revenue"],
            financial_params
        )
        
        return {
            "financial_metrics": {
                "net_present_value_usd": metrics.net_present_value_usd,
                "internal_rate_of_return": metrics.internal_rate_of_return,
                "payback_period_years": metrics.payback_period_years,
                "levelized_cost_of_energy_usd_mwh": metrics.levelized_cost_of_energy_usd_mwh,
                "return_on_investment": metrics.return_on_investment,
                "net_annual_cash_flow_usd": metrics.net_annual_cash_flow_usd
            }
        }
    
    async def _handle_sensitivity_analysis(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle sensitivity analysis requests"""
        project_data = message.content
        
        sensitivity = await self._perform_sensitivity_analysis(
            project_data["project_type"],
            project_data["capacity_mw"],
            project_data["financial_params"]
        )
        
        return {"sensitivity_analysis": sensitivity}
    
    async def _handle_risk_assessment(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle risk assessment requests"""
        project_data = message.content
        
        risks = await self._assess_project_risks(
            project_data["project_type"],
            project_data["location"],
            project_data["resource_data"],
            project_data["financial_params"]
        )
        
        return {"risk_assessment": risks}
    
    async def _handle_compare_options(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle project option comparison requests"""
        project_options = message.content.get("options", [])
        
        comparisons = []
        for option in project_options:
            economics = await self.evaluate_project_costs(option)
            comparisons.append({
                "project_type": option.get("project_type"),
                "capacity_mw": option.get("capacity_mw"),
                "npv_usd": economics.financial_metrics.net_present_value_usd,
                "irr": economics.financial_metrics.internal_rate_of_return,
                "payback_years": economics.financial_metrics.payback_period_years,
                "lcoe_usd_mwh": economics.financial_metrics.levelized_cost_of_energy_usd_mwh
            })
        
        # Sort by NPV
        comparisons.sort(key=lambda x: x["npv_usd"], reverse=True)
        
        return {"project_comparisons": comparisons}