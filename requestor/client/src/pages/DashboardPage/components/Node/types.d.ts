import { statuses } from './statuses';

export type NodeProps = {
  id: string;
  name: string;
  init_params: { network: string };
  status: typeof statuses;
  url: string;
  auth: { user: string; password: string };
  created_at: string;
  stopped_at?: string;
};
