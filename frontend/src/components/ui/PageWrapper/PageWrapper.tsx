"use client";

import {motion, AnimatePresence} from "framer-motion";
import {usePathname} from "next/navigation";
import {ReactNode} from "react";

export default function PageWrapper({children}: { children: ReactNode }) {
    const pathname = usePathname();

    return (
        // For the home page, we don't want to animate
        pathname === '/' ?
            <>{children}</> :
            <AnimatePresence mode="popLayout">
                <motion.div
                    key={pathname} // Animates on page change
                    initial={{opacity: 0, x: 10}}
                    animate={{opacity: 1, x: 0}}
                    exit={{opacity: 0, x: -10}}
                    transition={{duration: 0.3}}
                >
                    {children}
                </motion.div>
            </AnimatePresence>
    );
}
