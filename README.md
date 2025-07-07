# CASQE - Context-Aware Search Query Enrichment

A generic, domain-agnostic search query enrichment system that automatically generates comprehensive search variations using contextual knowledge and AI-powered insights.

> **Note**: This module does not perform the search itself. It enriches queries to be used with search engines or search APIs later on.

## 🎯 What Problem Does CASQE Solve?

When researching any topic—whether it's a product, company, person, or technology—most people start with basic queries but struggle to think of all the effective ways to search. CASQE automates the expertise of skilled researchers by systematically generating targeted, context-aware search variations.

## ✨ Key Features

- **Universal Applicability**: Works for any search target (products, companies, people, technologies, research topics)
- **Dual Enrichment Strategies**: 
  - **Basic Enrichment**: Combinatorial approach using identifiers, platforms, and entities
  - **Advanced Enrichment**: AI-powered natural language query generation
- **Contextual Intelligence**: Uses provided context to generate relevant, high-value search variations
- **Scoring System**: Each enriched query gets a relevance score and explanation
- **Flexible Configuration**: Customizable enrichment strategies and output limits

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from casqe.query_enricher import SearchQueryEnricher
from casqe.schemes import SearchQueryEnrichmentRequestObject

# Initialize the enricher
enricher = SearchQueryEnricher()

# Create a request object
request = SearchQueryEnrichmentRequestObject(
    query="Tesla Model Y",
    identifier_context="Electric SUV manufactured by Tesla, competitor to BMW iX",
    search_reason_context="Find detailed technical specifications and reviews",
    how_many=10,
    use_basic_enrichment=True,
    use_advanced_enrichment=True
)

# Generate enriched queries
enriched_queries = enricher.enrich(request)

# Print results
for query in enriched_queries:
    print(f"{query.query} (score: {query.score:.3f}) - {query.explanation}")
```

## 📖 Usage Examples

### Product Research
```python
request = SearchQueryEnrichmentRequestObject(
    query="iPhone 15 Pro",
    identifier_context="Apple's flagship smartphone, A17 Pro chip, titanium build",
    search_reason_context="Compare with competitors and find detailed reviews",
    how_many=8,
    use_advanced_enrichment=True
)
```

**Sample Output:**
- `iPhone 15 Pro vs Samsung Galaxy S24 comparison` (score: 0.92)
- `iPhone 15 Pro titanium durability test` (score: 0.87) 
- `A17 Pro chip benchmarks performance` (score: 0.85)

### Company Research
```python
request = SearchQueryEnrichmentRequestObject(
    query="Anthropic",
    identifier_context="AI safety company founded 2021, creates Claude AI assistant",
    search_reason_context="Research business model and competitive landscape",
    how_many=10,
    use_basic_enrichment=True,
    use_advanced_enrichment=True
)
```

**Sample Output:**
- `Anthropic funding Series C investment` (score: 0.89)
- `Claude AI vs ChatGPT comparison` (score: 0.86)
- `Anthropic constitutional AI research papers` (score: 0.83)

### Technology Research
```python
request = SearchQueryEnrichmentRequestObject(
    query="Kubernetes",
    identifier_context="Container orchestration platform, originally by Google, CNCF project",
    search_reason_context="Find best practices for production deployment",
    how_many=12,
    use_advanced_enrichment=True
)
```

**Sample Output:**
- `Kubernetes production best practices 2024` (score: 0.91)
- `Google Kubernetes Engine deployment guide` (score: 0.88)
- `CNCF Kubernetes security checklist` (score: 0.85)

## 🔧 API Reference

### SearchQueryEnrichmentRequestObject

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `query` | `str` | The base search query | Required |
| `identifier_context` | `str` | Additional context about the search target | `None` |
| `search_reason_context` | `str` | What you're trying to accomplish with the search | `None` |
| `text_rules` | `str` | Custom rules for query generation | `None` |
| `how_many` | `int` | Maximum number of enriched queries to return | `10` |
| `use_basic_enrichment` | `bool` | Enable combinatorial enrichment | `False` |
| `use_advanced_enrichment` | `bool` | Enable AI-powered enrichment | `False` |
| `use_thinking` | `bool` | Use advanced reasoning model (o3) | `False` |

### UnifiedQueryCandidate

Each enriched query returns:
- `query`: The enriched search string
- `score`: Relevance score (0.0-1.0) 
- `explanation`: Description of what information this query targets
- `origin`: Whether from "basic" or "advanced" enrichment

## 🏗️ Architecture

### Basic Enrichment
1. **Extract Components**: AI identifies identifiers, platforms, and entities from context
2. **Generate Combinations**: Creates systematic combinations (identifier + platform, identifier + entity, etc.)
3. **Score & Filter**: Assigns relevance scores and filters low-quality combinations

### Advanced Enrichment
1. **Context Analysis**: AI analyzes the search goal and available context
2. **Natural Query Generation**: Creates human-like search variations
3. **Quality Assessment**: Each query gets explanation and relevance scoring

### Merge & Rank
- Combines results from both enrichment strategies
- Deduplicates similar queries (keeping highest scored)
- Returns top N results sorted by relevance score

## ⚙️ Configuration

### Environment Setup
Create a `.env` file with your LLM service configuration:
```
OPENAI_API_KEY=your_api_key_here
# Add other model provider keys as needed
```

### Custom Models
```python
from casqe.myllmservice import MyLLMService

# Use specific model
llm_service = MyLLMService()
enricher = SearchQueryEnricher(llm=llm_service)

# For requests requiring advanced reasoning
request.use_thinking = True  # Uses o3 model
```

## 🎯 Use Cases

- **Competitive Intelligence**: Comprehensive competitor research
- **Product Research**: Technical specifications, reviews, comparisons
- **Academic Research**: Literature reviews, expert finding
- **OSINT**: Open source intelligence gathering
- **Market Research**: Industry analysis, trend identification
- **Due Diligence**: Background research for business decisions
- **Content Research**: Finding diverse sources for content creation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♀️ Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the [documentation](docs/) for detailed guides
- Review the example scripts in the `examples/` directory

---

**CASQE** - Making comprehensive research accessible to everyone.