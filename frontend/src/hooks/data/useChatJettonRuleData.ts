import {useClientOnce} from "@/hooks/useClientOnce";
import {createJettonRule, fetchJettonRule, toggleJettonRule, updateJettonRule} from "@/services";
import {useState} from "react";
import {IRule} from "@/interfaces";


const useChatJettonRuleData = ({slug, jettonAddress}: {slug: string, jettonAddress?: string}) => {
  const [chatJettonRuleData, setChatJettonRuleData] = useState<IRule | null>(null);
  const [ isLoading, setIsLoading ] = useState(false);

  useClientOnce(() => {
    if (!jettonAddress) return;
    setIsLoading(true);
    fetchJettonRule(slug, jettonAddress).then(
        (data) => { setChatJettonRuleData(data) }
    ).finally(() => { setIsLoading(false) });
  });

  const createChatJettonRule = async (expected: number, blockchainAddress: string) => {
    setIsLoading(true);
    createJettonRule(slug, blockchainAddress, expected).then(
        (data) => { setChatJettonRuleData(data) }
    ).finally(() => { setIsLoading(false) });
  }

  const updateChatJettonRule = async (expected: number, blockchainAddress: string) => {
    setIsLoading(true);
    updateJettonRule(slug, blockchainAddress, expected).then(
        (data) => { setChatJettonRuleData(data) }
    ).finally(() => setIsLoading(false));
  }

  const toggleChatJettonRule = async (isEnabled: boolean, blockchainAddress: string) => {
    setIsLoading(true);
    toggleJettonRule(slug, blockchainAddress, isEnabled).then(
        (data) => { setChatJettonRuleData(data) }
    ).finally(() => setIsLoading(false));
  }

  return {chatJettonRuleData, createChatJettonRule, updateChatJettonRule, toggleChatJettonRule, isLoading};
};

export default useChatJettonRuleData;
