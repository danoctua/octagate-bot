import {useClientOnce} from "@/hooks/useClientOnce";
import {
  createNftCollectionRule,
  fetchNftCollectionRule,
  toggleNftCollectionRule,
  updateNftCollectionRule
} from "@/services";
import {useState} from "react";
import {IRule} from "@/interfaces";


const useChatNftCollectionRuleData = ({slug, collectionAddress}: {slug: string, collectionAddress?: string}) => {
  const [chatNftCollectionRuleData, setChatNftCollectionRuleData] = useState<IRule | null>(null);
  const [ isLoading, setIsLoading ] = useState(false);

  useClientOnce(() => {
    if (!collectionAddress) return;
    setIsLoading(true);
    fetchNftCollectionRule(slug, collectionAddress).then(
        (data) => { setChatNftCollectionRuleData(data) }
    ).finally(() => { setIsLoading(false) });
  });

  const createChatNftCollectionRule = async (expected: number, blockchainAddress: string) => {
    setIsLoading(true);
    createNftCollectionRule(slug, blockchainAddress, expected).then(
        (data) => { setChatNftCollectionRuleData(data) }
    ).finally(() => { setIsLoading(false) });
  }

  const updateChatNftCollectionRule = async (expected: number, blockchainAddress: string, isEnabled: boolean) => {
    setIsLoading(true);
    updateNftCollectionRule(slug, blockchainAddress, expected, isEnabled).then(
        (data) => { setChatNftCollectionRuleData(data) }
    ).finally(() => setIsLoading(false));
  }

  const toggleChatNftCollectionRule = async (isEnabled: boolean, blockchainAddress: string) => {
    setIsLoading(true);
    toggleNftCollectionRule(slug, blockchainAddress, isEnabled).then(
        (data) => { setChatNftCollectionRuleData(data) }
    ).finally(() => setIsLoading(false));
  }

  return {chatNftCollectionRuleData, createChatNftCollectionRule, updateChatNftCollectionRule, toggleChatNftCollectionRule, isLoading};
};

export default useChatNftCollectionRuleData;
