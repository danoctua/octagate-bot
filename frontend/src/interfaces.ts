export interface IBaseChat {
    id: number,
    username: string,
    title: string,
    description: string,
    slug: string,
    isForum: boolean,
    logoPath: string,
    membersCount: number,
}


export interface IChat extends IBaseChat {
    joinUrl?: string,
    isMember: boolean,
    isEligible: boolean,
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

export interface IUser {
    id: number,
    firstName: string,
    lastName: string,
    username: string,
    isPremium: boolean,
    languageCode: string,
    photoUrl: string | null,
    walletAddress: string | null,
}