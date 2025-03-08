export const generateBotJoinLink = (slug: string) => {
    return `${process.env.NEXT_PUBLIC_BOT_URL}?startapp=${slug}`;
}
