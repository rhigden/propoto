# Automated Testing Guide - Propoto

This guide covers the automated testing infrastructure for the Propoto API. We use `pytest` for backend testing.

## 🧪 Backend Testing (Python)

The backend tests are located in `propoto/api/tests/`.

### Prerequisites

Ensure you have the development dependencies installed:

```bash
cd propoto/api
source venv/bin/activate
pip install -r requirements.txt
# Ensure pytest and pytest-asyncio are installed
pip install pytest pytest-asyncio httpx
```

### Running Tests

#### Run All Tests
```bash
pytest
```

#### Run Specific Test File
```bash
pytest tests/test_integration.py
```

#### Run with Output (Verbose)
```bash
pytest -v
```

#### Run with Logs
```bash
pytest -o log_cli=true
```

### Test Categories

| File | Purpose |
|------|---------|
| `test_main.py` | Basic API endpoints (root, health, auth) |
| `test_agents.py` | Unit tests for individual agents (Knowledge, Sales, Brand) |
| `test_integration.py` | Full workflow tests mocking external services |
| `test_e2e_validation.py` | End-to-end validation of proposal generation logic |
| `test_error_handling.py` | Tests for error scenarios and exception handling |
| `test_rate_limit.py` | Verification of rate limiting middleware |
| `test_output_quality.py` | Checks for response structure and quality |

### Mocking

Most tests use `unittest.mock` to mock external services (OpenRouter, Gamma, Exa, Firecrawl, Convex) to avoid incurring costs and to ensure deterministic results.

- **External APIs:** Mocked in `test_integration.py` and `test_agents.py`.
- **Database:** Convex interactions are mocked.

## 🖥️ Frontend Testing

Currently, there are no automated tests for the frontend (`propoto/web`).

**Recommended Next Steps:**
1.  **Unit Tests:** Add Jest/React Testing Library for components.
2.  **E2E Tests:** Add Playwright or Cypress for critical user flows.

## 🤖 Telegram Bot Testing

**Status:** ⚠️ Missing Automated Tests

The Telegram Bot integration (`services/telegram_bot.py`) currently relies on manual testing.

**Recommended Next Steps:**
1.  Add `tests/test_telegram.py`.
2.  Mock `python-telegram-bot`'s `Application` and `Context` to test command handlers.

## 📊 Test Coverage

To check code coverage:

```bash
pip install pytest-cov
pytest --cov=.
```

Current coverage focus:
- **High:** Core agent logic, API endpoints, Error handling.
- **Medium:** Service integrations (Gamma, Scraping).
- **Low:** Telegram Bot, Frontend UI.
