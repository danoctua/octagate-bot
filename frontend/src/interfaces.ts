export interface IBaseChat {
    id: number,
    username: string,
    title: string,
    description: string,
    slug: string,
    isForum: boolean,
    logoPath: string,
}


export interface IChat extends IBaseChat {
    joinUrl?: string,
    isMember: boolean,
    isEligible: boolean,
}


export interface IRule {
    id: number,
    category: string,
    title: string,
    blockchainAddress: string,
    promoteUrl: string,
    expected: number,
    photoUrl: string,
    isEnabled: boolean,
}

export interface IWhitelistRule {
    id: number,
    chatId: number,
    name: string,
    description: string | null,
    users: number[],
    isEnabled: boolean,
    createdAt: string,
    updatedAt: string,
}

export interface IExternalWhitelistRule extends IWhitelistRule {
    url: string,
}


export interface IRuleEligibility extends IRule {
    actual?: number,
    isEligible: boolean,
}

export interface IChatConfiguration {
    chat: IChat,
    rules: IRuleEligibility[],
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

export interface IJetton {
    address: string,
    name: string,
    description?: string,
    symbol: string,
    logoPath?: string,
    isEnabled: boolean,
}

export interface IJettonWithTitle extends IJetton {
    title: string,
    subtitle?: string
}

export interface INftCollection {
    address: string,
    name: string,
    description?: string,
    logoPath?: string,
    isEnabled: boolean,
}

export interface INftCollectionWithTitle extends INftCollection {
    title: string,
    subtitle?: string
}
