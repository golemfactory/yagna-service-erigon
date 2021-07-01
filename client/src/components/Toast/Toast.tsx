import { ToastProps } from './types';
import { error } from './utils';

const Toast = ({ code, message }: ToastProps) => <>{message ? message : error(code)}</>;

export default Toast;
