import { status } from './statuses';

export type NodeProps = {
  id: string;
  name: string;
  init_params: { network: string };
  status: status.starting | status.pending | status.running | status.stopped;
  url: string;
  auth: { user: string; password: string };
  created_at: string;
  stopped_at?: string;
};
