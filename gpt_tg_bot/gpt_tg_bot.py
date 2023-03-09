import os
import re
import html
from gpt_api.gpt_api import GPTApi
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
import logging

from typing import Dict, List, Tuple


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# GPT API
gpt_api = GPTApi()

# Telegram API token
TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")

# Conversation states
NO_ACTIVE_CHAT, ACTIVE_CHAT = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    reply_text = "Welcome to GPT telegram bot. "

    if context.user_data:
        reply_text += (
            f"You already have an active chat. You can continue chatting or type /end to end it."
        )
        await update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup([["🪙 Token usage", "✋ End chat"]], one_time_keyboard=True))
        return ACTIVE_CHAT

    reply_text += (
        "Press the button below to get start a new GPT chat."
    )
    await update.message.reply_text(reply_text,
                                    reply_markup=ReplyKeyboardMarkup([["💬 New Chat"]],
                                                                     one_time_keyboard=True))

    return NO_ACTIVE_CHAT


async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    context.user_data["messages"] = []
    context.user_data["total_tokens"] = 0
    context.user_data["messages_tokens"] = []

    context.user_data["messages"].append(
        {"role": "system", "content": "You are a helpful assistant."})

    await update.message.reply_text(
        "A new chat has been started. Write your first message.", reply_markup=ReplyKeyboardRemove()
    )

    return ACTIVE_CHAT


async def chat_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    text = update.message.text
    context.user_data["messages"].append({"role": "user", "content": text})

    gpt_reply, num_tokens = gpt_api.message(context.user_data["messages"])

    context.user_data["messages"].append(
        {"role": "assistant", "content": gpt_reply})
    context.user_data["total_tokens"] += num_tokens

    # count tokens in this user-assistant pair
    if not context.user_data["messages_tokens"]:
        context.user_data["messages_tokens"].append(num_tokens)
    else:
        message_tokens = num_tokens - sum(context.user_data["messages_tokens"])
        context.user_data["messages_tokens"].append(message_tokens)

    # shorten the dialog if it's close to the limit of 4096 tokens
    messages_s, messages_tokens_s = shorten_msg(
        context.user_data["messages"], context.user_data["messages_tokens"])
    
    context.user_data["messages"] = messages_s
    context.user_data["messages_tokens"] = messages_tokens_s

    gpt_reply_processed = replace_code_block(gpt_reply)

    await update.message.reply_text(gpt_reply_processed, reply_markup=ReplyKeyboardMarkup([["🪙 Token usage", "✋ End chat"]], one_time_keyboard=True), parse_mode='HTML')

    return ACTIVE_CHAT


def shorten_msg(messages: List, messages_tokens: List) -> List:

    while sum(messages_tokens) > 3596:
        del messages[3:5]
        del messages_tokens[1]

    return messages, messages_tokens


def replace_code_block(message: str) -> str:

    code_block_start_regex = re.compile(r"(```\w+)")
    matches = code_block_start_regex.findall(message)

    for match in matches:
        message = message.replace(match, "```")

    code_block_regex = re.compile(r'```([^`]+)```')
    return code_block_regex.sub(code_md_to_html, html.escape(message))


def code_md_to_html(match: re.Match) -> str:
    return f'<code>{match.group(1)}</code>'


async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    try:
        del context.user_data["messages"]
        del context.user_data["total_tokens"]
        del context.user_data["messages_tokens"]
    except KeyError:
        pass

    await update.message.reply_text(
        "Your chat has been ended. You can start a new chat with the /start command or using the button below.",
        reply_markup=ReplyKeyboardMarkup(
            [["💬 New Chat"]], one_time_keyboard=True)
    )

    return NO_ACTIVE_CHAT


async def token_usage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if "total_tokens" not in context.user_data:
        await update.message.reply_text("There are no token usage stats available.")
        return ACTIVE_CHAT

    reply_text = format_token_usage_msg(context.user_data["total_tokens"])
    await update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup([["🪙 Token usage", "✋ End chat"]], one_time_keyboard=True))

    return ACTIVE_CHAT


def format_token_usage_msg(total_tokens: int) -> str:

    estimated_cost = 0.002 * total_tokens/1000

    return f"You have used {total_tokens} tokens in this chat session. The estimated cost is ${estimated_cost:.2f} at $0.002 / 1K tokens."


def main() -> None:

    if not TELEGRAM_API_TOKEN:
        logger.error("TELEGRAM_API_TOKEN not set")
        return

    persistence = PicklePersistence(filepath="active_chats.pkl")
    application = Application.builder().token(
        TELEGRAM_API_TOKEN).persistence(persistence).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        allow_reentry=True,
        states={
            NO_ACTIVE_CHAT: [
                MessageHandler(
                    filters.Regex("^(💬 New Chat)$"), new_chat
                ),
            ],
            ACTIVE_CHAT: [
                MessageHandler(
                    filters.Regex("^(🪙 Token usage)$"), token_usage
                ),
                MessageHandler(
                    filters.Regex("^(✋ End chat)$"), end_chat
                ),
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND), chat_reply
                )
            ]
        },
        fallbacks=[
            CommandHandler("end", end_chat)
        ],
        name="gpt_chat",
        persistent=True,
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
