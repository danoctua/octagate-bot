import {useState} from "react";
import {IJetton} from "@/interfaces";
import {createJetton, fetchJetton, updateJetton} from "@/services";
import {useClientOnce} from "@/hooks/useClientOnce";


const useJettonData = ( address?: string ) => {
  const [jetton, setJetton] = useState<IJetton | undefined>(undefined);
  const [ isLoading, setIsLoading ] = useState(false);

  useClientOnce(() => {
    if (!address) return;
    setIsLoading(true);
    fetchJetton(address).then(
        (data) => { setJetton(data) }
    ).finally(() => setIsLoading(false));
  });

  const addJetton = async (address: string): Promise<IJetton> => {
    setIsLoading(true);
    return await createJetton(address).then(
        (data) => {
          setJetton(data)
          setIsLoading(false)
          return data
        }
    ).finally(() => setIsLoading(false));
  }

  const toggleJetton = async (address: string, isEnabled: boolean): Promise<IJetton> => {
    setIsLoading(true);
    return await updateJetton(address, isEnabled).then(
        (data) => {
          setJetton(data)
          return data
        }
    ).finally(() => setIsLoading(false));
  }

  return { jetton, isLoading, addJetton, toggleJetton };
}

export default useJettonData;
