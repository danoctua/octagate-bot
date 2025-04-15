import {useClientOnce} from "@/hooks/useClientOnce";
import {
  createNftCollectionRule,
  fetchNftCollectionRule,
  updateNftCollectionRule
} from "@/services";
import {useState} from "react";
import {INftCollectionRule, INftMetadata} from "@/interfaces";


const useChatNftCollectionRuleData = ({slug, ruleId}: {slug: string, ruleId?: number}) => {
  const [chatNftCollectionRuleData, setChatNftCollectionRuleData] = useState<INftCollectionRule | null>(null);
  const [ isLoading, setIsLoading ] = useState(false);

  useClientOnce(() => {
    if (!ruleId) return;
    setIsLoading(true);
    fetchNftCollectionRule(slug, ruleId).then(
        (data) => { setChatNftCollectionRuleData(data) }
    ).finally(() => { setIsLoading(false) });
  });

  const createChatNftCollectionRule = async (
      {expected, address, requiredAttributes}: {expected: number, address: string, requiredAttributes: INftMetadata[]}
  ) => {
    if (!slug || ruleId) return;
    setIsLoading(true);
    createNftCollectionRule(slug, address, expected, requiredAttributes).then(
        (data) => { setChatNftCollectionRuleData(data) }
    ).catch((e) => { setIsLoading(false); throw e;});
  }

  const updateChatNftCollectionRule = async (
      {expected, address, isEnabled, requiredAttributes}: {expected: number, address: string, isEnabled: boolean, requiredAttributes: INftMetadata[]}
  ) => {
    if (!ruleId) return;
    setIsLoading(true);
    updateNftCollectionRule(slug, ruleId, {address, expected, isEnabled, requiredAttributes}).then(
        (data) => { setChatNftCollectionRuleData(data) }
    ).catch((e) => { setIsLoading(false); throw e;});
  }

  return {chatNftCollectionRuleData, createChatNftCollectionRule, updateChatNftCollectionRule, isLoading};
};

export default useChatNftCollectionRuleData;
