export interface IChat {
    id: number,
    username: string,
    title: string,
    description: string,
    slug: string,
    isForum: boolean,
    logoPath: string,
    joinUrl?: string,
    isMember: boolean,
    isEligible: boolean,
    membersCount: number,
}

export interface IRule {
    category: string,
    title: string,
    promoteUrl: string,
    expected: number,
    actual?: number,
    photoUrl: string,
    isEligible: boolean,
}

export interface IChatConfiguration {
    chat: IChat,
    rules: IRule[],
}
