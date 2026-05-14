"""
Growth Strategy Service - Generates growth strategies and action plans
Provides phased growth roadmap with milestones and KPIs
"""
import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class Milestone(BaseModel):
    """Growth milestone"""
    milestone_id: str
    title: str
    description: str
    target_completion: str  # e.g., "Month 3", "Q2 Year 1"
    success_criteria: List[str]
    dependencies: List[str] = []


class GrowthPhase(BaseModel):
    """Growth phase (Launch, Growth, Scale)"""
    phase_name: str
    phase_number: int
    duration: str
    objectives: List[str]
    milestones: List[Milestone]
    key_activities: List[str]
    resource_requirements: List[str]


class CustomerAcquisitionStrategy(BaseModel):
    """Customer acquisition strategy"""
    channel: str
    description: str
    estimated_cost: float
    expected_conversion_rate: float  # Percentage
    priority: str  # "High", "Medium", "Low"
    timeline: str


class KPI(BaseModel):
    """Key Performance Indicator"""
    kpi_name: str
    description: str
    target_value: str
    measurement_frequency: str  # "Daily", "Weekly", "Monthly"
    phase: str  # Which phase this KPI is most relevant for


class ActionItem(BaseModel):
    """90-day action plan item"""
    action_id: str
    title: str
    description: str
    priority: str  # "High", "Medium", "Low"
    estimated_effort: str  # "1 day", "1 week", "2 weeks"
    deadline: str  # "Week 1", "Week 4", etc.
    owner: str  # Role responsible
    dependencies: List[str] = []


