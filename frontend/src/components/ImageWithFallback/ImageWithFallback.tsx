import {FC, PropsWithChildren, useState} from "react";
import Image from "next/image";

const ImageWithFallback: FC<PropsWithChildren<{
    src: string, fallbackSrc: string, width: number, height: number, rounded?: boolean,
}>> = ({src, fallbackSrc, width, height, rounded = false, ...props}) => {
    const [imgSrc, setImgSrc] = useState(src);
    const onError = () => {
        setImgSrc(fallbackSrc);
    };

    let styleProps = {
        borderRadius: "8px",
        backgroundColor: "var(--tg-theme-header-bg-color)",
        width,
        height
    };
    if (rounded) {
        styleProps["borderRadius"] = "50%";
    }

    return (
        <div style={styleProps}>
            <Image style={styleProps} width={width} height={height} src={imgSrc} alt={""} onError={onError} {...props} />
        </div>
    )
}

export default ImageWithFallback;
