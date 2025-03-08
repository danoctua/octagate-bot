import axios, {AxiosError} from "axios";
import { EventEmitter } from "events";

import { retrieveLaunchParams } from "@telegram-apps/sdk-react";

export const errorEmitter = new EventEmitter();


const apiClient = axios.create({
  baseURL: "/api",
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
    } else {
      handleApiError(error);
    }
    return Promise.reject(error);
  }
);

const handleApiError = (error: AxiosError) => {
  errorEmitter.emit("apiError", error);
  switch (error.response?.status) {
    case 400:
      console.error("Bad Request", error.response.data);
      break;
    case 403:
      console.error("Forbidden", error.response.data);
      break;
    case 404:
      console.error("Not Found", error.response.data);
      break;
    case 500:
      console.error("Internal Server Error", error.response.data);
      break;
    default:
      console.error("An unexpected error occurred", error.response?.data);
  }
};

export default apiClient;
