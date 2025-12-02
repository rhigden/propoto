"""
Agent Output Quality Tests

Validates that agent outputs meet quality standards:
- Proposal structure completeness
- Pricing tier validation
- Entity extraction quality
- Lead scoring logic
"""

import pytest
from agents.proposal_agent import ProposalOutput, PricingTier
from agents.knowledge import KnowledgeOutput, Entity
from agents.sales import SalesOutput, Lead


class TestProposalOutputQuality:
    """Test proposal agent output quality."""
    
    def test_proposal_has_all_sections(self):
        """Validate that proposal has all 6 required sections."""
        proposal = ProposalOutput(
            executive_summary="Test summary",
            current_situation="Test situation",
            proposed_strategy="Test strategy",
            why_us="Test authority",
            investment=[
                PricingTier(name="Starter", price="$1k", features=["Feature 1"]),
                PricingTier(name="Growth", price="$5k", features=["Feature 2"]),
                PricingTier(name="Enterprise", price="$10k", features=["Feature 3"])
            ],
            next_steps="Test CTA"
        )
        
        assert proposal.executive_summary
        assert proposal.current_situation
        assert proposal.proposed_strategy
        assert proposal.why_us
        assert proposal.investment
        assert proposal.next_steps
    
    def test_proposal_has_exactly_three_tiers(self):
        """Validate that proposal has exactly 3 pricing tiers."""
        proposal = ProposalOutput(
            executive_summary="Test",
            current_situation="Test",
            proposed_strategy="Test",
            why_us="Test",
            investment=[
                PricingTier(name="Tier 1", price="$1", features=[]),
                PricingTier(name="Tier 2", price="$2", features=[]),
                PricingTier(name="Tier 3", price="$3", features=[])
            ],
            next_steps="Test"
        )
        
        assert len(proposal.investment) == 3
    
    def test_pricing_tier_structure(self):
        """Validate pricing tier has required fields."""
        tier = PricingTier(
            name="Starter",
            price="$1,000/mo",
            features=["Feature 1", "Feature 2"]
        )
        
        assert tier.name
        assert tier.price
        assert isinstance(tier.features, list)
        assert len(tier.features) > 0
    
    def test_executive_summary_length(self):
        """Validate executive summary is reasonable length (2-3 sentences)."""
        proposal = ProposalOutput(
            executive_summary="This is sentence one. This is sentence two. This is sentence three.",
            current_situation="Test",
            proposed_strategy="Test",
            why_us="Test",
            investment=[
                PricingTier(name="Tier 1", price="$1", features=[])
            ] * 3,
            next_steps="Test"
        )
        
        # Should have multiple sentences (rough check)
        sentences = proposal.executive_summary.split('.')
        assert len([s for s in sentences if s.strip()]) >= 2


class TestKnowledgeOutputQuality:
    """Test knowledge agent output quality."""
    
    def test_knowledge_has_summary(self):
        """Validate knowledge output has summary."""
        knowledge = KnowledgeOutput(
            summary="Test summary",
            entities=[],
            relevance_score=5
        )
        
        assert knowledge.summary
        assert len(knowledge.summary) > 0
    
    def test_relevance_score_range(self):
        """Validate relevance score is between 1-10."""
        knowledge = KnowledgeOutput(
            summary="Test",
            entities=[],
            relevance_score=5
        )
        
        assert 1 <= knowledge.relevance_score <= 10
    
    def test_entity_structure(self):
        """Validate entity has required fields."""
        entity = Entity(
            name="Test Entity",
            type="competitor",
            details="Test details"
        )
        
        assert entity.name
        assert entity.type
        assert entity.details
    
    def test_entity_types(self):
        """Validate entity types are valid."""
        valid_types = ["competitor", "feature", "pricing", "other"]
        
        for entity_type in valid_types:
            entity = Entity(
                name="Test",
                type=entity_type,
                details="Test"
            )
            assert entity.type in valid_types


class TestSalesOutputQuality:
    """Test sales agent output quality."""
    
    def test_sales_has_market_summary(self):
        """Validate sales output has market summary."""
        sales = SalesOutput(
            leads=[],
            market_summary="Test summary"
        )
        
        assert sales.market_summary
        assert len(sales.market_summary) > 0
    
    def test_lead_structure(self):
        """Validate lead has required fields."""
        lead = Lead(
            company_name="Acme Corp",
            website="https://acme.com",
            description="Test description",
            score=75,
            status="new"
        )
        
        assert lead.company_name
        assert lead.description
        assert 0 <= lead.score <= 100
        assert lead.status in ["new", "contacted", "qualified"]
    
    def test_lead_score_range(self):
        """Validate lead score is between 0-100."""
        lead = Lead(
            company_name="Test",
            website="https://test.com",
            description="Test",
            score=50,
            status="new"
        )
        
        assert 0 <= lead.score <= 100

