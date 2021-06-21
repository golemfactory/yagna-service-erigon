export type ButtonProps = {
  type?: 'button' | 'submit';
  label: string;
  onClick?: () => void;
  outlined?: boolean;
  ghost?: boolean;
};
