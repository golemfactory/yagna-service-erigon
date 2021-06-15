import styled, { css } from 'styled-components';
import color from 'styles/colors';

export const StyledButton = styled.button<{ outlined?: boolean }>`
  width: 29.5rem;
  height: 5rem;

  color: ${color.white};
  font-family: 'Inter Regular', sans-serif;
  font-size: 1.1rem;
  line-height: 1.4rem;
  text-transform: uppercase;
  letter-spacing: 0.4rem;

  background-color: ${color.petrol};
  border: 0.1rem solid ${color.petrol};

  margin: 0;

  ${({ outlined }) =>
    outlined &&
    css`
      color: ${color.petrol};

      background-color: ${color.white};
    `}
`;
