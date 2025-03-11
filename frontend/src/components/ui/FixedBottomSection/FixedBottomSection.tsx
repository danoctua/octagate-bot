import React, {FC, PropsWithChildren} from "react";
import {Button, Divider, FixedLayout} from "@telegram-apps/telegram-ui";


export interface ButtonStateProps {
    disabled?: boolean;
    loading?: boolean;
    text: string;
    onClick?: () => void;
    mode?: 'filled' | 'bezeled' | 'plain' | 'gray' | 'outline' | 'white';
    size?: 's' | 'm' | 'l';
}


const FixedBottomSection: FC<PropsWithChildren<ButtonStateProps>> = (
    {
        text,
        mode = 'filled',
        onClick,
        loading = false,
        disabled = false,
        size = "m",
        children
    }
) => {
    return (
        <FixedLayout value={"bottom"} style={{ background: "var(--tg-theme-secondary-bg-color)" }}>
            <Divider/>
            {children}
            <div
                style={{
                    padding: "8px 16px"
                }}
            >
                <Button
                    mode={mode}
                    loading={loading}
                    disabled={disabled}
                    size={size}
                    stretched
                    onClick={onClick}
                >
                    {text}
                </Button>
            </div>
        </FixedLayout>
    )
}

export default FixedBottomSection;
