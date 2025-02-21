import {useState} from 'react';
import apiClient, {authenticateUser} from "@/utils/apiClient";
import {useClientOnce} from "@/hooks/useClientOnce";
import {IUser} from "@/interfaces";


const useAuthAndFetchUser = () => {
    const [user, setUser] = useState<IUser | undefined>(undefined);
    const [isUserDataLoading, setIsUserDataLoading] = useState(false);

    useClientOnce(() => {
        const fetchUser = async () => {
            try {
                await authenticateUser();
                const response = await apiClient.get("/users/me");
                return response.data
            } catch (error) {
                console.error("Failed to fetch user", error);
            }
        };

        if (user) {
            return;
        }

        console.log("Fetching user", user);

        fetchUser().then(data => setUser(data));
    });

    return {user, setUser, isUserDataLoading, setIsUserDataLoading};
}

export default useAuthAndFetchUser;
