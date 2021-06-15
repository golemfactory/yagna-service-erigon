import { ReactNode } from 'react';
import { toast } from 'react-toastify';

export const error = (code?: number) => {
  switch (code) {
    case 1:
      return 'Do you have multiple wallets installed?';
    case -32002:
      return 'Proceed with MetaMask login!';
    default:
      return 'Something went wrong!';
  }
};

const notify = (content: ReactNode, id?: string) =>
  id === 'success' ? toast.success(content) : toast.error(content, { toastId: id });

export default notify;
