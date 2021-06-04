export type Url = {
  path: string;
  id?: string;
};

export type HttpRequest = {
  method?: string;
  data: object;
} & Url;
