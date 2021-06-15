import { ButtonProps } from './types';
import { StyledButton } from './styles';

const Button = ({ type = 'button', label, onClick, outlined, ...props }: ButtonProps) => (
  <StyledButton type={type} onClick={onClick} outlined={outlined} {...props}>
    {label}
  </StyledButton>
);

export default Button;
