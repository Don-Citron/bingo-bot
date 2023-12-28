"""Functions for Discord related things."""

import discord
from discord.ext import commands
import typing
import datetime

import utility.text as text
import utility.custom as custom

everyone_prevention = discord.AllowedMentions(everyone=False)

def embed(
        title: str, title_link: str = None,
        color: typing.Union[str, tuple[int, int, int]] = "#e91e63",
        description: str = None,
        author_name: str = None, author_link: str = None, author_icon: str = None,
        footer_text: str = None, footer_icon: str = None,
        image_link: str = None,
        thumbnail_link: str = None,
        fields: list[tuple[str, str, bool]] = None,
        timestamp: datetime.datetime = None
    ) -> discord.Embed:
    """Function for easy creation of embeds. The color can be provided as a hex code (with or without the hash symbol) or as RGB values.
    # Fields:
    Each field is a 3 item tuple as follows:
    1. Field name (256 characters)
    2. Field text (1024 characters)
    3. Whether the field should be inline (bool)
    The fields should be provided in the order you want to display them.
    # For adding images:
    https://discordpy.readthedocs.io/en/stable/faq.html#local-image"""

    if isinstance(color, str):
        color = int(color.replace("#", ""), 16)
    elif isinstance(color, tuple):
        color = int(f"{color[0]:02x}{color[1]:02x}{color[2]:02x}", 16)
    else:
        raise TypeError("Provided color must be a hex code or set of RBG values in a tuple.")
    
    embed = discord.Embed(
        color = color,
        title = title,
        url = title_link,
        description = description,
        timestamp = timestamp
    )

    if author_name is not None:
        embed.set_author(
            name = author_name,
            url = author_link,
            icon_url = author_icon
        )
    
    if footer_text is not None:
        embed.set_footer(
            text = footer_text,
            icon_url = footer_icon
        )
    
    if image_link is not None:
        embed.set_image(
            url = image_link
        )
    
    if thumbnail_link is not None:
        embed.set_thumbnail(
            url = thumbnail_link
        )
    
    if fields is not None:
        for field_title, field_text, field_inline in fields:
            embed.add_field(
                name = field_title,
                value = field_text,
                inline = field_inline
            )
    
    return embed

def msg_content(ctx: commands.Context) -> str:
    """Returns the message content from a context object, while removing commands.
    For example, a context object of the message `%objective search Hello, world!` would return `Hello, world!`"""
    return ((ctx.message.content).replace(str(ctx.command), "", 1).replace(ctx.bot.command_prefix, "", 1).lstrip(" "))

def combine_args(ctx: (commands.Context | str), args: (tuple | list), keep: int, ctx_is_content: bool = False) -> list[str]:
    """Combines args into a single arg using msg_content(), it will, however, keep the first x arguments as normal, and will not incorporate those into the joined arg. x is set with the keep parameter. 
    If ctx_is_content is set to true then the ctx argument will be treated as the content."""
    args = list(args)
    if ctx_is_content:
        content = ctx
    else:
        content = msg_content(ctx)

    if keep == 0: return content

    indexstart = content.find(args[keep - 1]) + len(args[keep - 1]) + 1
    while content[indexstart] in ['"', "'", " "] and not indexstart >= len(content):
        indexstart += 1
    if indexstart >= len(content):
        content == ""
    else:
        content = content[indexstart:]
    
    return [args[i] for i in range(keep)] + [content]

def get_display_name(member):
    return (member.global_name if (member.global_name is not None and member.name == member.display_name) else member.display_name)

async def smart_reply(ctx, content: str = "", **kwargs) -> discord.Message:
    """Attempts to reply, if there's an error it then tries to send it normally."""

    try:
        return await safe_reply(ctx, content, **kwargs)
    except discord.HTTPException:
        # If something went wrong replying.
        if kwargs.get("mention_author", True):
            return await safe_send(ctx, f"{ctx.author.mention},\n\n{content}", **kwargs)
        else:
            return await safe_send(ctx, f"{text.ping_filter(get_display_name(ctx.author))},\n\n{content}", **kwargs)
    except:
        # For other errors, this will fire and reraise the exception.
        raise


async def safe_reply(ctx, content: str = "", **kwargs) -> discord.Message:
    """Replies in a safe manner."""
    
    kwargs["allowed_mentions"] = everyone_prevention

    return await ctx.reply(content, **kwargs)

async def safe_send(ctx, content: str = "", **kwargs) -> discord.Message:
    """Sends a message in a safe manner."""

    kwargs["allowed_mentions"] = everyone_prevention
    
    return await ctx.send(content, **kwargs)
