'use client';

import {useCallback, useEffect, useState} from "react";
import {AxiosError} from "axios";
import {errorEmitter} from "@/utils/apiClient";

interface ErrorResponseData {
    detail?: {
        error?: {
            message?: string;
        };
    } | string;
}


interface FlashMessage {
    id: string;  // random uuid
    type: "error" | "info" | "success";
    title: string;
    message: string;
}


export const generateMessageId = (): string => {
    return Math.random().toString(36).substring(2);
}


const useFlashMessages = () => {
    const [messages, setMessages] = useState<FlashMessage[]>([]);

    const addMessage = useCallback((message: FlashMessage) => {
        setMessages([...messages, message]);
    }, [messages])

    const removeMessage = useCallback((id: string) => {
        setMessages(messages.filter((message) => message.id !== id));
    }, [messages])

    const pushMessage = useCallback((title: string, message: string, type: "error" | "info" | "success") => {
        addMessage(
            {
                id: generateMessageId(),
                title,
                message,
                type,
            }
        );
    }, [addMessage])

    const onMessageClose = useCallback((messageId: string) => {
        removeMessage(messageId);
    }, [removeMessage])

    useEffect(() => {
        const extractErrorMessage = (error: AxiosError): string => {
            if (!error.response || !error.response.data) {
                return 'Something went wrong';
            }

            const _error = error.response.data as ErrorResponseData;

            if (typeof _error.detail === "object" && _error.detail?.error?.message) {
                return _error.detail.error.message;
            } else if (
                typeof _error.detail === 'string'
            ) {
                return _error.detail;
            }
            return "Something went wrong"
        }

        const handleError = (error: AxiosError) => {
            if (!error.response) return;
            console.error('API error', error.response.status, error.response.data);
            const errorMessage = extractErrorMessage(error);
            addMessage({
                id: generateMessageId(),
                type: "error",
                title: "Oops!",
                message: errorMessage,
            });
        };

        errorEmitter.on("apiError", handleError);

        return () => {
            errorEmitter.off("apiError", handleError);
        };
    }, [addMessage]);

    return {
        messages,
        pushMessage,
        onMessageClose,
    }
}

export default useFlashMessages;