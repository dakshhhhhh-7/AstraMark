"""
Risk Assessment Service - Identifies and analyzes business risks
Provides risk severity, probability, and mitigation strategies
"""
import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class Risk(BaseModel):
    """Individual risk model"""
    risk_id: str
    category: str  # "Market", "Financial", "Operational", "Competitive", "Regulatory"
    title: str
    description: str
    severity: str  # "High", "Medium", "Low"
    probability: str  # "High", "Medium", "Low"
    risk_score: float  # Combined severity and probability (0-10)
    mitigation_strategies: List[str]
    impact_areas: List[str]


class RiskAssessmentResult(BaseModel):
    """Complete risk assessment result"""
    risks: List[Risk]
    total_risk_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    regulatory_requirements: List[str]
    assessment_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RiskAssessment:
    """
    Risk assessment service that identifies business risks
    and provides mitigation strategies
    """
    
    # Risk templates by category
    RISK_TEMPLATES = {
        "Market": [
            {
                "title": "Market Demand Uncertainty",
                "description": "Uncertain customer demand for product/service",
                "severity": "High",
                "probability": "Medium",
                "mitigation": [
                    "Conduct thorough market research and customer validation",
                    "Start with MVP to test market response before full launch",
                    "Implement customer feedback loops for continuous improvement"
                ],
                "impact_areas": ["Revenue", "Growth", "Customer Acquisition"]
            },
            {
                "title": "Market Saturation",
                "description": "Highly competitive market with established players",
                "severity": "Medium",
                "probability": "High",
                "mitigation": [
                    "Differentiate through unique value proposition",
                    "Focus on underserved niche segments",
                    "Build strong brand identity and customer loyalty"
                ],
                "impact_areas": ["Market Share", "Pricing", "Customer Acquisition"]
            },
            {
                "title": "Economic Downturn",
                "description": "Economic recession affecting customer spending",
                "severity": "High",
                "probability": "Low",
                "mitigation": [
                    "Maintain healthy cash reserves and contingency funds",
                    "Diversify revenue streams and customer segments",
                    "Focus on essential value propositions during downturns"
                ],
                "impact_areas": ["Revenue", "Cash Flow", "Customer Retention"]
            }
        ],
        "Financial": [
            {
                "title": "Cash Flow Shortage",
                "description": "Insufficient cash flow to cover operational expenses",
                "severity": "High",
                "probability": "Medium",
                "mitigation": [
                    "Maintain 6-12 months of operating expenses in reserves",
                    "Implement strict cash flow monitoring and forecasting",
                    "Secure credit lines or backup funding sources"
                ],
                "impact_areas": ["Operations", "Staffing", "Growth"]
            },
            {
                "title": "Budget Overruns",
                "description": "Actual costs exceeding budgeted amounts",
                "severity": "Medium",
                "probability": "High",
                "mitigation": [
                    "Implement detailed budget tracking and variance analysis",
                    "Build 10-20% contingency into all budget categories",
                    "Establish approval processes for unplanned expenses"
                ],
                "impact_areas": ["Profitability", "Cash Flow", "Operations"]
            },
            {
                "title": "Funding Shortfall",
                "description": "Unable to secure additional funding when needed",
                "severity": "High",
                "probability": "Medium",
                "mitigation": [
                    "Build relationships with multiple funding sources early",
                    "Achieve key milestones to improve fundability",
                    "Explore alternative funding options (grants, crowdfunding)"
                ],
                "impact_areas": ["Growth", "Operations", "Expansion"]
            }
        ],
        "Operational": [
            {
                "title": "Key Personnel Dependency",
                "description": "Over-reliance on specific individuals or founders",
                "severity": "Medium",
                "probability": "Medium",
                "mitigation": [
                    "Document all critical processes and knowledge",
                    "Cross-train team members on key functions",
                    "Build redundancy in critical roles"
                ],
                "impact_areas": ["Operations", "Continuity", "Growth"]
            },
            {
                "title": "Supply Chain Disruption",
                "description": "Interruptions in supply of goods or services",
                "severity": "High",
                "probability": "Low",
                "mitigation": [
                    "Diversify suppliers and maintain backup options",
                    "Build inventory buffers for critical items",
                    "Establish strong supplier relationships and contracts"
                ],
                "impact_areas": ["Operations", "Customer Satisfaction", "Revenue"]
            },
            {
                "title": "Technology Failures",
                "description": "System outages, data loss, or technical issues",
                "severity": "High",
                "probability": "Medium",
                "mitigation": [
                    "Implement robust backup and disaster recovery systems",
                    "Use reliable cloud infrastructure with SLAs",
                    "Maintain technical support and monitoring"
                ],
                "impact_areas": ["Operations", "Customer Satisfaction", "Reputation"]
            },
            {
                "title": "Scalability Challenges",
                "description": "Inability to scale operations with growth",
                "severity": "Medium",
                "probability": "High",
                "mitigation": [
                    "Design scalable systems and processes from the start",
                    "Use cloud infrastructure that scales automatically",
                    "Plan hiring and training ahead of growth needs"
                ],
                "impact_areas": ["Growth", "Customer Satisfaction", "Operations"]
            }
        ],
        "Competitive": [
            {
                "title": "New Market Entrants",
                "description": "New competitors entering the market",
                "severity": "Medium",
                "probability": "High",
                "mitigation": [
                    "Build strong customer relationships and loyalty programs",
                    "Continuously innovate and improve offerings",
                    "Establish barriers to entry through brand and network effects"
                ],
                "impact_areas": ["Market Share", "Pricing", "Customer Retention"]
            },
            {
                "title": "Price Competition",
                "description": "Competitors engaging in aggressive price cutting",
                "severity": "Medium",
                "probability": "Medium",
                "mitigation": [
                    "Compete on value and differentiation, not just price",
                    "Build premium brand positioning",
                    "Focus on customer experience and service quality"
                ],
                "impact_areas": ["Margins", "Revenue", "Profitability"]
            },
            {
                "title": "Competitive Innovation",
                "description": "Competitors launching superior products/services",
                "severity": "High",
                "probability": "Medium",
                "mitigation": [
                    "Invest in continuous R&D and innovation",
                    "Monitor competitor activities and market trends",
                    "Maintain agility to quickly respond to market changes"
                ],
                "impact_areas": ["Market Share", "Customer Retention", "Revenue"]
            }
        ],
        "Regulatory": [
            {
                "title": "Regulatory Compliance",
                "description": "Failure to comply with industry regulations",
                "severity": "High",
                "probability": "Low",
                "mitigation": [
                    "Engage legal counsel to ensure compliance",
                    "Implement compliance monitoring and reporting systems",
                    "Stay updated on regulatory changes in the industry"
                ],
                "impact_areas": ["Legal", "Operations", "Reputation"]
            },
            {
                "title": "Data Privacy and Security",
                "description": "Data breaches or privacy violations",
                "severity": "High",
                "probability": "Medium",
                "mitigation": [
                    "Implement robust cybersecurity measures and encryption",
                    "Comply with GDPR, CCPA, and other privacy regulations",
                    "Conduct regular security audits and penetration testing"
                ],
                "impact_areas": ["Legal", "Reputation", "Customer Trust"]
            },
            {
                "title": "Licensing and Permits",
                "description": "Missing required business licenses or permits",
                "severity": "Medium",
                "probability": "Low",
                "mitigation": [
                    "Research all required licenses and permits early",
                    "Work with legal advisors to ensure compliance",
                    "Maintain calendar for license renewals"
                ],
                "impact_areas": ["Legal", "Operations"]
            }
        ]
    }
    
    # Industry-specific regulatory requirements
    REGULATORY_REQUIREMENTS = {
        "SaaS": [
            "Data privacy compliance (GDPR, CCPA)",
            "Software licensing and intellectual property protection",
            "Terms of service and privacy policy",
            "Payment processing compliance (PCI DSS if handling payments)"
        ],
        "E-commerce": [
            "Business registration and tax compliance",
            "Consumer protection laws and return policies",
            "Payment gateway compliance (PCI DSS)",
            "Data privacy regulations (GDPR, CCPA)",
            "Product liability insurance"
        ],
        "Retail": [
            "Business license and permits",
            "Sales tax registration and collection",
            "Health and safety regulations",
            "Employment laws and labor compliance",
            "Product safety standards"
        ],
        "Service": [
            "Professional licensing (if applicable)",
            "Business registration and permits",
            "Liability insurance",
            "Contract law compliance",
            "Employment regulations"
        ],
        "Manufacturing": [
            "Manufacturing licenses and permits",
            "Environmental regulations and compliance",
            "Product safety and quality standards",
            "Occupational health and safety (OSHA)",
            "Import/export regulations (if applicable)"
        ],
        "Technology": [
            "Intellectual property protection (patents, trademarks)",
            "Data privacy and security compliance",
            "Software licensing agreements",
            "Export control regulations (for certain technologies)",
            "Industry-specific certifications"
        ],
        "Default": [
            "Business registration and licenses",
            "Tax compliance (income, sales, payroll)",
            "Employment laws and regulations",
            "Data privacy compliance",
            "General liability insurance"
        ]
    }
    
    def __init__(self):
        """Initialize risk assessment service"""
        logger.info("RiskAssessment initialized")
    
    def assess_risks(
        self,
        business_type: str,
        industry: str,
        budget: float,
        geographic_location: str
    ) -> RiskAssessmentResult:
        """
        Identify and assess business risks
        
        Args:
            business_type: Type of business
            industry: Industry category
            budget: Total budget
            geographic_location: Operating location
            
        Returns:
            RiskAssessmentResult with identified risks
        """
        logger.info(f"Assessing risks for {business_type} in {industry}")
        
        # Identify relevant risks (5-15 risks)
        risks = self._identify_risks(business_type, industry, budget, geographic_location)
        
        # Calculate risk scores and sort by priority
        risks = self._calculate_risk_scores(risks)
        risks = sorted(risks, key=lambda r: r.risk_score, reverse=True)
        
        # Limit to 5-15 risks
        risks = risks[:15]
        if len(risks) < 5:
            # Add generic risks if needed
            risks.extend(self._get_generic_risks(5 - len(risks)))
        
        # Count risks by severity
        high_risk_count = sum(1 for r in risks if r.severity == "High")
        medium_risk_count = sum(1 for r in risks if r.severity == "Medium")
        low_risk_count = sum(1 for r in risks if r.severity == "Low")
        
        # Get regulatory requirements
        regulatory_requirements = self._get_regulatory_requirements(business_type, industry, geographic_location)
        
        result = RiskAssessmentResult(
            risks=risks,
            total_risk_count=len(risks),
            high_risk_count=high_risk_count,
            medium_risk_count=medium_risk_count,
            low_risk_count=low_risk_count,
            regulatory_requirements=regulatory_requirements
        )
        
        logger.info(f"Risk assessment complete: {len(risks)} risks identified")
        return result
    
    def _identify_risks(
        self,
        business_type: str,
        industry: str,
        budget: float,
        geographic_location: str
    ) -> List[Risk]:
        """
        Identify relevant risks based on business context
        
        Args:
            business_type: Type of business
            industry: Industry category
            budget: Total budget
            geographic_location: Operating location
            
        Returns:
            List of Risk objects
        """
        risks = []
        risk_counter = 1
        
        # Add risks from each category
        for category, risk_templates in self.RISK_TEMPLATES.items():
            # Select relevant risks for this category
            category_risks = self._select_category_risks(
                category, risk_templates, business_type, industry, budget
            )
            
            for risk_template in category_risks:
                risk = Risk(
                    risk_id=f"RISK-{risk_counter:03d}",
                    category=category,
                    title=risk_template["title"],
                    description=risk_template["description"],
                    severity=risk_template["severity"],
                    probability=risk_template["probability"],
                    risk_score=0.0,  # Will be calculated later
                    mitigation_strategies=risk_template["mitigation"],
                    impact_areas=risk_template["impact_areas"]
                )
                risks.append(risk)
                risk_counter += 1
        
        return risks
    
    def _select_category_risks(
        self,
        category: str,
        risk_templates: List[Dict[str, Any]],
        business_type: str,
        industry: str,
        budget: float
    ) -> List[Dict[str, Any]]:
        """
        Select relevant risks from category based on business context
        
        Args:
            category: Risk category
            risk_templates: Available risk templates
            business_type: Type of business
            industry: Industry category
            budget: Total budget
            
        Returns:
            List of selected risk templates
        """
        # For now, select 2-3 risks per category
        # In a more sophisticated system, this would be context-aware
        
        if category == "Market":
            # Always include market risks
            return risk_templates[:3]
        
        elif category == "Financial":
            # Financial risks depend on budget size
            if budget < 100000:  # Small budget
                return risk_templates[:3]  # All financial risks
            else:
                return risk_templates[:2]  # Fewer risks for larger budgets
        
        elif category == "Operational":
            # Operational risks vary by business type
            if "technology" in business_type.lower() or "saas" in business_type.lower():
                return [risk_templates[2], risk_templates[3]]  # Tech and scalability
            else:
                return risk_templates[:2]  # General operational risks
        
        elif category == "Competitive":
            # Competitive risks are always relevant
            return risk_templates[:2]
        
        elif category == "Regulatory":
            # Regulatory risks depend on industry
            return risk_templates[:2]
        
        return risk_templates[:2]  # Default: 2 risks per category
    
    def _calculate_risk_scores(self, risks: List[Risk]) -> List[Risk]:
        """
        Calculate risk scores based on severity and probability
        
        Args:
            risks: List of risks
            
        Returns:
            List of risks with calculated scores
        """
        severity_scores = {"High": 3, "Medium": 2, "Low": 1}
        probability_scores = {"High": 3, "Medium": 2, "Low": 1}
        
        for risk in risks:
            severity_score = severity_scores.get(risk.severity, 2)
            probability_score = probability_scores.get(risk.probability, 2)
            
            # Risk score = (severity * probability) normalized to 0-10
            risk.risk_score = ((severity_score * probability_score) / 9) * 10
        
        return risks
    
    def _get_generic_risks(self, count: int) -> List[Risk]:
        """
        Get generic risks to fill minimum requirement
        
        Args:
            count: Number of generic risks needed
            
        Returns:
            List of generic Risk objects
        """
        generic_risks = []
        
        generic_templates = [
            {
                "category": "Market",
                "title": "Customer Acquisition Cost",
                "description": "Higher than expected costs to acquire customers",
                "severity": "Medium",
                "probability": "Medium",
                "mitigation": [
                    "Test multiple marketing channels to find most cost-effective",
                    "Optimize conversion funnel to reduce CAC"
                ],
                "impact_areas": ["Profitability", "Growth"]
            },
            {
                "category": "Operational",
                "title": "Quality Control Issues",
                "description": "Product or service quality not meeting standards",
                "severity": "Medium",
                "probability": "Low",
                "mitigation": [
                    "Implement quality assurance processes",
                    "Gather and act on customer feedback"
                ],
                "impact_areas": ["Customer Satisfaction", "Reputation"]
            }
        ]
        
        for i, template in enumerate(generic_templates[:count]):
            risk = Risk(
                risk_id=f"RISK-GEN-{i+1:02d}",
                category=template["category"],
                title=template["title"],
                description=template["description"],
                severity=template["severity"],
                probability=template["probability"],
                risk_score=4.0,
                mitigation_strategies=template["mitigation"],
                impact_areas=template["impact_areas"]
            )
            generic_risks.append(risk)
        
        return generic_risks
    
    def _get_regulatory_requirements(
        self,
        business_type: str,
        industry: str,
        geographic_location: str
    ) -> List[str]:
        """
        Get regulatory requirements for business
        
        Args:
            business_type: Type of business
            industry: Industry category
            geographic_location: Operating location
            
        Returns:
            List of regulatory requirements
        """
        # Find matching requirements
        requirements = []
        
        # Check industry
        for key in self.REGULATORY_REQUIREMENTS.keys():
            if key.lower() in industry.lower() or industry.lower() in key.lower():
                requirements = self.REGULATORY_REQUIREMENTS[key].copy()
                break
        
        # Check business type if no industry match
        if not requirements:
            for key in self.REGULATORY_REQUIREMENTS.keys():
                if key.lower() in business_type.lower() or business_type.lower() in key.lower():
                    requirements = self.REGULATORY_REQUIREMENTS[key].copy()
                    break
        
        # Default requirements
        if not requirements:
            requirements = self.REGULATORY_REQUIREMENTS["Default"].copy()
        
        # Add location-specific requirements
        if "india" in geographic_location.lower():
            requirements.append("GST registration and compliance")
            requirements.append("Shop and Establishment Act registration")
        elif "us" in geographic_location.lower() or "usa" in geographic_location.lower():
            requirements.append("Federal and state tax registration")
            requirements.append("Business entity formation (LLC, Corporation, etc.)")
        
        return requirements
