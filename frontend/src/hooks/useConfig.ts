import {useEffect, useState} from "react";

export default function useConfig() {
  const [config, setConfig] = useState<{
      botUrl: string,
      sentryDns: string,
  } | null>(null);

  useEffect(() => {
    fetch("/settings.json")
      .then((res) => res.json())
      .then((data) => setConfig(data));
  }, []);

  return config;
}
