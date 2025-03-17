import React, {FC, PropsWithChildren} from "react";


const Header: FC<PropsWithChildren<{}>> = ({children}) => {
    return (
        <div className={"flex items-center justify-center flex-col py-4 gap-3 text-center"}>
            {children}
        </div>
    )
}

export default Header;
