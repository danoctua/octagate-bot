import {useState} from "react";
import {useClientOnce} from "@/hooks/useClientOnce";

export default function useConfig() {
  const [config, setConfig] = useState<{
      botUrl: string,
      sentryDns: string,
  } | null>(null);

  useClientOnce(() => {
    fetch("/settings.json")
      .then((res) => res.json())
      .then((data) => setConfig(data));
  });

  return config;
}
