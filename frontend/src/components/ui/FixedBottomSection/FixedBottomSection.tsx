'use client';


import React, {FC, PropsWithChildren, ReactNode, useRef, useEffect} from "react";
import {Button, Divider, FixedLayout, RootRenderer} from "@telegram-apps/telegram-ui";
import {AlertTriangle, CheckCircle, Info} from "lucide-react";
import useFlashMessages from "@/hooks/useFlashMessages";
import {Snackbar} from "@/components/ui/Snackbar/Snackbar";


export interface ButtonStateProps {
    disabled?: boolean;
    loading?: boolean;
    text: string;
    onClick?: () => void;
    mode?: 'filled' | 'bezeled' | 'plain' | 'gray' | 'outline' | 'white';
    size?: 's' | 'm' | 'l';
}


export const FixedBottomButton: FC<PropsWithChildren<ButtonStateProps>> = (
    {
        text,
        mode = 'filled',
        onClick,
        loading = false,
        disabled = false,
        size = "m",
    }
) => {
    return (
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
    )
}

const FixedBottomSection: FC<PropsWithChildren<{
    button?: ReactNode
}>> = (
    {
        button,
        children
    }
) => {

    const {onMessageClose, messages} = useFlashMessages()
    const fixedLayoutRef = useRef<HTMLDivElement>(null);
    const [fixedLayoutHeight, setFixedLayoutHeight] = React.useState<number>(0);

    useEffect(() => {
        if (fixedLayoutRef.current) {
            setFixedLayoutHeight(fixedLayoutRef.current.offsetHeight);
        }
    }, [button, children]);


    const getSnackbarIcon = (type: "error" | "success" | "info" | undefined) => {
        switch (type) {
            case 'error':
                return <AlertTriangle/>
            case 'success':
                return <CheckCircle/>
            case 'info':
                return <Info/>
            default:
                return undefined
        }
    }

    return (
        <>
            <div
                id={"custom-tweak-to-add-bottom-padding"}
                style={{height: `${fixedLayoutHeight + 10}px`}}
            ></div>
            <FixedLayout
                className={(children || button) ? "pb-1.5" : ""}
                value={"bottom"}
            >
                <div ref={fixedLayoutRef}>
                    {messages.length > 0 &&
                        messages.map((message) => (
                            <Snackbar
                                key={message.id}
                                onClose={() => onMessageClose(message.id)}
                                duration={200000}
                                before={getSnackbarIcon(message.type)}
                            >
                                {message.message}
                            </Snackbar>
                        ))
                    }
                    <div
                        style={{background: "var(--tg-theme-secondary-bg-color)"}}
                    >
                        <Divider/>
                        {children}
                        {button &&
                            <div className={"px-4 py-2"}>
                                {button}
                            </div>
                        }
                    </div>
                </div>
            </FixedLayout>
        </>
    )
}

export default FixedBottomSection;
