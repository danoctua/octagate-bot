import React, {FC, PropsWithChildren} from "react";


const Header: FC<PropsWithChildren<{}>> = ({children}) => {
    return (
        <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            padding: "40px 16px",
            paddingTop: 48,
            gap: 12,
            textAlign: "center"
        }}>
            {children}
        </div>
    )
}

export default Header;
