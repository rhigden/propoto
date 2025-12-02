# Transcript / Detailed Summary: "How I'd Make $5K with Agentic Workflows (Top 3 Ways)"
**Date**: November 27, 2025
**Creator**: Nick Saraev

> **Note**: This document is a comprehensive summary and reconstruction of key points from the video, as a direct verbatim transcript was not available.

## 1. Introduction
Nick Saraev outlines practical, revenue-generating "agentic workflows" that can be built and sold to businesses or used to generate income directly. The focus is on high-value, specific problems that businesses face.

## 2. Workflow #1: The AI Proposal Generator
**Revenue Potential**: $1,500 - $5,000 per setup (sold to agencies/businesses).

### The Problem
Agencies spend hours writing proposals. Generic templates don't convert, and fully custom proposals are too time-consuming.

### The Solution
An n8n workflow that automates the creation of highly personalized proposals.

### How It Works
1.  **Input**: A form (e.g., Typeform) collects prospect data (LinkedIn URL, Company Name, Pain Points).
2.  **Scraping**: The workflow uses a tool (like PhantomBuster or a custom scraper) to scrape the prospect's LinkedIn profile and company website.
3.  **Analysis**: AI (GPT-4 or Claude) analyzes the scraped data to understand the prospect's tone, recent posts, and company values.
4.  **Generation**: The AI edits specific sections of a proposal template:
    - **Subject Line**: Personalized to catch attention.
    - **Icebreaker**: References recent activity or shared interests.
    - **Elevator Pitch**: Tailors the value prop to their specific industry/pain points.
    - **Call to Action (CTA)**: Customized low-friction ask.
    - **P.S.**: A personal touch to build rapport.
5.  **Output**: A draft proposal is created in Google Docs or sent directly to the sales team for final review.

### Key Insight
"Effective systems are often rigid." You don't need a fully autonomous agent that writes everything from scratch. You need a reliable workflow that modifies specific variables within a proven structure.

## 3. Workflow #2: The Facebook Ads Spy Tool
**Revenue Potential**: $2,000+ (sold to marketing agencies) or used for own lead gen.

### The Problem
Marketing agencies need to constantly monitor competitor ads to see what's working. Manual checking is slow and unscalable.

### The Solution
An automated system that scrapes, analyzes, and summarizes competitor ad strategies.

### How It Works
1.  **Trigger**: User inputs a Facebook Ad Library search URL.
2.  **Scraping**: The workflow uses **Apify** to scrape all active ads from that URL.
3.  **Processing**:
    - Categorizes ads (Video, Image, Carousel).
    - Extracts ad copy.
4.  **AI Analysis**:
    - **GPT-4** analyzes the hooks, angles, and value propositions.
    - Identifies common themes (e.g., "UGC style," "Fear of missing out").
    - Rewrites ad copy to create new variations for testing.
5.  **Output**: A report or dashboard (e.g., Airtable) showing top-performing competitor angles and suggested new ad copy.

### Key Insight
This allows agencies to "parasite" successful strategies and iterate faster than competitors.

## 4. Workflow #3: Advanced Web Scraping & Lead Enrichment
**Revenue Potential**: Recurring revenue (Lead Gen Service) or High-Ticket Setup.

### The Problem
Generic lead lists are low quality. Businesses need verified, enriched data to make sales.

### The Solution
A multi-step scraping and enrichment workflow using n8n and AI.

### How It Works
1.  **Source**: Scrape listings from platforms like Fiverr, Upwork, or Google Maps.
2.  **Extraction**: Use **Claude 3.5 Sonnet** to parse unstructured text.
    - *Example*: Extracting email addresses buried in long descriptions or "About Us" pages.
    - *Prompting*: "Find the email address in this text. If none, return null."
3.  **Enrichment**:
    - Cross-reference with LinkedIn to find decision-makers.
    - Verify emails using tools like NeverBounce.
4.  **Action**: Automatically add to a cold outreach campaign (e.g., Instantly.ai).

### Key Insight
The value is in the **data quality**. AI allows you to structure unstructured data that traditional scrapers miss.

## 5. Conclusion
- **Don't overcomplicate**: Start with a specific business problem.
- **Sell the Outcome**: Clients buy "more sales calls" or "saved time," not "n8n workflows."
- **Price on Value**: If a system saves a sales rep 10 hours a week, price it accordingly.
