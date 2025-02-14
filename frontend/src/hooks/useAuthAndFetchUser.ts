import { useState } from 'react';
import apiClient, { authenticateUser } from "@/utils/apiClient";
import {useClientOnce} from "@/hooks/useClientOnce";

export interface IUser {
  id: number;
  firstName: string;
  lastName: string;
  username: string;
  photoUrl: string;
  walletAddress: string | null;
}

export const useAuthAndFetchUser = (): [IUser | undefined, (user: IUser | undefined) => void] => {
  const [user, setUser] = useState<IUser | undefined>(undefined);

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

    if (user) { return; }

    console.log("Fetching user", user);

    fetchUser().then(data => setUser(data));
  });

  return [user, setUser];
}
