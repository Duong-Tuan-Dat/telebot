import re
import pytesseract
import asyncio
from PIL import Image
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

user_state = {}

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_state[chat_id] = {"step": "initial"}
    keyboard = [
        [InlineKeyboardButton("📋 Đăng ký ngay", callback_data="register")],
        [InlineKeyboardButton("ℹ️ Tìm hiểu thêm", callback_data="learn_more")]
    ]
    await update.message.reply_text("Hi", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()

    if query.data == "learn_more":
        keyboard = [[InlineKeyboardButton("📋 Đăng ký ngay", callback_data="register")]]
        await query.message.reply_text("Ai biết", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "register":
        user_state[chat_id] = {"step": "waiting_for_info"}
        await query.message.reply_text("Vui lòng nhập họ tên và năm sinh của bạn theo định dạng: Họ và tên + Năm sinh (ví dụ : Nguyễn Văn A 1995)")
    elif query.data == "agree_terms":
        user_state[chat_id]["step"] = "confirm_terms"
        keyboard = [[InlineKeyboardButton("✅ Đồng ý", callback_data="final_agree")]]
        await query.message.reply_text("⚠️ Xin lưu ý:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "final_agree":
        user_state[chat_id]["step"] = "waiting_for_info_details"
        await query.message.reply_text("Nhập: \nTên\nTuổi\nTỉnh")
    elif query.data == "confirm_correct":
        user_state[chat_id]["step"] = "waiting_for_photo"
        sent_msg = await query.message.reply_text("Gửi mặt điii")
        user_state[chat_id]["last_msg_id"] = sent_msg.message_id
    elif query.data == "reenter_info":
        user_state[chat_id]["step"] = "waiting_for_info_details"
        await query.message.reply_text("Nhập: \nTên\nTuổi\nTỉnh")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    if chat_id not in user_state:
        await start(update, context)
        return

    state = user_state[chat_id]["step"]

    # --- Nhắc nhở khi đang chờ ảnh ---
    if state == "waiting_for_photo":
        await update.message.reply_text("có gì thắc mắc qua đây mà hỏi")
        return
    elif state in ["waiting_for_photo_2", "waiting_for_photo_3", "waiting_for_photo_4"]:
        await update.message.reply_text("vui lòng làm lại, có gì thắc mắc qua đây mà hỏi")
        return

    # --- Xử lý các step thông tin ---
    if state == "waiting_for_info":
        parts = text.rsplit(" ", 1)
        if len(parts) != 2 or not parts[1].isdigit():
            await update.message.reply_text("Thông tin không hợp lệ, vui lòng nhập lại.")
            return

        name, birth_year = " ".join(parts[0].split()), int(parts[1])
        if birth_year < 1945 or birth_year > 2025:
            await update.message.reply_text("Tuổi không hợp lệ, vui lòng thử lại.")
            return
        if birth_year >= 2010:
            await update.message.reply_text("Chưa đủ tuổi để tham gia, vui lòng nhập lại.")
            return

        user_state[chat_id] = {"step": "confirm_terms", "name": name}
        keyboard = [[InlineKeyboardButton("✅ Đồng ý với tất cả các điều khoản trên", callback_data="agree_terms")]]
        await update.message.reply_text(f"Chào {name}", reply_markup=InlineKeyboardMarkup(keyboard))

    elif state == "waiting_for_info_details":
        lines = text.split("\n")
        if len(lines) != 3:
            await update.message.reply_text("Thông tin không hợp lệ, vui lòng nhập lại.")
            return

        name = " ".join(lines[0].split())
        age = lines[1].strip()
        province = " ".join(lines[2].split())

        if not age.isdigit():
            await update.message.reply_text("Tuổi không hợp lệ, vui lòng nhập lại.")
            return
        if not re.match(r"^[A-Za-zÀ-Ỹà-ỹ\s]+$", name):
            await update.message.reply_text("Tên không hợp lệ, vui lòng nhập lại.")
            return
        if not re.match(r"^[A-Za-zÀ-Ỹà-ỹ\s]+$", province):
            await update.message.reply_text("Tỉnh không hợp lệ, vui lòng nhập lại.")
            return

        user_state[chat_id]["step"] = "confirm_info"
        keyboard = [
            [InlineKeyboardButton("✅ Xác nhận đúng thông tin", callback_data="confirm_correct")],
            [InlineKeyboardButton("🔄 Nhập lại", callback_data="reenter_info")]
        ]
        await update.message.reply_text("⚠️ Nếu nhập sai thì bị khờ.", reply_markup=InlineKeyboardMarkup(keyboard))



async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_path = f"{chat_id}_photo.jpg"
    await file.download_to_drive(file_path)

    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang="vie")
        original_text = text.strip()  # giữ nguyên để so sánh bước 4
        cleaned_text = text.lower()    # dùng cho các bước 1-3
        step = user_state.get(chat_id, {}).get("step", "waiting_for_photo")

        # Bước 1
        if step == "waiting_for_photo":
            if "duong tuan dat" in cleaned_text or "dương tuấn đạt" in cleaned_text:
                last_msg_id = user_state.get(chat_id, {}).get("last_msg_id")
                if last_msg_id:
                    await context.bot.edit_message_text(chat_id=chat_id, message_id=last_msg_id, text="hello")
                await update.message.reply_text("chờ tí")
                await asyncio.sleep(5)
                await update.message.reply_text("hình như nhầm rồi")
                user_state[chat_id]["step"] = "waiting_for_photo_2"
            else:
                await update.message.reply_text("sai rồi")

        # Bước 2
        elif step == "waiting_for_photo_2":
            if "598" in cleaned_text:
                last_msg_id = user_state.get(chat_id, {}).get("last_msg_id")
                if last_msg_id:
                    await context.bot.edit_message_text(chat_id=chat_id, message_id=last_msg_id, text="589")
                await update.message.reply_text("chờ tí 2")
                await asyncio.sleep(5)
                await update.message.reply_text("hình như nhầm rồi 2")
                await context.bot.send_photo(chat_id=chat_id, photo=open("step2_fail.jpg", "rb"))
                await update.message.reply_text("đây k có m, làm lại đi")
                user_state[chat_id]["step"] = "waiting_for_photo_3"
            else:
                await update.message.reply_text("sai rồi 2")

        # Bước 3
        elif step == "waiting_for_photo_3":
            if "589" in cleaned_text:
                last_msg_id = user_state.get(chat_id, {}).get("last_msg_id")
                if last_msg_id:
                    await context.bot.edit_message_text(chat_id=chat_id, message_id=last_msg_id, text="Id589")
                await update.message.reply_text("chờ tí 3")
                await asyncio.sleep(5)
                await update.message.reply_text("hình như nhầm rồi 3")
                user_state[chat_id]["step"] = "waiting_for_photo_4"
            else:
                await update.message.reply_text("sai rồi 3")

        # Bước 4
        elif step == "waiting_for_photo_4":
            if "Id589" in original_text:  # giữ chữ hoa I
                await update.message.reply_text("vui lòng chờ 1-2p để chuyển")
                await asyncio.sleep(5)
                await update.message.reply_text("đã chặn đi")
            else:
                await update.message.reply_text("sai rồi 4")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)





app = Application.builder().token("7955469884:AAHIgByV3yd_mcJz3SW8McMMPIlyHUgzEXs").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(CallbackQueryHandler(button_callback))
app.run_polling()

