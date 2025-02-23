// Get the value of a cookie by name
export const getCookie = (name: string) => {
  const nameEQ = `${name}=`;
  const cookiesArray = document.cookie.split(';');
  for (let cookie of cookiesArray) {
    cookie = cookie.trim();
    if (cookie.startsWith(nameEQ)) {
      return cookie.substring(nameEQ.length);
    }
  }
  return null;
};


export const setCookie = (name: string, value: string, seconds: number) => {
  const date = new Date();
  date.setTime(date.getTime() + seconds * 1000);
  const expires = `expires=${date.toUTCString()}`;
  document.cookie = `${name}=${value}; ${expires}; path=/`;
};
