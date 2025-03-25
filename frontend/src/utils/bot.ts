export const generateBotJoinLink = (slug: string) => {
    return `${process.env.NEXT_PUBLIC_BOT_URL}?startapp=${slug}`;
}

export const generateBotAddToChatLink = () => {
    const botUrlWithoutPath = process.env.NEXT_PUBLIC_BOT_URL?.split('/').slice(0, 4).join('/');
    return `${botUrlWithoutPath}?startgroup=true`;
}
