import {useState} from "react";
import {IJetton} from "@/interfaces";
import {fetchAllJettons, fetchWhitelistedJettons} from "@/services";
import {useClientOnce} from "@/hooks/useClientOnce";


const useJettonsData = ({whitelistedOnly = true}: {whitelistedOnly: boolean}) => {
  const [jettons, setJettons] = useState<IJetton[] | undefined>(undefined);
  const [ isLoading, setIsLoading ] = useState(true);

  useClientOnce(() => {
    if (whitelistedOnly) {
      fetchWhitelistedJettons().then((data) => { setIsLoading(false); setJettons(data) });
    } else {
      fetchAllJettons().then((data) => {
        setIsLoading(false);
        setJettons(data)
      });
    }
  });

  return { jettons, isLoading };
}

export default useJettonsData;
