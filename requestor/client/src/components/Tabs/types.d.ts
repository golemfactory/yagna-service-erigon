import { ReactNode } from 'react';

export type TabsProps = {
  children: ReactNode;
  count: {
    active: number;
    stopped: number;
  };
};

export type TabProps = {
  id: number;
  name: string;
};
