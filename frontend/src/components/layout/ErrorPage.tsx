import React, {useEffect, useMemo} from 'react';
import BannerPage from "@/components/layout/BannerPage/BannerPage";

export const ErrorPage = ({
  error,
  reset,
}: {
  error: Error & { digest?: string, status?: number, message?: string }
  reset?: () => void
}) => {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  return useMemo(() => {
      if (error.status) {
          if (error.status === 403) {
              return (
                  <BannerPage
                      logoUrl={"/telegram.gif"}
                      title={"Forbidden"}
                      subtitle={"You don't have access to the requested page"}
                  />
              )
          }
      }
      return (
          <BannerPage logoUrl={"/welcome.gif"} title={"Unhandled error"} subtitle={error.message}/>
      )
  }, [error])
}