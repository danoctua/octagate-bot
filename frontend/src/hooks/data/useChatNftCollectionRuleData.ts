import {useClientOnce} from "@/hooks/useClientOnce";
import {
  createNftCollectionRule,
  fetchNftCollectionRule,
  updateNftCollectionRule
} from "@/services";
import {useState} from "react";
import {IRule} from "@/interfaces";


const useChatNftCollectionRuleData = ({slug, ruleId}: {slug: string, ruleId?: number}) => {
  const [chatNftCollectionRuleData, setChatNftCollectionRuleData] = useState<IRule | null>(null);
  const [ isLoading, setIsLoading ] = useState(false);

  useClientOnce(() => {
    if (!ruleId) return;
    setIsLoading(true);
    fetchNftCollectionRule(slug, ruleId).then(
        (data) => { setChatNftCollectionRuleData(data) }
    ).finally(() => { setIsLoading(false) });
  });

  const createChatNftCollectionRule = async ({expected, address}: {expected: number, address: string}) => {
    if (!slug || ruleId) return;
    setIsLoading(true);
    createNftCollectionRule(slug, address, expected).then(
        (data) => { setChatNftCollectionRuleData(data) }
    ).catch((e) => { setIsLoading(false); throw e;});
  }

  const updateChatNftCollectionRule = async ({expected, address, isEnabled}: {expected: number, address: string, isEnabled: boolean}) => {
    if (!ruleId) return;
    setIsLoading(true);
    updateNftCollectionRule(slug, ruleId, {address, expected, isEnabled}).then(
        (data) => { setChatNftCollectionRuleData(data) }
    ).catch((e) => { setIsLoading(false); throw e;});
  }

  return {chatNftCollectionRuleData, createChatNftCollectionRule, updateChatNftCollectionRule, isLoading};
};

export default useChatNftCollectionRuleData;
