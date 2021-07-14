import { ButtonProps } from './types';
import { StyledButton } from './styles';

const Button = ({ type = 'button', label, ...props }: ButtonProps) => (
  <StyledButton type={type} {...props}>
    {label}
  </StyledButton>
);

export default Button;
