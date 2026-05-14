"""
Financial Projector Service - Generates financial projections and analysis
Provides revenue forecasts, cost projections, break-even analysis, and ROI calculations
"""
import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import math

logger = logging.getLogger(__name__)


class RevenueProjection(BaseModel):
    """Revenue projection for a period"""
    period: str  # "Month 1", "Q1 Year 2", etc.
    period_number: int
    revenue: float
    growth_rate: float
    assumptions: List[str] = []


class CostProjection(BaseModel):
    """Cost projection for a period"""
    period: str
    period_number: int
    fixed_costs: float
    variable_costs: float
    total_costs: float


class BreakEvenAnalysis(BaseModel):
    """Break-even analysis"""
    break_even_month: int
    break_even_revenue: float
    cumulative_investment_at_break_even: float
    months_to_profitability: int


class ProfitMargins(BaseModel):
    """Profit margin calculations"""
    gross_margin: float  # Percentage
    net_margin: float  # Percentage
    operating_margin: float  # Percentage


class ROICalculation(BaseModel):
    """ROI calculation for a period"""
    period_months: int
    roi_percentage: float
    total_return: float
    payback_period_months: int


class CashFlowProjection(BaseModel):
    """Cash flow projection for a period"""
    period: str
    period_number: int
    inflows: float
    outflows: float
    net_cash_flow: float
    cumulative_cash: float


class ScenarioAnalysis(BaseModel):
    """Scenario analysis with best/realistic/worst cases"""
    best_case: Dict[str, Any]
    realistic_case: Dict[str, Any]
    worst_case: Dict[str, Any]
    scenario_assumptions: Dict[str, List[str]]


