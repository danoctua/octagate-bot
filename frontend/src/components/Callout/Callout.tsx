import {FC, PropsWithChildren, ReactElement} from "react";

const Callout: FC<PropsWithChildren<{
    type: 'info' | 'success' | 'warning' | 'error';
    before?: ReactElement;
    after?: ReactElement;
}>> = (
    {
        type,
        before,
        after,
        children
    }) => {
    let bgColor = "var(--tgui--card_bg_color)";
    let textColor = "var(--tgui--text_color)";

    if (type === "error") {
        bgColor = "var(--tgui--destructive_background)";
        textColor = "var(--tgui--destructive_text_color)";
    }

    return (
        <div
            style={
                {
                    color: textColor,
                    backgroundColor: bgColor,
                    textAlign: "start",
                    display: "flex",
                    flexWrap: "nowrap",
                    alignItems: "center",
                    gap: "12px",
                    padding: "8px 16px",
                    borderRadius: "14px",
                }
            }
        >
            {before && <div>{before}</div>}
            <div style={{flex: 1}}>
                {children}
            </div>
            {after && <div>{after}</div>}
        </div>
    )
}

export default Callout;
