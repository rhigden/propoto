"""
Telegram Bot Service for Proposal Generation

Allows users to generate proposals via Telegram chat.
Commands:
- /start - Welcome message and instructions
- /proposal <name> <url> <pain_point> - Generate a proposal
- /status - Check bot status
- /help - Show help message

Environment Variables:
- TELEGRAM_BOT_TOKEN: Your Telegram bot token from @BotFather
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Check if python-telegram-bot is available
try:
    from telegram import Update, Bot
    from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("python-telegram-bot not installed. Telegram bot features disabled.")


@dataclass
class TelegramBotConfig:
    """Configuration for Telegram bot."""
    token: str
    webhook_url: Optional[str] = None
    api_url: str = "http://localhost:8000"
    api_key: str = ""


class TelegramBotService:
    """
    Telegram bot service for generating proposals via chat.
    """
    
    def __init__(self, config: Optional[TelegramBotConfig] = None):
        self.config = config or TelegramBotConfig(
            token=TELEGRAM_BOT_TOKEN or "",
            api_url=os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8000"),
            api_key=os.getenv("AGENT_SERVICE_KEY", "")
        )
        self.application: Optional[Any] = None
        self._running = False
        
    @property
    def is_configured(self) -> bool:
        """Check if bot is properly configured."""
        return bool(TELEGRAM_AVAILABLE and self.config.token)
    
    async def start(self):
        """Start the Telegram bot."""
        if not self.is_configured:
            logger.error("Telegram bot not configured. Set TELEGRAM_BOT_TOKEN.")
            return
        
        logger.info("Starting Telegram bot...")
        
        # Create application
        self.application = Application.builder().token(self.config.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self._handle_start))
        self.application.add_handler(CommandHandler("help", self._handle_help))
        self.application.add_handler(CommandHandler("status", self._handle_status))
        self.application.add_handler(CommandHandler("proposal", self._handle_proposal))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        
        # Start polling
        self._running = True
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Telegram bot started successfully!")
    
    async def stop(self):
        """Stop the Telegram bot."""
        if self.application and self._running:
            logger.info("Stopping Telegram bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            self._running = False
            logger.info("Telegram bot stopped.")
    
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_message = """
🚀 *Welcome to AgencyOS Proposal Bot!*

I can help you generate high-converting sales proposals in seconds.

*Quick Start:*
Use the /proposal command with the following format:

`/proposal CompanyName https://company.com Their main pain point`

*Example:*
`/proposal Acme Corp https://acme.com Low conversion rates on their website`

Type /help for more commands.
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        
        # Log the user
        logger.info(f"New user started bot: {update.effective_user.username} ({update.effective_chat.id})")
    
    async def _handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
📖 *AgencyOS Bot Commands*

/proposal <name> <url> <pain_point>
Generate a sales proposal

/status
Check if the service is running

/help
Show this help message

*Tips:*
• Be specific about the pain point
• Include the full website URL
• The more context, the better!

