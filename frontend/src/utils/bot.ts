export const generateBotJoinLink = (botUrl: string, slug: string) => {
    return `${botUrl}?startapp=${slug}`;
}

export const generateBotAddToChatLink = (botUrl: string) => {
    const botUrlWithoutPath = botUrl.split('/').slice(0, 4).join('/');
    return `${botUrlWithoutPath}?startgroup=true`;
}