class GrowthStrategyResult(BaseModel):
    """Complete growth strategy result"""
    growth_phases: List[GrowthPhase]
    customer_acquisition_strategies: List[CustomerAcquisitionStrategy]
    kpis: List[KPI]
    action_plan_90_days: List[ActionItem]
    strategy_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GrowthStrategy:
    """
    Growth strategy service that generates phased growth roadmaps
    with milestones, KPIs, and actionable plans
    """
    
    def __init__(self):
        """Initialize growth strategy service"""
        logger.info("GrowthStrategy initialized")
    
    def generate_strategy(
        self,
        business_type: str,
        industry: str,
        budget: float,
        target_market: str,
        geographic_location: str
    ) -> GrowthStrategyResult:
        """
        Generate comprehensive growth strategy
        
        Args:
            business_type: Type of business
            industry: Industry category
            budget: Total budget
            target_market: Target market segment
            geographic_location: Operating location
            
        Returns:
            GrowthStrategyResult with complete strategy
        """
        logger.info(f"Generating growth strategy for {business_type} in {industry}")
        
        # Generate 3 growth phases
        growth_phases = self._generate_growth_phases(business_type, industry, budget)
        
        # Generate customer acquisition strategies
        acquisition_strategies = self._generate_acquisition_strategies(
            business_type, industry, budget, target_market
        )
        
        # Generate KPIs
        kpis = self._generate_kpis(business_type, industry)
        
        # Generate 90-day action plan
        action_plan = self._generate_90_day_action_plan(
            business_type, industry, budget, growth_phases[0]
        )
        
        result = GrowthStrategyResult(
            growth_phases=growth_phases,
            customer_acquisition_strategies=acquisition_strategies,
            kpis=kpis,
            action_plan_90_days=action_plan
        )
        
        logger.info("Growth strategy generated successfully")
        return result
    
    def _generate_growth_phases(
        self,
        business_type: str,
        industry: str,
        budget: float
    ) -> List[GrowthPhase]:
        """
        Generate 3 growth phases: Launch, Growth, Scale
        
        Args:
            business_type: Type of business
            industry: Industry category
            budget: Total budget
            
        Returns:
            List of GrowthPhase objects
        """
        phases = []
        
        # Phase 1: Launch (Months 0-6)
        launch_phase = GrowthPhase(
            phase_name="Launch",
            phase_number=1,
            duration="Months 0-6",
            objectives=[
                "Establish business foundation and legal structure",
                "Develop and launch minimum viable product (MVP)",
                "Acquire first 100 customers",
                "Validate product-market fit",
                "Build core team and processes"
            ],
            milestones=[
                Milestone(
                    milestone_id="M1-1",
                    title="Business Registration Complete",
                    description="Complete all legal registrations, licenses, and permits",
                    target_completion="Month 1",
                    success_criteria=[
                        "Business entity registered",
                        "Tax registrations complete",
                        "Required licenses obtained"
                    ]
                ),
                Milestone(
                    milestone_id="M1-2",
                    title="MVP Launch",
                    description="Launch minimum viable product to initial customers",
                    target_completion="Month 3",
                    success_criteria=[
                        "Core features developed and tested",
                        "Initial marketing materials ready",
                        "First 10 customers onboarded"
                    ],
                    dependencies=["M1-1"]
                ),
                Milestone(
                    milestone_id="M1-3",
                    title="Product-Market Fit Validation",
                    description="Validate that product meets market needs",
                    target_completion="Month 6",
                    success_criteria=[
                        "100+ customers acquired",
                        "Positive customer feedback (NPS > 30)",
                        "Repeat purchase or retention rate > 40%"
                    ],
                    dependencies=["M1-2"]
                )
            ],
            key_activities=[
                "Set up business infrastructure (office, tools, systems)",
                "Develop MVP with core features",
                "Launch initial marketing campaigns",
                "Onboard first customers and gather feedback",
                "Iterate product based on customer insights",
                "Build foundational team (2-5 people)"
            ],
            resource_requirements=[
                "Founders/core team (full-time)",
                "Product development resources",
                "Initial marketing budget (20-30% of total)",
                "Basic operational infrastructure"
            ]
        )
        phases.append(launch_phase)
        
        # Phase 2: Growth (Months 7-18)
        growth_phase = GrowthPhase(
            phase_name="Growth",
            phase_number=2,
            duration="Months 7-18",
            objectives=[
                "Scale customer acquisition to 1,000+ customers",
                "Optimize unit economics and profitability",
                "Expand product features and offerings",
                "Build scalable processes and systems",
                "Grow team to 10-20 people"
            ],
            milestones=[
                Milestone(
                    milestone_id="M2-1",
                    title="1,000 Customers Milestone",
                    description="Reach 1,000 active customers",
                    target_completion="Month 12",
                    success_criteria=[
                        "1,000+ active customers",
                        "Monthly recurring revenue established",
                        "Customer acquisition cost optimized"
                    ]
                ),
                Milestone(
                    milestone_id="M2-2",
                    title="Break-Even Achievement",
                    description="Achieve monthly break-even or profitability",
                    target_completion="Month 15",
                    success_criteria=[
                        "Monthly revenue covers monthly costs",
                        "Positive contribution margin",
                        "Clear path to profitability"
                    ],
                    dependencies=["M2-1"]
                ),
                Milestone(
                    milestone_id="M2-3",
                    title="Product Expansion",
                    description="Launch additional features or product lines",
                    target_completion="Month 18",
                    success_criteria=[
                        "New features launched based on customer demand",
                        "Increased customer lifetime value",
                        "Improved retention rates"
                    ]
                )
            ],
            key_activities=[
                "Scale marketing across multiple channels",
                "Optimize sales and conversion funnels",
                "Expand product features and capabilities",
                "Build customer success and support teams",
                "Implement data analytics and tracking",
                "Hire key team members (sales, marketing, product)"
            ],
            resource_requirements=[
                "Expanded team (10-20 people)",
                "Increased marketing budget (30-40% of revenue)",
                "Product development resources",
                "Customer support infrastructure",
                "Data and analytics tools"
            ]
        )
        phases.append(growth_phase)
        
        # Phase 3: Scale (Months 19-36)
        scale_phase = GrowthPhase(
            phase_name="Scale",
            phase_number=3,
            duration="Months 19-36",
            objectives=[
                "Achieve 10,000+ customers and market leadership",
                "Expand to new markets or geographies",
                "Build sustainable competitive advantages",
                "Achieve strong profitability and unit economics",
                "Prepare for next stage (funding, acquisition, IPO)"
            ],
            milestones=[
                Milestone(
                    milestone_id="M3-1",
                    title="10,000 Customers Milestone",
                    description="Reach 10,000 active customers",
                    target_completion="Month 24",
                    success_criteria=[
                        "10,000+ active customers",
                        "Strong brand recognition in target market",
                        "Efficient customer acquisition machine"
                    ]
                ),
                Milestone(
                    milestone_id="M3-2",
                    title="Market Expansion",
                    description="Successfully expand to new markets or segments",
                    target_completion="Month 30",
                    success_criteria=[
                        "Launched in 2+ new markets/segments",
                        "Diversified revenue streams",
                        "Proven expansion playbook"
                    ],
                    dependencies=["M3-1"]
                ),
                Milestone(
                    milestone_id="M3-3",
                    title="Sustainable Profitability",
                    description="Achieve consistent monthly profitability",
                    target_completion="Month 36",
                    success_criteria=[
                        "6+ months of consecutive profitability",
                        "Healthy profit margins (>20%)",
                        "Strong cash flow generation"
                    ]
                )
            ],
            key_activities=[
                "Expand to new markets and customer segments",
                "Build strategic partnerships and alliances",
                "Invest in brand building and thought leadership",
                "Optimize operations for efficiency and scale",
                "Develop advanced product features and innovation",
                "Build executive team and organizational structure"
            ],
            resource_requirements=[
                "Mature team (20-50+ people)",
                "Significant marketing and sales investment",
                "Advanced technology infrastructure",
                "Executive leadership team",
                "Strategic partnerships and alliances"
            ]
        )
        phases.append(scale_phase)
        
        return phases
    
    def _generate_acquisition_strategies(
        self,
        business_type: str,
        industry: str,
        budget: float,
        target_market: str
    ) -> List[CustomerAcquisitionStrategy]:
        """
        Generate customer acquisition strategies
        
        Args:
            business_type: Type of business
            industry: Industry category
            budget: Total budget
            target_market: Target market segment
            
        Returns:
            List of CustomerAcquisitionStrategy objects
        """
        # Calculate marketing budget (assume 25-30% of total budget)
        marketing_budget = budget * 0.275
        
        strategies = [
            CustomerAcquisitionStrategy(
                channel="Content Marketing & SEO",
                description="Create valuable content (blogs, videos, guides) optimized for search engines to attract organic traffic",
                estimated_cost=marketing_budget * 0.20,
                expected_conversion_rate=2.5,
                priority="High",
                timeline="Ongoing from Month 1"
            ),
            CustomerAcquisitionStrategy(
                channel="Social Media Advertising",
                description="Paid advertising on Facebook, Instagram, LinkedIn targeting specific demographics",
                estimated_cost=marketing_budget * 0.30,
                expected_conversion_rate=3.0,
                priority="High",
                timeline="Start Month 2, scale in Month 4+"
            ),
            CustomerAcquisitionStrategy(
                channel="Search Engine Marketing (SEM)",
                description="Google Ads and Bing Ads targeting high-intent keywords",
                estimated_cost=marketing_budget * 0.25,
                expected_conversion_rate=4.0,
                priority="High",
                timeline="Start Month 3, optimize ongoing"
            ),
            CustomerAcquisitionStrategy(
                channel="Email Marketing",
                description="Build email list and nurture leads through automated campaigns",
                estimated_cost=marketing_budget * 0.10,
                expected_conversion_rate=5.0,
                priority="Medium",
                timeline="Start Month 2, grow list continuously"
            ),
            CustomerAcquisitionStrategy(
                channel="Referral Program",
                description="Incentivize existing customers to refer new customers",
                estimated_cost=marketing_budget * 0.10,
                expected_conversion_rate=8.0,
                priority="Medium",
                timeline="Launch Month 6 after initial customer base"
            ),
            CustomerAcquisitionStrategy(
                channel="Strategic Partnerships",
                description="Partner with complementary businesses for co-marketing and referrals",
                estimated_cost=marketing_budget * 0.05,
                expected_conversion_rate=6.0,
                priority="Low",
                timeline="Develop from Month 6 onwards"
            )
        ]
        
        return strategies
    
    def _generate_kpis(
        self,
        business_type: str,
        industry: str
    ) -> List[KPI]:
        """
        Generate key performance indicators
        
        Args:
            business_type: Type of business
            industry: Industry category
            
        Returns:
            List of KPI objects
        """
        kpis = [
            # Launch Phase KPIs
            KPI(
                kpi_name="Customer Acquisition",
                description="Number of new customers acquired per month",
                target_value="100 in Month 6, 200+ in Month 12",
                measurement_frequency="Weekly",
                phase="Launch"
            ),
            KPI(
                kpi_name="Customer Acquisition Cost (CAC)",
                description="Average cost to acquire one customer",
                target_value="< 20% of Customer Lifetime Value",
                measurement_frequency="Monthly",
                phase="Launch"
            ),
            KPI(
                kpi_name="Product Engagement",
                description="Active usage of product/service by customers",
                target_value="60%+ weekly active users",
                measurement_frequency="Daily",
                phase="Launch"
            ),
            
            # Growth Phase KPIs
            KPI(
                kpi_name="Monthly Recurring Revenue (MRR)",
                description="Predictable monthly revenue from customers",
                target_value="20%+ month-over-month growth",
                measurement_frequency="Monthly",
                phase="Growth"
            ),
            KPI(
                kpi_name="Customer Retention Rate",
                description="Percentage of customers retained over time",
                target_value=">80% monthly retention",
                measurement_frequency="Monthly",
                phase="Growth"
            ),
            KPI(
                kpi_name="Net Promoter Score (NPS)",
                description="Customer satisfaction and likelihood to recommend",
                target_value="NPS > 50",
                measurement_frequency="Quarterly",
                phase="Growth"
            ),
            KPI(
                kpi_name="Conversion Rate",
                description="Percentage of leads that become customers",
                target_value="3-5% across all channels",
                measurement_frequency="Weekly",
                phase="Growth"
            ),
            
            # Scale Phase KPIs
            KPI(
                kpi_name="Customer Lifetime Value (LTV)",
                description="Total revenue expected from a customer over their lifetime",
                target_value="LTV:CAC ratio > 3:1",
                measurement_frequency="Monthly",
                phase="Scale"
            ),
            KPI(
                kpi_name="Gross Margin",
                description="Revenue minus cost of goods sold",
                target_value=">60% gross margin",
                measurement_frequency="Monthly",
                phase="Scale"
            ),
            KPI(
                kpi_name="Net Profit Margin",
                description="Percentage of revenue that becomes profit",
                target_value=">20% net margin",
                measurement_frequency="Monthly",
                phase="Scale"
            ),
            KPI(
                kpi_name="Market Share",
                description="Percentage of total addressable market captured",
                target_value="1-5% of TAM by Month 36",
                measurement_frequency="Quarterly",
                phase="Scale"
            )
        ]
        
        return kpis
    
    def _generate_90_day_action_plan(
        self,
        business_type: str,
        industry: str,
        budget: float,
        launch_phase: GrowthPhase
    ) -> List[ActionItem]:
        """
        Generate prioritized 90-day action plan
        
        Args:
            business_type: Type of business
            industry: Industry category
            budget: Total budget
            launch_phase: Launch phase for context
            
        Returns:
            List of ActionItem objects
        """
        actions = [
            # Week 1-2: Foundation
            ActionItem(
                action_id="A001",
                title="Complete Business Registration",
                description="Register business entity, obtain EIN/tax ID, open business bank account",
                priority="High",
                estimated_effort="1 week",
                deadline="Week 2",
                owner="Founder/CEO"
            ),
            ActionItem(
                action_id="A002",
                title="Set Up Accounting System",
                description="Implement accounting software (QuickBooks, Xero) and set up chart of accounts",
                priority="High",
                estimated_effort="3 days",
                deadline="Week 2",
                owner="Founder/CFO",
                dependencies=["A001"]
            ),
            ActionItem(
                action_id="A003",
                title="Obtain Required Licenses",
                description="Research and apply for all necessary business licenses and permits",
                priority="High",
                estimated_effort="1 week",
                deadline="Week 3",
                owner="Founder/Legal"
            ),
            
            # Week 3-4: Product & Infrastructure
            ActionItem(
                action_id="A004",
                title="Define MVP Features",
                description="Finalize minimum viable product feature set based on customer research",
                priority="High",
                estimated_effort="1 week",
                deadline="Week 4",
                owner="Product Manager/Founder"
            ),
            ActionItem(
                action_id="A005",
                title="Set Up Technology Infrastructure",
                description="Set up cloud hosting, development tools, and core technology stack",
                priority="High",
                estimated_effort="1 week",
                deadline="Week 4",
                owner="CTO/Tech Lead"
            ),
            ActionItem(
                action_id="A006",
                title="Create Brand Identity",
                description="Design logo, color scheme, brand guidelines, and initial marketing materials",
                priority="Medium",
                estimated_effort="2 weeks",
                deadline="Week 5",
                owner="Marketing Lead"
            ),
            
            # Week 5-8: Development & Marketing
            ActionItem(
                action_id="A007",
                title="Develop MVP Core Features",
                description="Build and test core product features for initial launch",
                priority="High",
                estimated_effort="4 weeks",
                deadline="Week 8",
                owner="Development Team",
                dependencies=["A004", "A005"]
            ),
            ActionItem(
                action_id="A008",
                title="Build Website and Landing Pages",
                description="Create professional website with clear value proposition and conversion paths",
                priority="High",
                estimated_effort="2 weeks",
                deadline="Week 6",
                owner="Marketing/Web Developer",
                dependencies=["A006"]
            ),
            ActionItem(
                action_id="A009",
                title="Set Up Analytics and Tracking",
                description="Implement Google Analytics, conversion tracking, and key metrics dashboard",
                priority="High",
                estimated_effort="1 week",
                deadline="Week 6",
                owner="Marketing/Analytics",
                dependencies=["A008"]
            ),
            ActionItem(
                action_id="A010",
                title="Create Content Marketing Plan",
                description="Develop 90-day content calendar with blog posts, social media, and SEO strategy",
                priority="Medium",
                estimated_effort="1 week",
                deadline="Week 7",
                owner="Content Marketing Lead"
            ),
            
            # Week 9-12: Launch & Acquisition
            ActionItem(
                action_id="A011",
                title="Conduct Beta Testing",
                description="Recruit 10-20 beta users to test MVP and provide feedback",
                priority="High",
                estimated_effort="2 weeks",
                deadline="Week 10",
                owner="Product Manager",
                dependencies=["A007"]
            ),
            ActionItem(
                action_id="A012",
                title="Launch MVP to Public",
                description="Official product launch with press release and marketing campaign",
                priority="High",
                estimated_effort="1 week",
                deadline="Week 11",
                owner="Founder/Marketing",
                dependencies=["A011"]
            ),
            ActionItem(
                action_id="A013",
                title="Start Paid Advertising Campaigns",
                description="Launch initial Google Ads and social media advertising campaigns",
                priority="High",
                estimated_effort="1 week",
                deadline="Week 11",
                owner="Marketing Lead",
                dependencies=["A008", "A009"]
            ),
            ActionItem(
                action_id="A014",
                title="Implement Customer Feedback Loop",
                description="Set up systems to collect, analyze, and act on customer feedback",
                priority="Medium",
                estimated_effort="1 week",
                deadline="Week 12",
                owner="Product Manager",
                dependencies=["A012"]
            ),
            ActionItem(
                action_id="A015",
                title="Hire First Team Members",
                description="Recruit and onboard 1-2 key team members (sales, support, or development)",
                priority="Medium",
                estimated_effort="4 weeks",
                deadline="Week 12",
                owner="Founder/HR"
            )
        ]
        
        return actions
