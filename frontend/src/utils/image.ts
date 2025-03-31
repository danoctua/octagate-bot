export const getImageUrl = (imagePath: string) => {
    if (!imagePath || imagePath.startsWith("http")) {
        return imagePath;
    }

    return `${process.env.NEXT_PUBLIC_CDN_URL}/${imagePath}`;
}