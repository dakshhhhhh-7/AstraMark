"""
Budget Analyzer Service - Analyzes and breaks down business budgets
Provides optimal allocation across categories with industry benchmarks
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field
from exchange_rate_service import ExchangeRateService

logger = logging.getLogger(__name__)


class SubCategory(BaseModel):
    """Sub-category budget item"""
    name: str
    amount: float
    description: str
    priority: str  # "High", "Medium", "Low"


class CategoryAllocation(BaseModel):
    """Budget category allocation"""
    category: str
    amount: float
    percentage: float
    rationale: str


class BudgetBreakdown(BaseModel):
    """Complete budget breakdown"""
    total_budget: float
    currency: str
    categories: List[CategoryAllocation]
    sub_categories: Dict[str, List[SubCategory]]
    allocation_rationale: str
    industry_benchmarks: Dict[str, str]


class ValidationResult(BaseModel):
    """Budget validation result"""
    is_valid: bool
    message: str
    suggested_minimum: Optional[float] = None


class BudgetAnalyzer:
    """
    Budget analyzer that breaks down budgets into optimal allocations
    based on industry benchmarks and business type
    """
    
    # Minimum and maximum budget thresholds (in INR)
    MIN_BUDGET_INR = 10000  # ₹10,000
    MAX_BUDGET_INR = 100000000  # ₹10 Crore
    
    # Industry-specific allocation benchmarks (min%, max%)
    ALLOCATION_BENCHMARKS = {
        "SaaS": {
            "Marketing": (25, 35),
            "Operations": (15, 25),
            "Technology": (20, 30),
            "Staffing": (25, 35),
            "Contingency": (10, 15)
        },
        "E-commerce": {
            "Marketing": (30, 40),
            "Operations": (25, 35),
            "Technology": (15, 25),
            "Staffing": (15, 25),
            "Contingency": (10, 15)
        },
        "Retail": {
            "Marketing": (20, 30),
            "Operations": (30, 40),
            "Technology": (10, 20),
            "Staffing": (25, 35),
            "Contingency": (10, 15)
        },
        "Service": {
            "Marketing": (25, 35),
            "Operations": (20, 30),
            "Technology": (10, 20),
            "Staffing": (30, 40),
            "Contingency": (10, 15)
        },
        "Manufacturing": {
            "Marketing": (15, 25),
            "Operations": (35, 45),
            "Technology": (10, 20),
            "Staffing": (20, 30),
            "Contingency": (10, 15)
        },
        "Technology": {
            "Marketing": (25, 35),
            "Operations": (15, 25),
            "Technology": (25, 35),
            "Staffing": (25, 35),
            "Contingency": (10, 15)
        },
        "Default": {
            "Marketing": (25, 30),
            "Operations": (25, 30),
            "Technology": (15, 20),
            "Staffing": (25, 30),
            "Contingency": (10, 15)
        }
    }
    
    # Sub-category templates
    SUB_CATEGORY_TEMPLATES = {
        "Marketing": [
            ("Social Media Advertising", 0.30, "Paid ads on Facebook, Instagram, LinkedIn", "High"),
            ("Search Engine Marketing (SEM)", 0.25, "Google Ads, Bing Ads campaigns", "High"),
            ("Content Marketing", 0.15, "Blog posts, videos, infographics", "Medium"),
            ("SEO Services", 0.15, "Search engine optimization and link building", "Medium"),
            ("Email Marketing", 0.10, "Email campaigns and automation tools", "Medium"),
            ("Influencer Marketing", 0.05, "Partnerships with influencers", "Low")
        ],
        "Operations": [
            ("Office Space/Rent", 0.35, "Physical office or co-working space", "High"),
            ("Utilities", 0.10, "Electricity, internet, phone", "High"),
            ("Equipment & Supplies", 0.20, "Computers, furniture, office supplies", "High"),
            ("Insurance", 0.15, "Business liability and property insurance", "Medium"),
            ("Legal & Compliance", 0.10, "Legal fees, licenses, permits", "Medium"),
            ("Miscellaneous", 0.10, "Other operational expenses", "Low")
        ],
        "Technology": [
            ("Software Licenses", 0.25, "CRM, project management, productivity tools", "High"),
            ("Cloud Infrastructure", 0.30, "AWS, Azure, Google Cloud hosting", "High"),
            ("Development Tools", 0.15, "IDEs, testing tools, CI/CD", "Medium"),
            ("Cybersecurity", 0.15, "Security software, SSL certificates", "High"),
            ("Website/App Development", 0.10, "Initial development or maintenance", "Medium"),
            ("IT Support", 0.05, "Technical support and maintenance", "Low")
        ],
        "Staffing": [
            ("Salaries", 0.60, "Employee salaries and wages", "High"),
            ("Benefits", 0.15, "Health insurance, retirement plans", "High"),
            ("Recruitment", 0.10, "Hiring costs, job postings", "Medium"),
            ("Training & Development", 0.10, "Employee training programs", "Medium"),
            ("Contractors/Freelancers", 0.05, "External contractors", "Low")
        ],
        "Contingency": [
            ("Emergency Fund", 0.50, "Unexpected expenses and emergencies", "High"),
            ("Market Fluctuations", 0.30, "Buffer for market changes", "Medium"),
            ("Growth Opportunities", 0.20, "Quick response to opportunities", "Low")
        ]
    }
    
    def __init__(self, exchange_rate_service: ExchangeRateService):
        """
        Initialize budget analyzer
        
        Args:
            exchange_rate_service: Exchange rate service for currency conversion
        """
        self.exchange_rate_service = exchange_rate_service
        logger.info("BudgetAnalyzer initialized")
    
    async def analyze_budget(
        self,
        budget_amount: float,
        currency: str,
        business_type: str,
        industry: str
    ) -> BudgetBreakdown:
        """
        Generate comprehensive budget breakdown
        
        Args:
            budget_amount: Total budget amount
            currency: Currency code (INR, USD, EUR)
            business_type: Type of business
            industry: Industry category
            
        Returns:
            BudgetBreakdown with complete allocation
        """
        logger.info(f"Analyzing budget: {budget_amount} {currency} for {business_type} in {industry}")
        
        # Validate budget
        validation = await self.validate_budget(budget_amount, currency)
        if not validation.is_valid:
            logger.warning(f"Budget validation failed: {validation.message}")
        
        # Calculate category allocations
        allocations = self.calculate_allocations(budget_amount, business_type, industry)
        
        # Generate sub-categories for each category
        sub_categories = {}
        for category, allocation in allocations.items():
            sub_cats = self.generate_sub_categories(category, allocation["amount"], business_type)
            sub_categories[category] = sub_cats
        
        # Build category allocation list
        category_list = [
            CategoryAllocation(
                category=cat,
                amount=alloc["amount"],
                percentage=alloc["percentage"],
                rationale=alloc["rationale"]
            )
            for cat, alloc in allocations.items()
        ]
        
        # Get industry benchmarks
        benchmarks = self._get_industry_benchmarks(industry)
        
        # Generate overall rationale
        rationale = self._generate_allocation_rationale(business_type, industry, budget_amount, currency)
        
        breakdown = BudgetBreakdown(
            total_budget=budget_amount,
            currency=currency,
            categories=category_list,
            sub_categories=sub_categories,
            allocation_rationale=rationale,
            industry_benchmarks=benchmarks
        )
        
        logger.info(f"Budget analysis complete for {business_type}")
        return breakdown
    
    async def validate_budget(self, amount: float, currency: str) -> ValidationResult:
        """
        Validate budget amount against thresholds
        
        Args:
            amount: Budget amount
            currency: Currency code
            
        Returns:
            ValidationResult with validation status
        """
        # Convert to INR for validation
        amount_inr = await self.exchange_rate_service.convert_amount(
            amount, currency, "INR"
        )
        
        if amount_inr < self.MIN_BUDGET_INR:
            suggested = await self.exchange_rate_service.convert_amount(
                self.MIN_BUDGET_INR, "INR", currency
            )
            return ValidationResult(
                is_valid=False,
                message=f"Budget is below minimum threshold of ₹{self.MIN_BUDGET_INR:,.0f} INR",
                suggested_minimum=suggested
            )
        
        if amount_inr > self.MAX_BUDGET_INR:
            return ValidationResult(
                is_valid=False,
                message=f"Budget exceeds maximum threshold of ₹{self.MAX_BUDGET_INR:,.0f} INR"
            )
        
        return ValidationResult(
            is_valid=True,
            message="Budget is within acceptable range"
        )
    
    async def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> float:
        """
        Convert between currencies using real-time rates
        
        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            Converted amount
        """
        return await self.exchange_rate_service.convert_amount(
            amount, from_currency, to_currency
        )
    
    def calculate_allocations(
        self,
        budget: float,
        business_type: str,
        industry: str = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate category allocations based on industry benchmarks
        
        Args:
            budget: Total budget amount
            business_type: Type of business
            industry: Industry category (optional)
            
        Returns:
            Dictionary of category allocations
        """
        # Determine which benchmark to use
        benchmark_key = self._get_benchmark_key(business_type, industry)
        benchmarks = self.ALLOCATION_BENCHMARKS.get(benchmark_key, self.ALLOCATION_BENCHMARKS["Default"])
        
        logger.debug(f"Using benchmark: {benchmark_key}")
        
        # Calculate allocations using mid-point of ranges
        allocations = {}
        total_percentage = 0
        
        for category, (min_pct, max_pct) in benchmarks.items():
            # Use mid-point
            percentage = (min_pct + max_pct) / 2
            amount = budget * (percentage / 100)
            
            allocations[category] = {
                "amount": amount,
                "percentage": percentage,
                "min_percentage": min_pct,
                "max_percentage": max_pct,
                "rationale": self._get_category_rationale(category, business_type)
            }
            
            total_percentage += percentage
        
        # Adjust to ensure exactly 100%
        if total_percentage != 100:
            adjustment_factor = 100 / total_percentage
            for category in allocations:
                allocations[category]["percentage"] *= adjustment_factor
                allocations[category]["amount"] = budget * (allocations[category]["percentage"] / 100)
        
        logger.debug(f"Calculated allocations for {len(allocations)} categories")
        return allocations
    
    def generate_sub_categories(
        self,
        category: str,
        allocation: float,
        business_type: str
    ) -> List[SubCategory]:
        """
        Generate itemized sub-categories
        
        Args:
            category: Main category name
            allocation: Total allocation for category
            business_type: Type of business
            
        Returns:
            List of SubCategory items
        """
        template = self.SUB_CATEGORY_TEMPLATES.get(category, [])
        
        sub_categories = []
        for name, percentage, description, priority in template:
            amount = allocation * percentage
            
            sub_cat = SubCategory(
                name=name,
                amount=amount,
                description=description,
                priority=priority
            )
            sub_categories.append(sub_cat)
        
        logger.debug(f"Generated {len(sub_categories)} sub-categories for {category}")
        return sub_categories
    
    def _get_benchmark_key(self, business_type: str, industry: Optional[str]) -> str:
        """
        Determine which benchmark to use based on business type and industry
        
        Args:
            business_type: Type of business
            industry: Industry category
            
        Returns:
            Benchmark key
        """
        # Check industry first
        if industry:
            industry_lower = industry.lower()
            for key in self.ALLOCATION_BENCHMARKS.keys():
                if key.lower() in industry_lower or industry_lower in key.lower():
                    return key
        
        # Check business type
        if business_type:
            business_lower = business_type.lower()
            for key in self.ALLOCATION_BENCHMARKS.keys():
                if key.lower() in business_lower or business_lower in key.lower():
                    return key
        
        return "Default"
    
    def _get_category_rationale(self, category: str, business_type: str) -> str:
        """
        Get rationale for category allocation
        
        Args:
            category: Category name
            business_type: Type of business
            
        Returns:
            Rationale explanation
        """
        rationales = {
            "Marketing": f"Essential for customer acquisition and brand awareness in {business_type}",
            "Operations": f"Core operational costs including facilities, utilities, and day-to-day expenses",
            "Technology": f"Technology infrastructure and tools needed to run {business_type} efficiently",
            "Staffing": f"Human resources including salaries, benefits, and recruitment for {business_type}",
            "Contingency": f"Emergency fund and buffer for unexpected expenses and opportunities"
        }
        
        return rationales.get(category, f"Allocation for {category} based on industry standards")
    
    def _get_industry_benchmarks(self, industry: str) -> Dict[str, str]:
        """
        Get industry benchmark descriptions
        
        Args:
            industry: Industry category
            
        Returns:
            Dictionary of benchmark descriptions
        """
        benchmark_key = self._get_benchmark_key("", industry)
        benchmarks = self.ALLOCATION_BENCHMARKS.get(benchmark_key, self.ALLOCATION_BENCHMARKS["Default"])
        
        descriptions = {}
        for category, (min_pct, max_pct) in benchmarks.items():
            descriptions[category] = f"Industry standard: {min_pct}% - {max_pct}%"
        
        return descriptions
    
    def _generate_allocation_rationale(
        self,
        business_type: str,
        industry: str,
        budget: float,
        currency: str
    ) -> str:
        """
        Generate overall allocation rationale
        
        Args:
            business_type: Type of business
            industry: Industry category
            budget: Total budget
            currency: Currency code
            
        Returns:
            Rationale explanation
        """
        symbol = self.exchange_rate_service.get_currency_symbol(currency)
        formatted_budget = self.exchange_rate_service.format_amount(budget, currency)
        
        rationale = (
            f"This budget breakdown for your {business_type} business in the {industry} industry "
            f"is based on industry benchmarks and best practices. With a total budget of {formatted_budget}, "
            f"we've allocated funds across five key categories to ensure balanced growth and sustainability. "
            f"The allocations prioritize customer acquisition, operational efficiency, and team building "
            f"while maintaining a healthy contingency fund for unexpected expenses."
        )
        
        return rationale
