export const generateBotJoinLink = (slug: string) => {
    return `${process.env.NEXT_PUBLIC_BOT_URL}?startapp=${slug}`;
}


export const generateBotShareLink = ({title, slug}: {title: string | undefined, slug: string | undefined}): string => {
    /* Generates a link to share the bot with a direct link to join the chat/channel */
    if (!slug || !title) {
        return "";
    }

    const botUrl = generateBotJoinLink(slug);
    return `https://t.me/share/url?url=${encodeURIComponent(botUrl)}&text=${encodeURIComponent(`Join ${title}`)}`;
}
