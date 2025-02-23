import {useState} from "react";
import {IJetton} from "@/interfaces";
import {fetchJettons} from "@/services";
import {useClientOnce} from "@/hooks/useClientOnce";


const useJettonsData = () => {
  const [jettons, setJettons] = useState<IJetton[]>([]);

  useClientOnce(() => {
    fetchJettons().then((data) => { setJettons(data) });
  });

  return jettons;
}

export default useJettonsData;
