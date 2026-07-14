export const SESSION_KEY = "juniper.session";
export const SHARE_KEY = "juniper.share";
export const ACCOUNT_KEY = "juniper.account";

export const getSession = () => localStorage.getItem(SESSION_KEY);
export const setSession = (v: string) => localStorage.setItem(SESSION_KEY, v);
export const getShare = () => localStorage.getItem(SHARE_KEY);
export const setShare = (v: string) => localStorage.setItem(SHARE_KEY, v);
export const getAccount = () => localStorage.getItem(ACCOUNT_KEY);
export const setAccount = (v: string) => localStorage.setItem(ACCOUNT_KEY, v);