*Example:*
`/proposal TechStartup https://techstartup.io They need better lead generation and their website is outdated`
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def _handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self.config.api_url}/health")
                if resp.status_code == 200:
                    status_msg = "✅ *AgencyOS Status: Online*\n\nAll systems operational."
                else:
                    status_msg = "⚠️ *AgencyOS Status: Degraded*\n\nSome features may be unavailable."
        except Exception as e:
            status_msg = f"❌ *AgencyOS Status: Offline*\n\nError: {str(e)}"
        
        await update.message.reply_text(status_msg, parse_mode='Markdown')
    
    async def _handle_proposal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /proposal command."""
        import httpx
        
        # Parse arguments
        args = context.args
        if not args or len(args) < 3:
            await update.message.reply_text(
                "❌ *Invalid format*\n\n"
                "Use: `/proposal CompanyName https://url.com Pain point description`\n\n"
                "Example: `/proposal Acme Corp https://acme.com Low website conversion`",
                parse_mode='Markdown'
            )
            return
        
        # Extract parameters
        prospect_name = args[0]
        prospect_url = args[1]
        pain_points = " ".join(args[2:])
        
        # Validate URL
        if not prospect_url.startswith(('http://', 'https://')):
            prospect_url = f"https://{prospect_url}"
        
        # Send "generating" message
        status_msg = await update.message.reply_text(
            f"🔄 *Generating proposal for {prospect_name}...*\n\n"
            "This typically takes 30-60 seconds. I'll analyze their website and craft a personalized proposal.",
            parse_mode='Markdown'
        )
        
        try:
            # Call the proposal API
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{self.config.api_url}/agents/proposal/generate",
                    json={
                        "prospect_name": prospect_name,
                        "prospect_url": prospect_url,
                        "pain_points": pain_points,
                        "deep_scrape": True  # Enable deep scraping for Telegram
                    },
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self.config.api_key
                    }
                )
                
                if resp.status_code != 200:
                    error_detail = resp.json().get("detail", "Unknown error")
                    await status_msg.edit_text(
                        f"❌ *Error generating proposal*\n\n{error_detail}",
                        parse_mode='Markdown'
                    )
                    return
                
                result = resp.json()
                
                if not result.get("success"):
                    await status_msg.edit_text(
                        "❌ *Failed to generate proposal*\n\nPlease try again later.",
                        parse_mode='Markdown'
                    )
                    return
                
                # Format the proposal
                proposal = result.get("data", {})
                presentation_url = result.get("presentation_url")
                pdf_url = result.get("pdf_url")
                
                # Build response message
                response = f"""
✅ *Proposal for {prospect_name}*

📋 *Executive Summary*
{proposal.get('executive_summary', 'N/A')}

📊 *Current Situation*
{proposal.get('current_situation', 'N/A')}

🎯 *Proposed Strategy*
{proposal.get('proposed_strategy', 'N/A')}

💪 *Why Us*
{proposal.get('why_us', 'N/A')}

💰 *Investment Options*
"""
                # Add pricing tiers
                for tier in proposal.get('investment', []):
                    response += f"\n*{tier.get('name')}* - {tier.get('price')}\n"
                    for feature in tier.get('features', [])[:3]:
                        response += f"  • {feature}\n"

                response += f"""
📞 *Next Steps*
{proposal.get('next_steps', 'N/A')}
"""
                
                # Add links
                if presentation_url:
                    response += f"\n🎨 [View Presentation]({presentation_url})"
                if pdf_url:
                    response += f"\n📄 [Download PDF]({pdf_url})"
                
                await status_msg.edit_text(response, parse_mode='Markdown', disable_web_page_preview=True)
                
        except asyncio.TimeoutError:
            await status_msg.edit_text(
                "⏱️ *Request timed out*\n\nThe proposal is taking longer than expected. Please try again.",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error generating proposal: {e}")
            await status_msg.edit_text(
                f"❌ *Error*\n\n{str(e)}",
                parse_mode='Markdown'
            )
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        text = update.message.text.lower()
        
        # Simple intent detection
        if any(word in text for word in ['proposal', 'generate', 'create']):
            await update.message.reply_text(
                "💡 *Tip:* To generate a proposal, use the /proposal command:\n\n"
                "`/proposal CompanyName https://url.com Pain point`\n\n"
                "Type /help for more info.",
                parse_mode='Markdown'
            )
        elif any(word in text for word in ['help', 'how', 'what']):
            await self._handle_help(update, context)
        else:
            await update.message.reply_text(
                "👋 I'm the AgencyOS Proposal Bot!\n\n"
                "Type /help to see available commands.",
                parse_mode='Markdown'
            )


# Singleton instance
_telegram_bot: Optional[TelegramBotService] = None

def get_telegram_bot() -> TelegramBotService:
    """Get or create Telegram bot singleton."""
    global _telegram_bot
    if _telegram_bot is None:
        _telegram_bot = TelegramBotService()
    return _telegram_bot


async def run_telegram_bot():
    """Run the Telegram bot (blocking)."""
    bot = get_telegram_bot()
    if not bot.is_configured:
        logger.error("Telegram bot not configured. Set TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    try:
        await bot.start()
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        await bot.stop()
    except Exception as e:
        logger.error(f"Bot error: {e}")
        await bot.stop()


if __name__ == "__main__":
    # Run bot directly
    asyncio.run(run_telegram_bot())

