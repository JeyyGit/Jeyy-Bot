import discord
import datetime as dt
import pytz

class AceModal(discord.ui.Modal):
    name_input = discord.ui.TextInput(
            label='Name', 
            min_length=1,
            max_length=100
    )
    text_input = discord.ui.TextInput(
            label='Text',
            style=discord.TextStyle.paragraph,
            min_length=1,
            max_length=240
    )

    def __init__(self, ctx, title):
        super().__init__(title=title)
        self.ctx = ctx
        self.name_input.default = str(ctx.author)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.stop()


class TaskAddModal(discord.ui.Modal):
    task_name_input = discord.ui.TextInput(
        label='Task Name',
        min_length=1,
        max_length=200,
        placeholder='required'
    )
    description_input = discord.ui.TextInput(
        label='Description',
        style=discord.TextStyle.paragraph,
        placeholder='optional',
        required=False,
        max_length=1000
    )

    deadline_input = discord.ui.TextInput(
        label='Deadline, TZ (DD/MM/YY hh:mm, region/city)',
        placeholder='Example: 24/12/23 18:00, America/Chicago',
        required=True
    )

    channel_input = discord.ui.TextInput(
        label='Channel ID',
        placeholder='Channel for sending reminder (default to current channel)',
        required=False
    )

    remind_before = discord.ui.TextInput(
        label='Remind before deadline in hour',
        placeholder='place comma for multiple',
        default='24, 6, 1'
    )

    def __init__(self, view):
        self.view = view
        self.ctx = view.ctx
        self.channel_input.default = self.ctx.channel.id
        super().__init__(title='Add New Task')

    async def on_submit(self, interaction: discord.Interaction):
        datetime_str, tz = self.deadline_input.value.strip().split(',')
        tz = tz.strip()
        ptz = pytz.timezone(tz)

        deadline = dt.datetime.strptime(datetime_str.strip(), '%d/%m/%y %H:%M')
        deadline_tz = deadline.astimezone(ptz).replace(tzinfo=None)

        reminds = [deadline - (deadline_tz - deadline) - dt.timedelta(hours=int(h.strip())) for h in self.remind_before.value.split(',') + ['0']]
        # reminds = [r for r in reminds if dt.datetime.now(pytz.timezone(tz)) <= r.astimezone(pytz.timezone(tz))]

        await self.ctx.db.execute('''
            INSERT INTO task 
                (user_id, name, description, deadline, tz, channel_id, remind_before, passed)
            VALUES
                ($1, $2, $3, $4, $5, $6, $7, $8)
        ''', self.ctx.author.id, self.task_name_input.value, self.description_input.value, deadline, tz.lower(), int(self.channel_input.value), reminds, [] * len(reminds))
        discord.utils.as_chunks()
        try:
            remind_text = "\n- ".join(f'{discord.utils.format_dt(r, "f")} \n- `{h}` hour before deadline, {discord.utils.format_dt(r, "R")}' for r, h in zip(reminds[:-1], self.remind_before.value.split(',')))
        except:
            remind_text = ""
        embed = discord.Embed(color=discord.Color.random(), title=f'Added new task: `{self.task_name_input.value}`', description=f'{self.description_input.value}\n\nDeadline: {discord.utils.format_dt(reminds[-1], "f")}\nWill be reminded on: \n- {remind_text}')
        return await interaction.response.send_message(embed=embed)
