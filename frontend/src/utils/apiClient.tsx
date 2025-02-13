import axios from "axios";

import { retrieveLaunchParams } from "@telegram-apps/sdk-react";


const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "https://localhost",
  headers: {
    "Content-Type": "application/json",
  },
});


export const authenticateUser = async () => {
  const { initDataRaw } = retrieveLaunchParams();

  try {
    const response = await apiClient.post("/auth/telegram", { initDataRaw });
    const accessToken = response.data.access_token;
    localStorage.setItem("accessToken", accessToken);
    return accessToken;
  } catch (error) {
    console.error("Failed to refresh token", error);
    return null;
  }
}

// Attach token to every request
apiClient.interceptors.request.use(async (config) => {
  let accessToken = localStorage.getItem("accessToken");
  if (accessToken) {
    config.headers["Authorization"] = `Bearer ${accessToken}`;
  }
  return config;
});

// Handle token expiration
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response && error.response.status === 401) {
      console.log("Token expired. Re-authenticating...");
      try {
        await authenticateUser();
        error.config.headers["Authorization"] = `Bearer ${localStorage.getItem("accessToken")}`;
        return apiClient(error.config);
      } catch (refreshError) {
        console.error("Re-authentication failed", refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
