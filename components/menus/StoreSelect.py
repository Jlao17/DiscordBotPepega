import discord
from components.menus.StoreSelectOption import StoreSelectOption
from functions.list_to_embed import list_to_embed
from functions.check_game_in_db import check_game_in_db
import logging

log = logging.getLogger(__name__)

class StoreSelect(discord.ui.Select):
    def __init__(self, data, components, user_cnf):
        super().__init__()
        self.data = data
        self.components = components
        self.user_cnf = user_cnf
        options = []
        for data, name in self.data:
            if data:
                # log.info(data)
                # log.info(name)
                option = StoreSelectOption(label=name, data=data)
                options.append(option)
            continue
        super().__init__(placeholder="Filter on store", options=options)

    async def callback(self, interaction: discord.Interaction):
        # if interaction.user.id != ctx.author.id
        selected_options = self.values  # Get the selected option
        selected_option_data = None
        # print("self.options", self.options)
        for option in self.options:  # Iterate over the options to find the selected option
            if option.value in selected_options:
                selected_option_data = option.data  # Get the data associated with the selected option
        log.info(selected_option_data)

        # convert selected_option_data[0][0] to steam game name
        game_name = await check_game_in_db(int(selected_option_data[0][0]))
        temp_list = list(selected_option_data[0])
        temp_list[0] = game_name[1]  # Modify the first element
        selected_option_data[0] = tuple(temp_list)  # Convert it back to a tuple

        embed = await list_to_embed(selected_option_data, ''.join(selected_options), self.user_cnf)
        await interaction.response.defer()
        await interaction.message.edit(embed=embed, view=self.components)
