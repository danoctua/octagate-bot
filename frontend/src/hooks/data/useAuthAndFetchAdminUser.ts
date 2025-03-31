import {useEffect, useState} from 'react';
import {authenticateAdminUser} from "@/utils/apiClient";
import {useClientOnce} from "@/hooks/useClientOnce";


const useAuthAdmin = () => {
    const [isAdminUserAuthenticated, setIsAdminUserAuthenticated] = useState(false);
    const [ error, setError] = useState<Error | null>(null);

    const authenticate = async () => {
        await authenticateAdminUser();
    }

    useClientOnce(async () => {
        await authenticate().then(() => setIsAdminUserAuthenticated(true)).catch((error) => {
            setError(error);
        })
    });

    useEffect(() => {
        if (error) {
            console.error("Error authenticating admin user:", error);
            throw error;
        }
    }, [error]);

    return {isAdminUserAuthenticated}
}

export default useAuthAdmin;
