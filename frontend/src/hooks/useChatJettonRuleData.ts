import {useClientOnce} from "@/hooks/useClientOnce";
import {fetchJettonRule} from "@/services";
import {useState} from "react";
import {IRule} from "@/interfaces";


const useChatJettonRuleData = ({slug, jettonAddress}: {slug: string, jettonAddress: string}) => {
  const [chatJettonRuleData, setChatJettonRuleData] = useState<IRule | null>(null);

  useClientOnce(() => {
    fetchJettonRule(slug, jettonAddress).then((data) => { setChatJettonRuleData(data) });
  });

  return chatJettonRuleData;
};

export default useChatJettonRuleData;
