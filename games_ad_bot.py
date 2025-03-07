import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

(
    GAME_NAME,
    PS5_PRIMARY,
    PS5_SECONDARY,
    PS4_AVAILABLE,
    PS4_PRIMARY,
    PS4_SECONDARY,
    OFFLINE_AVAILABLE,
) = range(7)

def yes_no_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes", callback_data="yes"),
            InlineKeyboardButton("❌ No", callback_data="no"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("🎮 Enter the game name:")
    return GAME_NAME

# Game name handler
async def game_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["game_name"] = update.message.text
    await update.message.reply_text(
        "Available for PS5 Primary?", reply_markup=yes_no_keyboard()
    )
    return PS5_PRIMARY

# PS5 Primary handler
async def ps5_primary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["ps5_primary"] = query.data
    await query.edit_message_text(
        "Available for PS5 Secondary?", reply_markup=yes_no_keyboard()
    )
    return PS5_SECONDARY

# PS5 Secondary handler
async def ps5_secondary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["ps5_secondary"] = query.data
    await query.edit_message_text(
        "Is the game available for PS4?", reply_markup=yes_no_keyboard()
    )
    return PS4_AVAILABLE

# PS4 availability handler
async def ps4_available(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "yes":
        context.user_data["ps4_available"] = "yes"
        await query.edit_message_text(
            "Available for PS4 Primary?", reply_markup=yes_no_keyboard()
        )
        return PS4_PRIMARY
    else:
        context.user_data["ps4_available"] = "no"
        context.user_data["ps4_primary"] = "no"
        context.user_data["ps4_secondary"] = "no"

        await query.edit_message_text(
            "Is the game available offline?", reply_markup=yes_no_keyboard()
        )
        return OFFLINE_AVAILABLE

# PS4 Primary handler
async def ps4_primary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data["ps4_primary"] = query.data

    await query.edit_message_text(
        "Available for PS4 Secondary?", reply_markup=yes_no_keyboard()
    )

    return PS4_SECONDARY

# PS4 Secondary handler
async def ps4_secondary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data["ps4_secondary"] = query.data

    await query.edit_message_text(
        "Is the game available offline?", reply_markup=yes_no_keyboard()
    )

    return OFFLINE_AVAILABLE

# Offline availability handler
async def offline_available(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    game_name = context.user_data['game_name']

    ps5_primary = '✅' if context.user_data['ps5_primary'] == 'yes' else '❌'

    ps5_secondary = '✅' if context.user_data['ps5_secondary'] == 'yes' else '❌'

    ps4_available = context.user_data['ps4_available'] == 'yes'

    # Build final summary message clearly and logically:

    summary_message = f"🎮 <b>Game:</b> {game_name}\n\n"
    summary_message += f"<b>PS5 Primary:</b> {ps5_primary}\n"
    summary_message += f"<b>PS5 Secondary:</b> {ps5_secondary}\n\n"
    summary_message += f"<b>PS4 Available:</b> {'✅' if ps4_available else '❌'}\n"

    if ps4_available:
        ps4_primary = '✅' if context.user_data['ps4_primary'] == 'yes' else '❌'
        ps4_secondary = '✅' if context.user_data['ps4_secondary'] == 'yes' else '❌'
        summary_message += f"<b>PS4 Primary:</b> {ps4_primary}\n"
        summary_message += f"<b>PS4 Secondary:</b> {ps4_secondary}\n"

    # Offline availability logic corrected clearly:

    if query.data == "yes":
        if ps4_available:
            offline_status = "✅ 2x OFFLINE available for BOTH PS4 | PS5"
        else:
            offline_status = "✅ OFFLINE available for PS5 ONLY"
    else:
        offline_status = "❌ Game is ONLY ONLINE PLAYABLE"

    summary_message += f"\n{offline_status}"

    await query.edit_message_text(summary_message, parse_mode="HTML")

    return ConversationHandler.END

# Cancel handler (optional)
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("🚫 Conversation cancelled.")
    return ConversationHandler.END

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GAME_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, game_name)],
            PS5_PRIMARY: [CallbackQueryHandler(ps5_primary)],
            PS5_SECONDARY: [CallbackQueryHandler(ps5_secondary)],
            PS4_AVAILABLE: [CallbackQueryHandler(ps4_available)],
            PS4_PRIMARY: [CallbackQueryHandler(ps4_primary)],
            PS4_SECONDARY: [CallbackQueryHandler(ps4_secondary)],
            OFFLINE_AVAILABLE: [CallbackQueryHandler(offline_available)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    ))

    application.run_polling()

if __name__ == "__main__":
    main()


