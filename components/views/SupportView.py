import discord


class SupportView(discord.ui.View):
    def __init__(self, args, bot):
        super(SupportView, self).__init__(timeout=30)
        self.args = args
        self.bot = bot

    @discord.ui.button(label='Report', style=discord.ButtonStyle.green)
    async def report(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("I've reported this to support, head over to our support server for updates")
        channel = self.bot.get_channel(772579930164035654)
        await channel.send(f"**LOG** - User reported non-existing game/dlc in IGDB/db: `{self.args}`")

    @discord.ui.button(label='Support', style=discord.ButtonStyle.blurple)
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(">Support server link here<")
