export const getImageUrl = (imagePath: string | undefined): string => {
    if (!imagePath || imagePath.startsWith("http")) {
        return "";
    }

    return `${process.env.NEXT_PUBLIC_CDN_URL}/${imagePath}`;
}