import discord
from discord.ext import commands
import requests

# Khởi tạo Intent và Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# URL raw của file txt trên GitHub (Thay đường dẫn của bạn vào đây)
GITHUB_TXT_URL = "https://raw.githubusercontent.com/MHLATP/vv/refs/heads/main/b"

def fetch_canva_data(url):
    """Hàm đọc file txt từ GitHub và chuyển thành dictionary {ngày: link}"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return {}
        
        lines = response.text.strip().splitlines()
        data = {}
        for line in lines:
            if " - " in line:
                parts = line.split(" - ", 1)
                date = parts[0].strip()
                link = parts[1].strip()
                data[date] = link
        return data
    except Exception as e:
        print(f"Lỗi khi đọc file GitHub: {e}")
        return {}

class DateDropdown(discord.ui.Select):
    def __init__(self, data):
        options = []
        for date in list(data.keys())[:25]: # Giới hạn tối đa 25 mục của Discord Select Menu
            options.append(
                discord.SelectOption(
                    label=date,
                    emoji="📅",
                    description=f"Nhấn để nhận link Canva ngày {date}"
                )
            )
        super().__init__(
            placeholder="Chọn ngày muốn lấy link...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.data = data

    async def callback(self, interaction: discord.Interaction):
        selected_date = self.values[0]
        link = self.data.get(selected_date, "Không tìm thấy link cho ngày này!")
        
        await interaction.response.send_message(
            f"🔗 **Link Canva ngày {selected_date}:**\n{link}",
            ephemeral=True
        )

class DateDropdownView(discord.ui.View):
    def __init__(self, data):
        super().__init__(timeout=None)
        self.add_item(DateDropdown(data))

class CanvaMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Lấy Link", style=discord.ButtonStyle.green, emoji="🔗")
    async def get_link_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = fetch_canva_data(GITHUB_TXT_URL)
        
        if not data:
            await interaction.response.send_message("❌ Không thể lấy dữ liệu từ GitHub hoặc file rỗng!", ephemeral=True)
            return

        # Khi bấm nút "Lấy Link", bot sẽ gửi menu chọn ngày hiển thị dạng riêng tư (hoặc công khai tùy ý)
        view = DateDropdownView(data)
        await interaction.response.send_message("📅 **Chọn ngày cần lấy link:**", view=view, ephemeral=True)

@bot.event
async def on_ready():
    print(f"Bot đã sẵn sàng: {bot.user}")

@bot.command(name="setcanva")
async def setcanva(ctx):
    """Lệnh !setcanva để tạo bảng giao diện Canva Pro"""
    # Xóa tin nhắn lệnh !setcanva của người dùng để khung trông đẹp mắt hơn
    try:
        await ctx.message.delete()
    except:
        pass

    # Tạo khung Embed giống mẫu yêu cầu
    embed = discord.Embed(
        title="Free Canva Pro (Team)",
        description="Nhấn vào nút **🔗 Lấy Link** bên dưới để lấy link.",
        color=discord.Color.from_rgb(235, 87, 87) # Màu hồng/đỏ nhẹ giống mẫu
    )
    
    # Thêm các dòng thông tin
    embed.add_field(
        name="", 
        value="• 🔄 Quét link tự động.\n• 📅 Quét 22 ngày gần nhất.", 
        inline=False
    )
    
    # Thêm hình ảnh minh họa lớn (Bạn có thể thay đổi link ảnh Canva tùy ý)
    embed.set_image(url="https://cdn.tgdd.vn/News/1558244/2-1280x720.jpg")
    
    # Thêm dòng chữ bản quyền dưới footer
    embed.set_footer(text="by : MHL_ATP 6 SCAN")

    # Gửi tin nhắn chứa Embed và nút bấm
    view = CanvaMainView()
    await ctx.send(embed=embed, view=view)

# Thay TOKEN_BOT_CUAR_BAN bằng token thật của bạn
bot.run("DISCORD_TOKEN")
