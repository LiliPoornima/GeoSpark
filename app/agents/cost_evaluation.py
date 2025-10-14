"""
Cost Evaluation Agent
Performs financial analysis and cost evaluation for renewable energy projects
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class CostEvaluationAgent:
    """Agent for evaluating project costs and financial metrics"""
    
    def __init__(self):
        # Cost parameters (USD per MW installed)
        self.solar_capex_per_mw = 1_000_000  # $1M per MW for solar
        self.wind_capex_per_mw = 1_500_000   # $1.5M per MW for wind
        
        # Operating costs (USD per MW per year)
        self.solar_opex_per_mw = 25_000      # $25k per MW per year
        self.wind_opex_per_mw = 40_000       # $40k per MW per year
        
        # Financial parameters
        self.discount_rate = 0.08            # 8% discount rate
        self.project_lifetime = 25           # 25 years
        self.electricity_price = 50          # $50 per MWh
        
    async def evaluate_costs(
        self,
        location: str,
        resource_data: Dict[str, Any],
        project_type: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        Evaluate project costs and financial metrics
        
        Args:
            location: Location name
            resource_data: Resource estimation data
            project_type: Type of project (solar, wind, or hybrid)
            
        Returns:
            Dictionary with cost evaluation and financial metrics
        """
        try:
            logger.info(f"Evaluating costs for {location}, type: {project_type}")
            
            installed_capacity = resource_data.get("installed_capacity_mw", 100)
            annual_generation_gwh = resource_data.get("annual_generation_gwh", 200)
            annual_generation_mwh = annual_generation_gwh * 1000
            
            # Calculate CAPEX
            if project_type == "solar":
                capex = installed_capacity * self.solar_capex_per_mw
                annual_opex = installed_capacity * self.solar_opex_per_mw
            elif project_type == "wind":
                capex = installed_capacity * self.wind_capex_per_mw
                annual_opex = installed_capacity * self.wind_opex_per_mw
            else:  # hybrid (60% solar, 40% wind typical split)
                solar_capacity = installed_capacity * 0.6
                wind_capacity = installed_capacity * 0.4
                capex = (
                    solar_capacity * self.solar_capex_per_mw +
                    wind_capacity * self.wind_capex_per_mw
                )
                annual_opex = (
                    solar_capacity * self.solar_opex_per_mw +
                    wind_capacity * self.wind_opex_per_mw
                )
            
            # Calculate annual revenue
            annual_revenue = annual_generation_mwh * self.electricity_price
            
            # Calculate NPV (Net Present Value)
            npv = self._calculate_npv(
                capex,
                annual_revenue,
                annual_opex,
                self.project_lifetime,
                self.discount_rate
            )
            
            # Calculate IRR (Internal Rate of Return)
            irr = self._calculate_irr(
                capex,
                annual_revenue,
                annual_opex,
                self.project_lifetime
            )
            
            # Calculate LCOE (Levelized Cost of Energy)
            lcoe = self._calculate_lcoe(
                capex,
                annual_opex,
                annual_generation_mwh,
                self.project_lifetime,
                self.discount_rate
            )
            
            # Calculate payback period
            payback_period = capex / (annual_revenue - annual_opex)
            
            # Calculate ROI
            total_net_revenue = (annual_revenue - annual_opex) * self.project_lifetime
            roi = ((total_net_revenue - capex) / capex) * 100
            
            result = {
                "location": location,
                "project_type": project_type,
                "installed_capacity_mw": installed_capacity,
                "capex_usd": round(capex, 2),
                "annual_opex_usd": round(annual_opex, 2),
                "annual_revenue_usd": round(annual_revenue, 2),
                "npv_usd": round(npv, 2),
                "irr_percent": round(irr * 100, 2),
                "lcoe_usd_per_mwh": round(lcoe, 2),
                "payback_period_years": round(payback_period, 2),
                "roi_percent": round(roi, 2),
                "project_lifetime_years": self.project_lifetime,
                "financial_viability": self._assess_viability(npv, irr, payback_period)
            }
            
            logger.info(f"Cost evaluation complete: NPV=${npv/1e6:.2f}M, IRR={irr*100:.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"Error in cost evaluation: {str(e)}")
            raise
    
    def _calculate_npv(
        self,
        capex: float,
        annual_revenue: float,
        annual_opex: float,
        lifetime: int,
        discount_rate: float
    ) -> float:
        """Calculate Net Present Value"""
        annual_net_cashflow = annual_revenue - annual_opex
        
        # Sum of discounted cash flows
        npv = -capex
        for year in range(1, lifetime + 1):
            npv += annual_net_cashflow / ((1 + discount_rate) ** year)
        
        return npv
    
    def _calculate_irr(
        self,
        capex: float,
        annual_revenue: float,
        annual_opex: float,
        lifetime: int
    ) -> float:
        """Calculate Internal Rate of Return using iterative method"""
        annual_net_cashflow = annual_revenue - annual_opex
        
        # Simple IRR approximation for constant cash flows
        # More accurate would be to use Newton-Raphson method
        
        # Try different rates to find where NPV = 0
        low_rate = 0.0
        high_rate = 1.0
        
        for _ in range(50):  # Iterate to converge
            mid_rate = (low_rate + high_rate) / 2
            
            npv = -capex
            for year in range(1, lifetime + 1):
                npv += annual_net_cashflow / ((1 + mid_rate) ** year)
            
            if abs(npv) < 1000:  # Close enough to zero
                return mid_rate
            
            if npv > 0:
                low_rate = mid_rate
            else:
                high_rate = mid_rate
        
        return mid_rate
    
    def _calculate_lcoe(
        self,
        capex: float,
        annual_opex: float,
        annual_generation_mwh: float,
        lifetime: int,
        discount_rate: float
    ) -> float:
        """Calculate Levelized Cost of Energy"""
        
        # Present value of costs
        pv_costs = capex
        for year in range(1, lifetime + 1):
            pv_costs += annual_opex / ((1 + discount_rate) ** year)
        
        # Present value of generation
        pv_generation = 0
        for year in range(1, lifetime + 1):
            pv_generation += annual_generation_mwh / ((1 + discount_rate) ** year)
        
        lcoe = pv_costs / pv_generation
        return lcoe
    
    def _assess_viability(
        self,
        npv: float,
        irr: float,
        payback_period: float
    ) -> str:
        """Assess overall financial viability"""
        
        score = 0
        
        # NPV criteria
        if npv > 50_000_000:
            score += 3
        elif npv > 20_000_000:
            score += 2
        elif npv > 0:
            score += 1
        
        # IRR criteria (compared to discount rate)
        if irr > 0.15:
            score += 3
        elif irr > 0.10:
            score += 2
        elif irr > 0.08:
            score += 1
        
        # Payback period criteria
        if payback_period < 10:
            score += 3
        elif payback_period < 15:
            score += 2
        elif payback_period < 20:
            score += 1
        
        # Overall assessment
        if score >= 7:
            return "Highly Viable"
        elif score >= 5:
            return "Viable"
        elif score >= 3:
            return "Marginally Viable"
        else:
            return "Not Viable"