class FinancialProjections(BaseModel):
    """Complete financial projections"""
    revenue_projections: List[RevenueProjection]
    cost_projections: List[CostProjection]
    break_even_analysis: BreakEvenAnalysis
    profit_margins: ProfitMargins
    roi_calculations: Dict[str, ROICalculation]  # "1_year", "2_year", "3_year"
    cash_flow_projections: List[CashFlowProjection]
    scenario_analysis: ScenarioAnalysis
    projection_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FinancialProjector:
    """
    Financial projector that generates comprehensive financial projections
    including revenue forecasts, cost projections, and profitability analysis
    """
    
    # Industry-specific growth rates (monthly % for first year)
    INDUSTRY_GROWTH_RATES = {
        "SaaS": {
            "initial_monthly": 15.0,  # 15% monthly growth
            "year2_quarterly": 25.0,  # 25% quarterly growth
            "year3_quarterly": 20.0   # 20% quarterly growth
        },
        "E-commerce": {
            "initial_monthly": 12.0,
            "year2_quarterly": 20.0,
            "year3_quarterly": 15.0
        },
        "Retail": {
            "initial_monthly": 8.0,
            "year2_quarterly": 12.0,
            "year3_quarterly": 10.0
        },
        "Service": {
            "initial_monthly": 10.0,
            "year2_quarterly": 15.0,
            "year3_quarterly": 12.0
        },
        "Manufacturing": {
            "initial_monthly": 7.0,
            "year2_quarterly": 10.0,
            "year3_quarterly": 8.0
        },
        "Technology": {
            "initial_monthly": 13.0,
            "year2_quarterly": 22.0,
            "year3_quarterly": 18.0
        },
        "Default": {
            "initial_monthly": 10.0,
            "year2_quarterly": 15.0,
            "year3_quarterly": 12.0
        }
    }
    
    # Cost structure percentages
    COST_STRUCTURES = {
        "SaaS": {
            "fixed_percentage": 60,  # 60% fixed costs
            "variable_percentage": 40  # 40% variable costs (scales with revenue)
        },
        "E-commerce": {
            "fixed_percentage": 40,
            "variable_percentage": 60
        },
        "Retail": {
            "fixed_percentage": 50,
            "variable_percentage": 50
        },
        "Service": {
            "fixed_percentage": 70,
            "variable_percentage": 30
        },
        "Manufacturing": {
            "fixed_percentage": 45,
            "variable_percentage": 55
        },
        "Technology": {
            "fixed_percentage": 65,
            "variable_percentage": 35
        },
        "Default": {
            "fixed_percentage": 55,
            "variable_percentage": 45
        }
    }
    
    def __init__(self, industry_benchmarks: Optional[Dict[str, Any]] = None):
        """
        Initialize financial projector
        
        Args:
            industry_benchmarks: Optional custom industry benchmarks
        """
        self.industry_benchmarks = industry_benchmarks or {}
        logger.info("FinancialProjector initialized")
    
    async def generate_projections(
        self,
        business_type: str,
        industry: str,
        initial_budget: float,
        market_size_value: Optional[str] = None,
        target_market_share: float = 0.01  # 1% default
    ) -> FinancialProjections:
        """
        Generate comprehensive financial projections
        
        Args:
            business_type: Type of business
            industry: Industry category
            initial_budget: Initial investment budget
            market_size_value: Market size (e.g., "$10B")
            target_market_share: Target market share percentage (0.01 = 1%)
            
        Returns:
            FinancialProjections with complete analysis
        """
        logger.info(f"Generating financial projections for {business_type} in {industry}")
        
        # Forecast revenue for 36 months
        revenue_projections = self.forecast_revenue(
            business_type, industry, initial_budget, market_size_value, target_market_share, months=36
        )
        
        # Project costs for 36 months
        cost_projections = self.project_costs(
            initial_budget, business_type, industry, revenue_projections, months=36
        )
        
        # Calculate break-even
        break_even = self.calculate_break_even(revenue_projections, cost_projections)
        
        # Calculate profit margins (using year 1 average)
        year1_revenue = sum(rp.revenue for rp in revenue_projections[:12])
        year1_costs = sum(cp.total_costs for cp in cost_projections[:12])
        profit_margins = self.calculate_margins(year1_revenue, year1_costs)
        
        # Calculate ROI for 1, 2, and 3 years
        roi_calculations = {
            "1_year": self.calculate_roi(initial_budget, revenue_projections[:12], cost_projections[:12], 12),
            "2_year": self.calculate_roi(initial_budget, revenue_projections[:24], cost_projections[:24], 24),
            "3_year": self.calculate_roi(initial_budget, revenue_projections[:36], cost_projections[:36], 36)
        }
        
        # Project cash flow
        cash_flow_projections = self.project_cash_flow(
            revenue_projections, cost_projections, initial_budget
        )
        
        # Generate scenario analysis
        scenario_analysis = self.generate_scenarios(
            business_type, industry, initial_budget, market_size_value, target_market_share
        )
        
        projections = FinancialProjections(
            revenue_projections=revenue_projections,
            cost_projections=cost_projections,
            break_even_analysis=break_even,
            profit_margins=profit_margins,
            roi_calculations=roi_calculations,
            cash_flow_projections=cash_flow_projections,
            scenario_analysis=scenario_analysis
        )
        
        logger.info("Financial projections generated successfully")
        return projections
    
    def forecast_revenue(
        self,
        business_type: str,
        industry: str,
        initial_budget: float,
        market_size_value: Optional[str] = None,
        target_market_share: float = 0.01,
        months: int = 36
    ) -> List[RevenueProjection]:
        """
        Forecast revenue for specified period
        
        Args:
            business_type: Type of business
            industry: Industry category
            initial_budget: Initial investment
            market_size_value: Market size string
            target_market_share: Target market share
            months: Number of months to project
            
        Returns:
            List of RevenueProjection objects
        """
        # Get growth rates for industry
        growth_rates = self._get_growth_rates(business_type, industry)
        
        # Calculate initial monthly revenue (conservative estimate)
        # Assume 5-10% of initial budget as first month revenue
        initial_monthly_revenue = initial_budget * 0.075  # 7.5% of budget
        
        projections = []
        current_revenue = initial_monthly_revenue
        
        for month in range(1, months + 1):
            # Determine growth rate based on period
            if month <= 12:
                # Year 1: Monthly projections with monthly growth
                growth_rate = growth_rates["initial_monthly"]
                period = f"Month {month}"
                period_number = month
            elif month <= 24:
                # Year 2: Quarterly projections
                if (month - 12) % 3 == 1:  # First month of quarter
                    growth_rate = growth_rates["year2_quarterly"]
                    quarter = ((month - 13) // 3) + 1
                    period = f"Q{quarter} Year 2"
                    period_number = month
                else:
                    # Skip non-quarter months for year 2+
                    current_revenue *= (1 + growth_rate / 100)
                    continue
            else:
                # Year 3: Quarterly projections
                if (month - 24) % 3 == 1:  # First month of quarter
                    growth_rate = growth_rates["year3_quarterly"]
                    quarter = ((month - 25) // 3) + 1
                    period = f"Q{quarter} Year 3"
                    period_number = month
                else:
                    # Skip non-quarter months for year 3
                    current_revenue *= (1 + growth_rate / 100)
                    continue
            
            # Apply growth
            if month > 1:
                current_revenue *= (1 + growth_rate / 100)
            
            # Generate assumptions
            assumptions = self._generate_revenue_assumptions(
                month, business_type, growth_rate
            )
            
            projection = RevenueProjection(
                period=period,
                period_number=period_number,
                revenue=current_revenue,
                growth_rate=growth_rate,
                assumptions=assumptions
            )
            projections.append(projection)
        
        logger.debug(f"Generated {len(projections)} revenue projections")
        return projections
    
    def project_costs(
        self,
        initial_budget: float,
        business_type: str,
        industry: str,
        revenue_projections: List[RevenueProjection],
        months: int = 36
    ) -> List[CostProjection]:
        """
        Project costs over time
        
        Args:
            initial_budget: Initial investment
            business_type: Type of business
            industry: Industry category
            revenue_projections: Revenue projections for reference
            months: Number of months to project
            
        Returns:
            List of CostProjection objects
        """
        # Get cost structure
        cost_structure = self._get_cost_structure(business_type, industry)
        
        # Calculate monthly burn rate from initial budget
        # Assume budget covers 12-18 months, use 15 months average
        monthly_budget_burn = initial_budget / 15
        
        # Fixed costs (relatively stable)
        base_fixed_costs = monthly_budget_burn * (cost_structure["fixed_percentage"] / 100)
        
        # Variable costs (scale with revenue)
        variable_cost_rate = cost_structure["variable_percentage"] / 100
        
        projections = []
        revenue_index = 0
        
        for month in range(1, months + 1):
            # Get corresponding revenue projection
            if revenue_index < len(revenue_projections) and revenue_projections[revenue_index].period_number == month:
                current_revenue = revenue_projections[revenue_index].revenue
                period = revenue_projections[revenue_index].period
                revenue_index += 1
            else:
                # Estimate revenue for non-projection months
                if revenue_index > 0:
                    current_revenue = revenue_projections[revenue_index - 1].revenue * 1.1
                else:
                    current_revenue = initial_budget * 0.075
                period = f"Month {month}"
            
            # Fixed costs (increase slightly over time due to inflation/growth)
            inflation_factor = 1 + (0.03 * (month / 12))  # 3% annual inflation
            fixed_costs = base_fixed_costs * inflation_factor
            
            # Variable costs (percentage of revenue)
            variable_costs = current_revenue * variable_cost_rate
            
            # Total costs
            total_costs = fixed_costs + variable_costs
            
            projection = CostProjection(
                period=period,
                period_number=month,
                fixed_costs=fixed_costs,
                variable_costs=variable_costs,
                total_costs=total_costs
            )
            projections.append(projection)
        
        logger.debug(f"Generated {len(projections)} cost projections")
        return projections
    
    def calculate_break_even(
        self,
        revenue_projections: List[RevenueProjection],
        cost_projections: List[CostProjection]
    ) -> BreakEvenAnalysis:
        """
        Calculate break-even point
        
        Args:
            revenue_projections: Revenue projections
            cost_projections: Cost projections
            
        Returns:
            BreakEvenAnalysis
        """
        cumulative_revenue = 0
        cumulative_costs = 0
        break_even_month = None
        break_even_revenue = 0
        
        # Find break-even point
        for i in range(min(len(revenue_projections), len(cost_projections))):
            cumulative_revenue += revenue_projections[i].revenue
            cumulative_costs += cost_projections[i].total_costs
            
            if cumulative_revenue >= cumulative_costs and break_even_month is None:
                break_even_month = revenue_projections[i].period_number
                break_even_revenue = cumulative_revenue
                break
        
        # If no break-even found in projection period
        if break_even_month is None:
            break_even_month = len(revenue_projections) + 6  # Estimate 6 months beyond
            break_even_revenue = cumulative_revenue * 1.5
            cumulative_costs = cumulative_costs
        
        # Calculate months to profitability (when monthly profit > 0)
        months_to_profitability = break_even_month
        for i in range(len(revenue_projections)):
            if revenue_projections[i].revenue > cost_projections[i].total_costs:
                months_to_profitability = revenue_projections[i].period_number
                break
        
        analysis = BreakEvenAnalysis(
            break_even_month=break_even_month,
            break_even_revenue=break_even_revenue,
            cumulative_investment_at_break_even=cumulative_costs,
            months_to_profitability=months_to_profitability
        )
        
        logger.debug(f"Break-even calculated at month {break_even_month}")
        return analysis
    
    def calculate_margins(self, revenue: float, costs: float) -> ProfitMargins:
        """
        Calculate profit margins
        
        Args:
            revenue: Total revenue
            costs: Total costs
            
        Returns:
            ProfitMargins
        """
        if revenue == 0:
            return ProfitMargins(
                gross_margin=0.0,
                net_margin=0.0,
                operating_margin=0.0
            )
        
        # Gross margin (assuming COGS is 40% of costs)
        cogs = costs * 0.4
        gross_profit = revenue - cogs
        gross_margin = (gross_profit / revenue) * 100
        
        # Operating margin (revenue - operating costs)
        operating_costs = costs * 0.8  # 80% of costs are operating
        operating_profit = revenue - operating_costs
        operating_margin = (operating_profit / revenue) * 100
        
        # Net margin (revenue - all costs)
        net_profit = revenue - costs
        net_margin = (net_profit / revenue) * 100
        
        margins = ProfitMargins(
            gross_margin=round(gross_margin, 2),
            net_margin=round(net_margin, 2),
            operating_margin=round(operating_margin, 2)
        )
        
        logger.debug(f"Calculated margins: gross={gross_margin:.2f}%, net={net_margin:.2f}%")
        return margins
    
    def calculate_roi(
        self,
        initial_investment: float,
        revenue_projections: List[RevenueProjection],
        cost_projections: List[CostProjection],
        period_months: int
    ) -> ROICalculation:
        """
        Calculate ROI for specified period
        
        Args:
            initial_investment: Initial investment amount
            revenue_projections: Revenue projections
            cost_projections: Cost projections
            period_months: Period in months
            
        Returns:
            ROICalculation
        """
        # Calculate total revenue and costs for period
        total_revenue = sum(rp.revenue for rp in revenue_projections[:period_months])
        total_costs = sum(cp.total_costs for cp in cost_projections[:period_months])
        
        # Net profit
        net_profit = total_revenue - total_costs
        
        # ROI percentage
        roi_percentage = ((net_profit - initial_investment) / initial_investment) * 100
        
        # Total return
        total_return = net_profit
        
        # Payback period (months until investment is recovered)
        cumulative_profit = 0
        payback_period = period_months
        
        for i in range(min(len(revenue_projections), len(cost_projections))):
            period_profit = revenue_projections[i].revenue - cost_projections[i].total_costs
            cumulative_profit += period_profit
            
            if cumulative_profit >= initial_investment:
                payback_period = revenue_projections[i].period_number
                break
        
        calculation = ROICalculation(
            period_months=period_months,
            roi_percentage=round(roi_percentage, 2),
            total_return=total_return,
            payback_period_months=payback_period
        )
        
        logger.debug(f"ROI calculated for {period_months} months: {roi_percentage:.2f}%")
        return calculation
    
    def project_cash_flow(
        self,
        revenue_projections: List[RevenueProjection],
        cost_projections: List[CostProjection],
        initial_capital: float
    ) -> List[CashFlowProjection]:
        """
        Project monthly cash flow
        
        Args:
            revenue_projections: Revenue projections
            cost_projections: Cost projections
            initial_capital: Initial capital/investment
            
        Returns:
            List of CashFlowProjection objects
        """
        projections = []
        cumulative_cash = initial_capital
        
        for i in range(min(len(revenue_projections), len(cost_projections))):
            # Inflows (revenue)
            inflows = revenue_projections[i].revenue
            
            # Outflows (costs)
            outflows = cost_projections[i].total_costs
            
            # Net cash flow
            net_cash_flow = inflows - outflows
            
            # Cumulative cash
            cumulative_cash += net_cash_flow
            
            projection = CashFlowProjection(
                period=revenue_projections[i].period,
                period_number=revenue_projections[i].period_number,
                inflows=inflows,
                outflows=outflows,
                net_cash_flow=net_cash_flow,
                cumulative_cash=cumulative_cash
            )
            projections.append(projection)
        
        logger.debug(f"Generated {len(projections)} cash flow projections")
        return projections
    
    def generate_scenarios(
        self,
        business_type: str,
        industry: str,
        initial_budget: float,
        market_size_value: Optional[str] = None,
        target_market_share: float = 0.01
    ) -> ScenarioAnalysis:
        """
        Generate best/realistic/worst case scenarios
        
        Args:
            business_type: Type of business
            industry: Industry category
            initial_budget: Initial investment
            market_size_value: Market size
            target_market_share: Target market share
            
        Returns:
            ScenarioAnalysis with three scenarios
        """
        # Realistic case (base case)
        realistic_revenue = self.forecast_revenue(
            business_type, industry, initial_budget, market_size_value, target_market_share, months=36
        )
        realistic_year1_revenue = sum(rp.revenue for rp in realistic_revenue[:12])
        
        # Best case (30% higher growth)
        best_revenue = self.forecast_revenue(
            business_type, industry, initial_budget * 1.3, market_size_value, target_market_share * 1.3, months=36
        )
        best_year1_revenue = sum(rp.revenue for rp in best_revenue[:12])
        
        # Worst case (30% lower growth)
        worst_revenue = self.forecast_revenue(
            business_type, industry, initial_budget * 0.7, market_size_value, target_market_share * 0.7, months=36
        )
        worst_year1_revenue = sum(rp.revenue for rp in worst_revenue[:12])
        
        scenario_assumptions = {
            "best_case": [
                "Market conditions highly favorable",
                "Strong customer adoption and retention",
                "Effective marketing and sales execution",
                "Minimal competitive pressure"
            ],
            "realistic_case": [
                "Normal market conditions",
                "Moderate customer adoption",
                "Standard marketing effectiveness",
                "Expected competitive landscape"
            ],
            "worst_case": [
                "Challenging market conditions",
                "Slower customer adoption",
                "Higher customer acquisition costs",
                "Increased competitive pressure"
            ]
        }
        
        analysis = ScenarioAnalysis(
            best_case={
                "year1_revenue": best_year1_revenue,
                "year1_growth": "+30% above realistic",
                "description": "Optimistic scenario with favorable conditions"
            },
            realistic_case={
                "year1_revenue": realistic_year1_revenue,
                "year1_growth": "Base case",
                "description": "Most likely scenario based on industry benchmarks"
            },
            worst_case={
                "year1_revenue": worst_year1_revenue,
                "year1_growth": "-30% below realistic",
                "description": "Conservative scenario with challenges"
            },
            scenario_assumptions=scenario_assumptions
        )
        
        logger.debug("Generated scenario analysis")
        return analysis
    
    # ==================== HELPER METHODS ====================
    
    def _get_growth_rates(self, business_type: str, industry: str) -> Dict[str, float]:
        """Get growth rates for business type/industry"""
        # Check industry first
        if industry:
            for key in self.INDUSTRY_GROWTH_RATES.keys():
                if key.lower() in industry.lower() or industry.lower() in key.lower():
                    return self.INDUSTRY_GROWTH_RATES[key]
        
        # Check business type
        if business_type:
            for key in self.INDUSTRY_GROWTH_RATES.keys():
                if key.lower() in business_type.lower() or business_type.lower() in key.lower():
                    return self.INDUSTRY_GROWTH_RATES[key]
        
        return self.INDUSTRY_GROWTH_RATES["Default"]
    
    def _get_cost_structure(self, business_type: str, industry: str) -> Dict[str, int]:
        """Get cost structure for business type/industry"""
        # Check industry first
        if industry:
            for key in self.COST_STRUCTURES.keys():
                if key.lower() in industry.lower() or industry.lower() in key.lower():
                    return self.COST_STRUCTURES[key]
        
        # Check business type
        if business_type:
            for key in self.COST_STRUCTURES.keys():
                if key.lower() in business_type.lower() or business_type.lower() in key.lower():
                    return self.COST_STRUCTURES[key]
        
        return self.COST_STRUCTURES["Default"]
    
    def _generate_revenue_assumptions(
        self,
        month: int,
        business_type: str,
        growth_rate: float
    ) -> List[str]:
        """Generate revenue assumptions for a period"""
        assumptions = []
        
        if month <= 3:
            assumptions.append("Initial customer acquisition phase")
            assumptions.append("Building brand awareness")
        elif month <= 6:
            assumptions.append("Early traction and customer feedback")
            assumptions.append("Refining product-market fit")
        elif month <= 12:
            assumptions.append("Scaling customer acquisition")
            assumptions.append(f"Maintaining {growth_rate}% monthly growth")
        else:
            assumptions.append("Established market presence")
            assumptions.append(f"Quarterly growth of {growth_rate}%")
        
        return assumptions
