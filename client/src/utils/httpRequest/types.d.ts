export type Url = {
  path: string;
  id?: string;
};

export type HttpRequest = {
  method?: string;
  account: string | null | undefined;
  data?: object;
} & Url;
