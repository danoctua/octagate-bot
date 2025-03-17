import {useState} from 'react';
import {authenticateUser} from "@/utils/apiClient";
import {useClientOnce} from "@/hooks/useClientOnce";
import {IUser} from "@/interfaces";
import {fetchUser} from "@/services";


const useAuthAndFetchUser = () => {
    const [user, setUser] = useState<IUser | undefined>(undefined);
    const [isUserDataLoading, setIsUserDataLoading] = useState(false);

    const getUserDetails = async () => {
        setIsUserDataLoading(true);
        await authenticateUser();
        return await fetchUser().then(
            data => {
                setUser(data)
                return data;
            }
        ).finally(() => setIsUserDataLoading(false));
    }

    useClientOnce(async () => {
        if (user) {
            return;
        }

        await getUserDetails();
    });

    return {user, setUser, isUserDataLoading, setIsUserDataLoading};
}

export default useAuthAndFetchUser;
