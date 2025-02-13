import { useState } from 'react';
import apiClient, { authenticateUser } from "@/utils/apiClient";
import {useClientOnce} from "@/hooks/useClientOnce";

export interface IUser {
  id: number;
  firstName: string;
  lastName: string;
  username: string;
  photoUrl: string;
  walletAddress: string;
}

export function useAuthAndFetchUser(): [IUser | undefined, (user: IUser | undefined) => void] {
  const [user, setUser] = useState<IUser | undefined>(undefined);

  useClientOnce(() => {
    const fetchUser = async () => {
      try {
        await authenticateUser();
        const response = await apiClient.get("/users/me");
        setUser(response.data);
      } catch (error) {
        console.error("Failed to fetch user", error);
      }
    };

    fetchUser().then();
  });

  return [user, setUser];
}