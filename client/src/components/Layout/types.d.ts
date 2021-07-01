import { ReactNode } from 'react';

export type LayoutProps = {
  children: ReactNode;
  columns?: { xs: number };
  offset?: { xs: number };
};
