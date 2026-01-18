"""
PDF Report Generator
Creates professional marketing intelligence reports with charts and insights
"""
import os
import logging
from typing import Dict, Any, List
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#8B5CF6'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#EC4899'),
            spaceBefore=20,
            spaceAfter=12
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            spaceAfter=12
        ))
    
    async def generate_analysis_report(self, analysis: Dict[str, Any]) -> BytesIO:
        """Generate a comprehensive PDF report from analysis data"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title Page
        story.append(Paragraph("AstraMark Intelligence Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            f"Generated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}",
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 0.5*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        story.append(Paragraph(analysis.get('overview', 'N/A'), self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))
        
        # Key Metrics
        story.append(Paragraph("Key Performance Indicators", self.styles['SectionHeader']))
        metrics_data = [
            ['Metric', 'Score'],
            ['Confidence Score', f"{analysis.get('confidence_score', 0)}%"],
            ['Virality Score', f"{analysis.get('virality_score', 0)}/100"],
            ['Retention Score', f"{analysis.get('retention_score', 0)}/100"],
            ['AI Verdict', analysis.get('ai_verdict', 'N/A')]
        ]
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#8B5CF6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F3F4F6')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#E5E7EB'))
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Market Analysis
        story.append(Paragraph("Market Analysis", self.styles['SectionHeader']))
        market = analysis.get('market_analysis', {})
        story.append(Paragraph(f"<b>Market Size:</b> {market.get('market_size', 'N/A')}", self.styles['CustomBody']))
        story.append(Paragraph(f"<b>Growth Rate:</b> {market.get('growth_rate', 'N/A')}", self.styles['CustomBody']))
        story.append(Paragraph(f"<b>Entry Barriers:</b> {market.get('entry_barriers', 'N/A')}", self.styles['CustomBody']))
        story.append(Spacer(1, 0.2*inch))
        
        # SWOT Analysis
        story.append(Paragraph("SWOT Analysis", self.styles['SectionHeader']))
        swot_data = [
            ['Strengths', 'Weaknesses'],
            [
                self._format_list(market.get('strengths', [])),
                self._format_list(market.get('weaknesses', []))
            ],
            ['Opportunities', 'Threats'],
            [
                self._format_list(market.get('opportunities', [])),
                self._format_list(market.get('risks', []))
            ]
        ]
        swot_table = Table(swot_data, colWidths=[3*inch, 3*inch])
        swot_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), HexColor('#10B981')),
            ('BACKGROUND', (1, 0), (1, 0), HexColor('#EF4444')),
            ('BACKGROUND', (0, 2), (0, 2), HexColor('#3B82F6')),
            ('BACKGROUND', (1, 2), (1, 2), HexColor('#F59E0B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('TEXTCOLOR', (0, 2), (-1, 2), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#E5E7EB'))
        ]))
        story.append(swot_table)
        story.append(PageBreak())
        
        # User Personas
        story.append(Paragraph("Target User Personas", self.styles['SectionHeader']))
        for idx, persona in enumerate(analysis.get('user_personas', []), 1):
            story.append(Paragraph(f"<b>Persona {idx}: {persona.get('name', 'N/A')}</b>", self.styles['CustomBody']))
            story.append(Paragraph(f"Demographics: {persona.get('demographics', 'N/A')}", self.styles['CustomBody']))
            story.append(Paragraph(f"Psychographics: {persona.get('psychographics', 'N/A')}", self.styles['CustomBody']))
            story.append(Paragraph(f"<b>Pain Points:</b>", self.styles['CustomBody']))
            for point in persona.get('pain_points', []):
                story.append(Paragraph(f"• {point}", self.styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Marketing Strategies
        story.append(PageBreak())
        story.append(Paragraph("Multi-Channel Marketing Strategies", self.styles['SectionHeader']))
        for strategy in analysis.get('strategies', []):
            story.append(Paragraph(f"<b>{strategy.get('channel', 'N/A')}</b>", self.styles['CustomBody']))
            story.append(Paragraph(strategy.get('strategy', 'N/A'), self.styles['CustomBody']))
            story.append(Paragraph(f"<b>Content Ideas:</b>", self.styles['CustomBody']))
            for idea in strategy.get('content_ideas', []):
                story.append(Paragraph(f"• {idea}", self.styles['CustomBody']))
            story.append(Paragraph(f"<b>Posting Schedule:</b> {strategy.get('posting_schedule', 'N/A')}", self.styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Revenue Projections
        story.append(PageBreak())
        story.append(Paragraph("Revenue Projections", self.styles['SectionHeader']))
        revenue = analysis.get('revenue_projection', {})
        revenue_data = [
            ['Projection Type', 'Amount'],
            ['Minimum Monthly', revenue.get('min_monthly', 'N/A')],
            ['Maximum Monthly', revenue.get('max_monthly', 'N/A')],
            ['Growth Timeline', revenue.get('growth_timeline', 'N/A')]
        ]
        revenue_table = Table(revenue_data, colWidths=[3*inch, 3*inch])
        revenue_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#10B981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#E5E7EB'))
        ]))
        story.append(revenue_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Action Items
        story.append(Paragraph("Critical Action Items", self.styles['SectionHeader']))
        story.append(Paragraph(f"<b>Biggest Opportunity:</b> {analysis.get('biggest_opportunity', 'N/A')}", self.styles['CustomBody']))
        story.append(Paragraph(f"<b>Biggest Risk:</b> {analysis.get('biggest_risk', 'N/A')}", self.styles['CustomBody']))
        story.append(Paragraph(f"<b>Next Action:</b> {analysis.get('next_action', 'N/A')}", self.styles['CustomBody']))
        story.append(Spacer(1, 0.3*inch))
        
        # Blockchain Proof (if available)
        if analysis.get('blockchain_proof'):
            story.append(PageBreak())
            story.append(Paragraph("Blockchain Verification", self.styles['SectionHeader']))
            proof = analysis['blockchain_proof']
            story.append(Paragraph(f"<b>Hash:</b> {proof.get('hash', 'N/A')}", self.styles['CustomBody']))
            story.append(Paragraph(f"<b>Timestamp:</b> {proof.get('timestamp', 'N/A')}", self.styles['CustomBody']))
            story.append(Paragraph(f"<b>Network:</b> {proof.get('network', 'N/A')}", self.styles['CustomBody']))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            "Generated by AstraMark AI Marketing Intelligence Platform",
            self.styles['CustomBody']
        ))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list of items as bullet points"""
        if not items:
            return "N/A"
        return "<br/>".join([f"• {item}" for item in items])

# Singleton instance
pdf_generator = PDFReportGenerator()
